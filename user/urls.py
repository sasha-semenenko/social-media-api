from django.urls import path

from user.views import CreateUserView, CreateTokenView
from rest_framework.authtoken import views

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register-user"),
    path("login/", CreateTokenView.as_view(), name="login")
]

app_name = "user"
