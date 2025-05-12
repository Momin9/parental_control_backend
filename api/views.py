from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from rest_framework import viewsets, permissions
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from api.models import BlockedURL
from api.serializers import BlockedURLSerializer, UserSerializer, ChildCreateSerializer
from .forms import ParentSignupForm, ChildCreateForm
from .models import Child

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Add user data to the token response
        user = self.user
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_parent': user.is_parent,
        }

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class IsParentUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_parent or request.user.is_child)


class ChildCreateViewSet(viewsets.ModelViewSet):
    queryset = Child.objects.all()
    serializer_class = ChildCreateSerializer
    permission_classes = [IsAuthenticated, IsParentUser]

    def get_queryset(self):
        return Child.objects.filter(parent=self.request.user)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'])
    def update_location(self, request, pk=None):
        child = self.get_object()
        if not child or request.data.get('location') is None:
            return Response({'message': 'Location is required', 'status': 400, 'error': True}, status=400)
        child.last_location = request.data.get('location', {})
        child.save()
        return Response({'status': 'Location updated'})


def parent_signup(request):
    if request.method == "POST":
        form = ParentSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_parent = True  # Ensure only parents can sign up
            user.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = ParentSignupForm()
    return render(request, "signup.html", {"form": form})


User = get_user_model()


@login_required(login_url="/login/")
def create_child(request):
    if not hasattr(request.user, "is_parent") or not request.user.is_parent:
        messages.error(request, "Only parents can create child accounts.")
        return redirect("dashboard")

    if request.method == "POST":
        form = ChildCreateForm(request.POST)
        if form.is_valid():
            child_user = form.save(commit=False)
            child_user.is_child = True  # Assuming you have an `is_child` field in User model
            child_user.save()

            # Extract age from form.cleaned_data
            age = form.cleaned_data.get("age", 0)
            Child.objects.create(user=child_user, parent=request.user, age=age)

            messages.success(request, "Child account created successfully!")
            return redirect("dashboard")
    else:
        form = ChildCreateForm()

    return render(request, "create_child.html", {"form": form})


class IsParent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_parent


# ViewSets


class BlockedURLViewSet(viewsets.ModelViewSet):
    queryset = BlockedURL.objects.all()
    serializer_class = BlockedURLSerializer
    permission_classes = [IsParent, IsAuthenticated]

    def get_queryset(self):
        # Get parent (the authenticated user)
        parent = self.request.user

        # Get child_id from query parameters, if provided
        child_id = self.request.query_params.get('child_id', None)

        # Start with a queryset filtered by the parent
        queryset = BlockedURL.objects.filter(parent=parent)

        if child_id:
            # If a child_id is provided, further filter by child
            queryset = queryset.filter(child_id=child_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(parent=self.request.user)


# Authentication Views
class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password are required"}, status=400)

        user = authenticate(username=username, password=password)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=400)

        # ✅ Manually log in the user for session authentication
        login(request, user)
        serialized_user = UserSerializer(user)
        token, created = Token.objects.get_or_create(user=user)
        print(user)
        return Response({"token": token.key, "user_data": serialized_user.data})


def login_page(request):
    return render(request, "login.html")


@login_required(login_url="/login/")
def dashboard(request):
    return render(request, "dashboard.html")


def logout_view(request):
    logout(request)
    return redirect("/login/")
