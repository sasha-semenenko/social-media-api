from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, TokenVerifyView,
)

from user.views import CreateUserView, LogoutView, ManageUserView

urlpatterns = [
    # user registration and authentication
    path("register/", CreateUserView.as_view(), name="register-user"),
    path("me/", ManageUserView.as_view(), name="manage"),
    path("token/", TokenObtainPairView.as_view(), name="token-obtain"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    path("logout/", LogoutView.as_view(), name="logout")
]

app_name = "user"
