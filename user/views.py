from django.http import Http404
from django.shortcuts import redirect
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import UserProfile
from user.serializers import UserSerializer, UserProfileSerializer, UserProfileListSerializer, \
    UserProfileDetailSerializer, UserProfileImageSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            request.user.auth_token.delete()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(viewsets.ModelViewSet):
    queryset = UserProfile.objects.select_related("user").prefetch_related("following", "followers")
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        username = self.request.query_params.get("username")
        queryset = self.queryset

        if username:
            queryset = queryset.filter(username__icontains=username)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return UserProfileListSerializer
        if self.action == "retrieve":
            return UserProfileDetailSerializer
        if self.action == "upload_image":
            return UserProfileImageSerializer
        return UserProfileSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific movie"""
        user_profile = self.get_object()
        serializer = self.get_serializer(user_profile, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "username",
                type=OpenApiTypes.STR,
                description="Filter by user profile username (ex. ?username=dotcom)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@api_view(["POST"])
def follow(request, pk: int):
    current_user = request.user
    current_profile = UserProfile.objects.get(user=current_user)
    other_profile = UserProfile.objects.get(pk=pk)
    other_user = other_profile.user
    if current_user == other_user:
        raise ValueError("You can not follow yourself")
    current_profile.following.add(other_user)
    other_profile.followers.add(current_user)
    return redirect("profiles:userprofile-detail", pk=other_profile.pk)


@api_view(["POST"])
def unfollow(request, pk: int):
    current_user = request.user
    current_profile = UserProfile.objects.get(user=current_user)
    other_profile = UserProfile.objects.get(pk=pk)
    other_user = other_profile.user
    current_profile.following.remove(other_user)
    other_profile.followers.remove(current_user)
    return redirect("profiles:userprofile-detail", pk=other_profile.pk)
