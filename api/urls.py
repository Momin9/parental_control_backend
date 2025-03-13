from django.urls import path, include
from rest_framework import routers

from api.views import UserViewSet, ChildViewSet, BlockedURLViewSet, request_live_location, login_page, dashboard, \
    logout_view, parent_signup, create_child

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'children', ChildViewSet)
router.register(r'blocked_urls', BlockedURLViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path("api/request_location/", request_live_location, name="request_location"),
    path("login/", login_page, name="login"),
    path("dashboard/", dashboard, name="dashboard"),
    path("logout/", logout_view, name="logout"),
    path("signup/", parent_signup, name="signup"),
    path("create_child/", create_child, name="create_child"),
]
