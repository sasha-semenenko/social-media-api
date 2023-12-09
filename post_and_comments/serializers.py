from rest_framework import serializers

from post_and_comments.models import Post, Comments, Like
from user.serializers import UserProfileDetailSerializer


class PostListSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)
    comments = serializers.CharField(source="get_count_comments", read_only=True)

    class Meta:
        model = Post
        fields = ("id", "author", "title", "content", "created_at", "image", "comments")


class PostDetailSerializer(serializers.ModelSerializer):
    author = UserProfileDetailSerializer(many=False, read_only=True)
    likes = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ("id", "author", "title", "content", "created_at", "image", "likes")

    def get_likes(self, post):
        return Like.objects.filter(post=post).count()


class PostCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = "__all__"


class CommentsListSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)
    post = serializers.CharField(source="post.title", read_only=True)

    class Meta:
        model = Comments
        fields = ("id", "author", "post", "created_at", "content")


class CommentsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = "__all__"


class LikeSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = Like
        fields = ("id", "author", "created_at")
