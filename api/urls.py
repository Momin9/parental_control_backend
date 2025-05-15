from django.urls import path, include
from rest_framework import routers

from api.views import UserViewSet, BlockedURLViewSet, ChildCreateViewSet, login_page, dashboard, \
    logout_view, parent_signup, create_child, URLCheckView

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'blocked_urls', BlockedURLViewSet)
router.register(r'children', ChildCreateViewSet, basename='children')

urlpatterns = [
    path('api/', include(router.urls)),
    path("login/", login_page, name="login"),
    path("dashboard/", dashboard, name="dashboard"),
    path("logout/", logout_view, name="logout"),
    path("signup/", parent_signup, name="signup"),
    path("create_child/", create_child, name="create_child"),
    path('check-url/', URLCheckView.as_view(), name='check-url'),
]
