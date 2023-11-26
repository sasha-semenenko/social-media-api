from django.contrib.auth import get_user_model
from rest_framework import serializers

from user.models import UserProfile


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password", "is_staff")
        read_only_fields = ("is_staff",)
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("id", "username", "bio", "picture")


class UserProfileListSerializer(UserProfileSerializer):

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "user_id",
            "username",
            "following",
            "followers",
            "picture"
        )


class UserProfileDetailSerializer(UserProfileListSerializer):
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "user",
            "username",
            "bio",
            "picture",
            "following",
            "followers"
        )


class UserProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("id", "picture")
