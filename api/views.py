from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework import viewsets, permissions
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from api.serializers import BlockedURLSerializer, UserSerializer, ChildCreateSerializer, CustomTokenObtainPairSerializer
from .forms import ParentSignupForm, ChildCreateForm
from .models import Child, BlockedURL
from .serializers import URLCheckSerializer

User = get_user_model()


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
        child = Child.objects.get(id=pk)
        if not child or request.data.get('location') is None:
            return Response({'message': 'Location is required', 'status': 400, 'error': True}, status=400)
        child.last_location = request.data.get('location', {})
        child.save()
        return Response({'status': 'Location updated'})

    def destroy(self, request, *args, **kwargs):
        # Override the delete method to check if the child belongs to the request user (parent)
        child = self.get_object()  # This will get the child based on the primary key (pk)

        # Check if the request user is the parent of the child
        if child.parent != request.user:
            return Response({'message': 'Not your child. You can only delete your own child.'},
                            status=status.HTTP_403_FORBIDDEN)

        # If the parent is correct, proceed with deletion
        self.perform_destroy(child)
        return Response({'status': 'Child deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


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


class BlockedURLViewSet(viewsets.ModelViewSet):
    queryset = BlockedURL.objects.all()
    serializer_class = BlockedURLSerializer
    permission_classes = [IsParentUser, IsAuthenticated]

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

        if self.request.user.is_child:
            child_id = Child.objects.get(user=self.request.user)
            queryset = BlockedURL.objects.filter(child_id=child_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(parent=self.request.user)

    def update(self, request, *args, **kwargs):
        # Custom handling for PUT (full update)
        try:
            blocked_url = BlockedURL.objects.filter(id=kwargs['pk']).first()  # Corrected here: use `objects.filter`
            if not blocked_url:
                return Response({'detail': 'Blocked URL not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': f'Error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        # You can add custom logic to update based on `id` here
        serializer = self.get_serializer(blocked_url, data=request.data, partial=False)  # Full update (not partial)
        if serializer.is_valid():
            serializer.save()  # Save the updated object
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        # Custom handling for PATCH (partial update)
        try:
            blocked_url = BlockedURL.objects.filter(id=kwargs['pk']).first()  # Corrected here: use `objects.filter`
            if not blocked_url:
                return Response({'detail': 'Blocked URL not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': f'Error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        # You can add custom logic to update based on `id` here
        serializer = self.get_serializer(blocked_url, data=request.data, partial=True)  # Partial update
        if serializer.is_valid():
            serializer.save()  # Save the updated object
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class URLCheckView(APIView):
    def post(self, request):
        # Validate the data
        serializer = URLCheckSerializer(data=request.data)
        if serializer.is_valid():
            url = serializer.validated_data['url']
            child_id = serializer.validated_data['child_id']

            try:
                # Get the child object based on child_id
                child = Child.objects.get(id=child_id)
            except Child.DoesNotExist:
                return Response({'error': 'Child not found'}, status=status.HTTP_404_NOT_FOUND)

            # Check if the URL is blocked for this child
            blocked_url_exists = BlockedURL.objects.filter(child=child, url=url).exists()

            if blocked_url_exists:
                return Response({'result': True}, status=status.HTTP_200_OK)
            else:
                return Response({'result': False}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
