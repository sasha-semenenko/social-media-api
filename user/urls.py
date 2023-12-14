from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, TokenVerifyView,
)
from user.views import (
    CreateUserView,
    LogoutView,
    ManageUserView,
    UserProfileView,
    follow,
    unfollow,
    UserProfileCreateView
)

urlpatterns = [
    # user registration and authentication
    path("register/", CreateUserView.as_view(), name="register-user"),
    path("me/", ManageUserView.as_view(), name="manage"),
    path("token/", TokenObtainPairView.as_view(), name="token-obtain"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # user profile
    path("userprofile-create/", UserProfileCreateView.as_view(), name="create-userprofile"),
    path("profiles/", UserProfileView.as_view({'get': 'list'}), name="profile-list"),
    path("profiles/<int:pk>/", UserProfileView.as_view({'get': 'retrieve'}), name="profile-detail"),
    path("profiles/<int:pk>/upload-image/", UserProfileView.as_view({"post": "upload_image"}), name="upload-image"),
    path("profiles/<int:pk>/update/", UserProfileView.as_view({'put': 'update'}), name="profile-update"),
    path("profiles/<int:pk>/follow/", follow, name="follow"),
    path("profiles/<int:pk>/unfollow/", unfollow, name="unfollow"),
]

app_name = "user"
