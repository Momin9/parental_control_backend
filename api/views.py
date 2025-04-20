from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.models import BlockedURL
from api.serializers import ChildSerializer, BlockedURLSerializer, UserSerializer
from .forms import ParentSignupForm, ChildCreateForm
from .models import Child


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
class ChildViewSet(viewsets.ModelViewSet):
    queryset = Child.objects.all()
    serializer_class = ChildSerializer
    permission_classes = [IsParent]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return Child.objects.filter(parent=self.request.user)
    @action(detail=True, methods=['post'])
    def update_location(self, request, pk=None):
        child = self.get_object()
        child.last_location = request.data.get('location', {})
        child.save()
        return Response({'status': 'Location updated'})


class BlockedURLViewSet(viewsets.ModelViewSet):
    queryset = BlockedURL.objects.all()
    serializer_class = BlockedURLSerializer
    permission_classes = [IsParent]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return self.queryset.filter(parent=self.request.user)


# Authentication Views
class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
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

        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})


@csrf_exempt
def request_live_location(request):
    if request.method == "POST":
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "child_tracking", {"type": "request_location"}
        )
        return JsonResponse({"message": "Live location request sent"}, status=200)

    return JsonResponse({"error": "Invalid request"}, status=400)


def login_page(request):
    return render(request, "login.html")


@login_required(login_url="/login/")
def dashboard(request):
    return render(request, "dashboard.html")


def logout_view(request):
    logout(request)
    return redirect("/login/")
