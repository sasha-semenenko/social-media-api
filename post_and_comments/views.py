from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, generics

from post_and_comments.models import Post
from post_and_comments.serializers import (
    PostCreateSerializer,
    PostListSerializer,
    PostDetailSerializer
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
