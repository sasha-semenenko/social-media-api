from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from post_and_comments.models import Post
from post_and_comments.serializers import (
    PostListSerializer,
    PostDetailSerializer
)
from user.models import UserProfile


POST_URL = reverse("posts:post-list")


def detail_url(post_id: int):
    return reverse("posts:post-detail", kwargs={"pk": post_id})


def sample_post(**params):
    data = {
        "title": "title",
        "author": "author",
        "content": "Test content",
        "created_at": "2023-12-12T15:28:10Z"
    }
    data.update(params)
    return Post.objects.create(**data)


class UnauthenticatedPostApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(POST_URL)
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_post_auth_required(self):
        post = sample_post(title="title 1", author=UserProfile.objects.create(
            user=get_user_model().objects.create_user(
                "newone@email.com", "pass-new"
            )
        ))
        data = {
            "title": "title",
            "author": post.author,
            "content": "content",
        }
        url = reverse("posts:create-post")
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPostApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            email="user@user.com",
            password="password_user"
        )
        self.author = UserProfile.objects.create(user=user)
        self.client.force_authenticate(user)

    def test_post_list(self):

        post1 = sample_post(title="title 1", author=self.author)
        post2 = sample_post(title="title 2", author=self.author)

        posts = Post.objects.all()
        response = self.client.get(POST_URL)
        serializer = PostListSerializer(posts, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

        serializer1 = PostListSerializer(post1)
        serializer2 = PostListSerializer(post2)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)

    def test_post_filter_by_title(self):
        post1 = sample_post(title="title_1", author=self.author)
        post2 = sample_post(title="title_2", author=self.author)

        response = self.client.get(POST_URL, {"title": "title_1"})

        serializer1 = PostListSerializer(post1)
        serializer2 = PostListSerializer(post2)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_post_filter_by_author(self):
        user1 = get_user_model().objects.create_user(
            email="social@social.com",
            password="pass-user"
        )
        user2 = get_user_model().objects.create_user(
            email="new@new.com",
            password="pass-new"
        )
        author1 = UserProfile.objects.create(
            user=user1, username="user1-username"
        )
        author2 = UserProfile.objects.create(
            user=user2, username="user2-username"
        )
        post1 = sample_post(author=author1)
        post2 = sample_post(author=author2)

        response = self.client.get(POST_URL, {"author": "user2"})

        serializer1 = PostListSerializer(post1)
        serializer2 = PostListSerializer(post2)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)

    def test_retrieve_post_detail(self):
        post = sample_post(title="new", author=self.author)

        url = detail_url(post.id)

        response = self.client.get(url)
        serializer = PostDetailSerializer(post)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(serializer.data, response.data)

    def test_create_post_forbidden(self):
        post = sample_post(title="submarine", author=UserProfile.objects.create(
            user=get_user_model().objects.create_user(
                "email@email.com", "pass-email"
            ), username="username"
        ))
        data = {
            "title": "new title",
            "author": post.author,
            "content": "content"
        }

        response = self.client.post(POST_URL, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
