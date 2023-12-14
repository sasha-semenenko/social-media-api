import os
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from user.models import UserProfile
from user.serializers import (
    UserProfileListSerializer,
    UserProfileDetailSerializer
)

USERPROFILE_URL = reverse("profiles:profile-list")


def sample_userprofile(**params):
    data = {
        "user": "test-user",
        "username": "test-username",
        "bio": "test-bio"
    }
    data.update(params)
    return UserProfile.objects.create(**data)


def detail_url(profile_id: int):
    return reverse("profiles:profile-detail", kwargs={"pk": profile_id})


def image_upload_url(userprofile_id):
    """Return URL for recipe image upload"""
    return reverse("profiles:upload-image", args=[userprofile_id])


class UnauthenticatedUserProfileApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(USERPROFILE_URL)
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_user(self):
        user = get_user_model().objects.create_user(
            email="user@user.com", password="user-pass"
        )
        data = {
            "user": user,
            "bio": "test-bio",
            "username": "user-username"
        }
        url = reverse("user:create-userprofile")
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserProfileApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="sem@email.com",
            password="password_sem"
        )
        self.client.force_authenticate(self.user)

    def test_userprofile_list(self):
        user1 = get_user_model().objects.create_user(
            email="test@email.com",
            password="password_test"
        )
        user2 = get_user_model().objects.create_user(
            email="tst@email.com",
            password="password_tst"
        )

        userprofile1 = sample_userprofile(user=user1, username="test")
        userprofile2 = sample_userprofile(user=user2, username="tst")

        user_profiles = UserProfile.objects.all()
        response = self.client.get(USERPROFILE_URL)
        serializer = UserProfileListSerializer(user_profiles, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

        serializer1 = UserProfileListSerializer(userprofile1)
        serializer2 = UserProfileListSerializer(userprofile2)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)

    def test_retrieve_userprofile_detail(self):
        user = get_user_model().objects.create_user(
            email="detail@email.com",
            password="password_detail"
        )
        userprofile = sample_userprofile(user=user, username="detail")

        url = detail_url(userprofile.id)

        response = self.client.get(url)
        serializer = UserProfileDetailSerializer(userprofile)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(serializer.data, response.data)

    def test_create_userprofile_forbidden(self):
        user = get_user_model().objects.create_user(
            email="forbiddenl@email.com",
            password="password_forbidden"
        )
        userprofile = sample_userprofile(user=user, username="forbidden")

        data = {
            "user": user,
            "username": userprofile.username,
            "bio": "bio"
        }

        response = self.client.post(USERPROFILE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_following_userprofile(self):
        other_user = get_user_model().objects.create_user(
            "other@email.com", "password"
        )
        self.client.force_authenticate(other_user)

        user_profile = UserProfile.objects.create(user=self.user, username="current")
        other_profile = UserProfile.objects.create(user=other_user, username="other")

        other_profile.follow.add(self.user)

        url = reverse("profiles:follow", args=[self.user.id])

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        other_detail_url = detail_url(other_profile.id)
        response_detail_url_other = self.client.get(other_detail_url)
        response_profiles = self.client.get(reverse("profiles:profile-list"))

        profile = UserProfile.objects.all()
        serializer = UserProfileListSerializer(profile, many=True)

        self.assertEqual(serializer.data, response_profiles.data)
        self.assertIn(self.user.id, response_detail_url_other.data["follow"])

    def test_unfollow_userprofile(self):

        other_user = get_user_model().objects.create_user(
            "other@email.com", "password"
        )
        self.client.force_authenticate(other_user)

        user_profile = UserProfile.objects.create(user=self.user, username="current")
        other_profile = UserProfile.objects.create(user=other_user, username="other")
        other_profile.follow.add(self.user)

        url = reverse("profiles:unfollow", args=[self.user.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        other_detail_url = detail_url(other_profile.id)
        response_detail_url_other = self.client.get(other_detail_url)
        response_profiles = self.client.get(reverse("profiles:profile-list"))

        profile = UserProfile.objects.all()
        serializer = UserProfileListSerializer(profile, many=True)

        self.assertEqual(serializer.data, response_profiles.data)
        self.assertNotIn(self.user.id, response_detail_url_other.data["follow"])


class UserProfileImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@social_media.com", "password"
        )
        self.userprofile = sample_userprofile(user=self.user, username="social")
        self.client.force_authenticate(self.user)

    def tearDown(self):
        self.userprofile.picture.delete()

    def test_upload_image_to_userprofile(self):
        """Test uploading an image to movie"""
        url = image_upload_url(self.userprofile.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"picture": ntf}, format="multipart")
        self.userprofile.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("picture", res.data)
        self.assertTrue(os.path.exists(self.userprofile.picture.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.userprofile.id)
        res = self.client.post(url, {"picture": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_image_url_is_shown_on_userprofile_detail(self):
        url = image_upload_url(self.userprofile.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"picture": ntf}, format="multipart")
        res = self.client.get(detail_url(self.userprofile.id))

        self.assertIn("picture", res.data)

    def test_image_url_is_shown_on_userprofile_list(self):
        url = image_upload_url(self.userprofile.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"picture": ntf}, format="multipart")
        res = self.client.get(USERPROFILE_URL)

        self.assertIn("picture", res.data[0].keys())
