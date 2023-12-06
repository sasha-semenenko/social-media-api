import os
import uuid

from django.db import models
from django.utils.text import slugify

from user.models import UserProfile


def post_image(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads", "post_and_comments", filename)


class Post(models.Model):
    title = models.CharField(max_length=65)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="author", null=True)
    content = models.TextField()
    created_at = models.DateTimeField()
    image = models.ImageField(null=True, upload_to=post_image, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.author} - {self.title}"

