from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from post_and_comments.models import Comments, Post
from post_and_comments.serializers import CommentsListSerializer
from user.models import UserProfile
COMMENT_URL = reverse("posts:comments-list")


def sample_comment(**params):
    data = {
        "author": "author",
        "post": "post",
        "created_at": "2023-12-27T19:29:00Z",
        "content": "content"
    }
    data.update(params)
    return Comments.objects.create(**data)


def detail_url(comment_id: int):
    return reverse("posts:comments-detail", kwargs={"pk": comment_id})


class UnauthenticatedCommentsApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            email="taras@email.com",
            password="password_taras"
        )
        self.author = UserProfile.objects.create(user=user, username="test-username")
        self.post = Post.objects.create(
            title="title-taras",
            author=self.author,
            content="content",
            created_at="2023-12-27T19:29:00Z",
        )

    def test_auth_required(self):
        response = self.client.get(COMMENT_URL)
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_comment_auth_required(self):
        data = {
            "author": self.author.username,
            "post": self.post.title,
            "content": "content",
        }
        url = reverse("posts:create-comment")
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCommentsApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            email="social@email.com",
            password="password_social"
        )
        self.author = UserProfile.objects.create(user=user, username="setup-user")
        self.post = Post.objects.create(
            title="title-social",
            author=self.author,
            content="content",
            created_at="2023-12-27T19:29:00Z"
        )
        self.client.force_authenticate(user)

    def test_comments_list(self):

        comment1 = sample_comment(author=self.author, post=self.post)
        comment2 = sample_comment(author=self.author, post=self.post)

        comments = Comments.objects.all()
        response = self.client.get(COMMENT_URL)
        serializer = CommentsListSerializer(comments, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

        serializer1 = CommentsListSerializer(comment1)
        serializer2 = CommentsListSerializer(comment2)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)

    def test_comment_filter_by_post_title(self):
        user1 = get_user_model().objects.create_user(
            email="taras@email.com",
            password="password_taras"
        )
        author1 = UserProfile.objects.create(user=user1, username="taras-user")
        post1 = Post.objects.create(
            title="title-taras",
            author=author1,
            content="content",
            created_at="2023-12-27T19:29:00Z"
        )
        user2 = get_user_model().objects.create_user(
            email="oleksiy@email.com",
            password="password_oleksiy"
        )
        author2 = UserProfile.objects.create(user=user2, username="oleksiy-user")
        post2 = Post.objects.create(
            title="title-oleksiy",
            author=author2,
            content="content",
            created_at="2023-12-27T19:29:00Z"
        )
        comment1 = sample_comment(author=author1, post=post1)
        comment2 = sample_comment(author=author2, post=post2)

        response = self.client.get(COMMENT_URL, {"post": "oleksiy"})

        serializer1 = CommentsListSerializer(comment1)
        serializer2 = CommentsListSerializer(comment2)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer1.data, response.data)

    def test_comment_filter_by_author(self):
        user1 = get_user_model().objects.create_user(
            email="black@black.com",
            password="pass-black"
        )
        user2 = get_user_model().objects.create_user(
            email="white@white.com",
            password="pass-white"
        )
        author1 = UserProfile.objects.create(
            user=user1, username="black-user"
        )
        author2 = UserProfile.objects.create(
            user=user2, username="white-user"
        )
        post1 = Post.objects.create(
            title="title-black",
            author=author1,
            content="content",
            created_at="2023-12-27T19:29:00Z")
        post2 = Post.objects.create(
            title="title-white",
            author=author2,
            content="content",
            created_at="2023-12-27T19:29:00Z")
        comment1 = sample_comment(author=author1, post=post1)
        comment2 = sample_comment(author=author2, post=post2)

        response = self.client.get(COMMENT_URL, {"author": "black"})

        serializer1 = CommentsListSerializer(comment1)
        serializer2 = CommentsListSerializer(comment2)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_retrieve_comment_detail(self):
        comments = Comments.objects.create(author=self.author, post=self.post, created_at="2023-12-27T19:29:00Z",)

        url = detail_url(comments.id)

        response = self.client.get(url)
        serializer = CommentsListSerializer(comments)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(serializer.data, response.data)

    def test_create_comment_forbidden(self):
        comment = sample_comment(author=self.author, post=self.post)
        data = {
            "title": "new title",
            "author": comment.author,
            "content": "content"
        }

        response = self.client.post(COMMENT_URL, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
