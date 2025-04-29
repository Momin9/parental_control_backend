"""
URL configuration for parental_control_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from api.views import CustomTokenObtainPairView


def root_redirect(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")


urlpatterns = [
    path('', root_redirect, name="root_redirect"),  # Redirect root to dashboard/login
    path('admin/', admin.site.urls),
    path('', include('api.urls')),
    path('api/login/', CustomTokenObtainPairView.as_view(), name='custom_login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
from django.http import HttpResponse


def silent_websocket(request):
    return HttpResponse(status=204)  # No content


urlpatterns += [
    path('websocket', silent_websocket),  # No slash to match /websocket exactly
]
