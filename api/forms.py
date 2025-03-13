from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class ParentSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class ChildCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]
