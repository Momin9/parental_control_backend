from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class ParentSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class ChildCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    age = forms.IntegerField(min_value=0, label="Child's Age")

    class Meta:
        model = User
        fields = ["username", "password", "age"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Hash the password
        if commit:
            user.save()
        return user
