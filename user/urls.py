from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, TokenVerifyView,
)
from user.views import (
    CreateUserView,
    LogoutView,
    ManageUserView,
    UserProfileView, follow, unfollow
)
from rest_framework import routers

router = routers.DefaultRouter()
router.register("profiles", UserProfileView)


urlpatterns = [
    # user registration and authentication
    path("register/", CreateUserView.as_view(), name="register-user"),
    path("me/", ManageUserView.as_view(), name="manage"),
    path("token/", TokenObtainPairView.as_view(), name="token-obtain"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # user profile
    path("", include(router.urls)),
    path("profiles/<int:pk>/follow/", follow, name="follow"),
    path("profiles/<int:pk>/unfollow/", unfollow, name="unfollow"),
]

app_name = "user"
