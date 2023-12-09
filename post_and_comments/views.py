from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, generics, mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from post_and_comments.models import Post, Comments, Like
from post_and_comments.serializers import (
    PostCreateSerializer,
    PostListSerializer,
    PostDetailSerializer,
    CommentsCreateSerializer,
    CommentsListSerializer,
    LikeSerializer
)
from user.models import UserProfile


class PostListView(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("author")
    serializer_class = PostListSerializer

    def get_queryset(self):
        title = self.request.query_params.get("title")
        author = self.request.query_params.get("author")
        queryset = self.queryset

        if title:
            queryset = queryset.filter(title__icontains=title)

        if author:
            queryset = queryset.filter(author__username__icontains=author)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PostDetailSerializer
        return PostListSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "author",
                type=OpenApiTypes.STR,
                description="Filter by author username (ex. ?author=social)",
            ),
            OpenApiParameter(
                "title",
                type=OpenApiTypes.STR,
                description="Filter by post title (ex. ?title=user)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.select_related("author")
    serializer_class = PostDetailSerializer


class PostCreateView(generics.CreateAPIView):
    queryset = Post.objects.select_related("author")
    serializer_class = PostCreateSerializer

    def perform_create(self, serializer):
        return serializer.save(
            author=UserProfile.objects.get(user=self.request.user)
        )


class CommentsListView(viewsets.ModelViewSet):
    queryset = Comments.objects.select_related("author", "post")
    serializer_class = CommentsListSerializer

    def get_queryset(self):
        queryset = self.queryset
        post = self.request.query_params.get("post")
        author = self.request.query_params.get("author")

        if post:
            queryset = queryset.filter(post__title__icontains=post)

        if author:
            queryset = queryset.filter(author__username__icontains=author)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "post",
                type=OpenApiTypes.STR,
                description="Filter by comments post (ex. ?post='social')",
            ),
            OpenApiParameter(
                "author",
                type=OpenApiTypes.STR,
                description="Filter by comments author's (ex. ?author='user')",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CommentsCreateView(generics.CreateAPIView):
    queryset = Comments.objects.select_related("author", "post")
    serializer_class = CommentsCreateSerializer


class LikeView(generics.CreateAPIView, mixins.DestroyModelMixin):
    serializer_class = LikeSerializer

    def get_queryset(self):
        user = self.request.user
        post = Post.objects.get(pk=self.kwargs["pk"])
        return Like.objects.filter(author=user, post=post)

    def perform_create(self, serializer):
        if self.get_queryset().exists():
            raise ValidationError("You have already liked for this post")
        serializer.save(author=self.request.user, post=Post.objects.get(pk=self.kwargs["pk"]))

    def delete(self, request, *args, **kwargs):
        if self.get_queryset().exists():
            self.get_queryset().delete()
            return Response(status.HTTP_200_OK)
        return ValidationError("You never liked this post")
