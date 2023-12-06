from rest_framework import serializers

from post_and_comments.models import Post
from user.serializers import UserProfileDetailSerializer


class PostListSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Post
        fields = ("id", "author", "title", "content", "created_at", "image")


class PostDetailSerializer(serializers.ModelSerializer):
    author = UserProfileDetailSerializer(many=False, read_only=True)

    class Meta:
        model = Post
        fields = ("id", "author", "title", "content", "created_at", "image")


class PostCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = "__all__"
