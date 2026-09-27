from django.contrib.auth.models import User
from django.db import models


def user_avatar_path(instance, filename):
    return f"avatars/user_{instance.user.pk}/{filename}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    agreement_accepted = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to=user_avatar_path, null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
