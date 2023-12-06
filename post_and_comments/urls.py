from django.urls import path, include

from post_and_comments.views import (
    PostCreateView,
    PostListView,
    PostDetailView
)
from rest_framework import routers

router = routers.DefaultRouter()
router.register("posts", PostListView)


urlpatterns = [
    path("post/create/", PostCreateView.as_view(), name="create-post"),
    path("", include(router.urls)),
    path("posts/<int:pk>/", PostDetailView.as_view(), name="post-detail"),
]

app_name = "post_and_comments"
