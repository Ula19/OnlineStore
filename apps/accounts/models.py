from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    avatar = models.ImageField(
        verbose_name='Аватар',
        default='user_avatars/default_user.png',
        upload_to='user_avatars/',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=('jpg', 'png', 'jpeg',))],
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class SubscribedUsers(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email
