from django.urls import path, include

from post_and_comments.views import (
    PostCreateView,
    PostListView,
    PostDetailView,
    CommentsListView, CommentsCreateView, LikeView
)
from rest_framework import routers

router = routers.DefaultRouter()
router.register("posts", PostListView)
router.register("comments", CommentsListView)

urlpatterns = [
    path("post/create/", PostCreateView.as_view(), name="create-post"),
    path("", include(router.urls)),
    path("posts/<int:pk>/", PostDetailView.as_view(), name="post-detail"),
    path("posts/<int:pk>/like/", LikeView.as_view(), name="like"),
    path("create-comment/", CommentsCreateView.as_view(), name="create-comment"),
]

app_name = "post_and_comments"
