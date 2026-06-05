from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    nickname = models.CharField(max_length=50, verbose_name='별명')
    created_at = models.DateTimeField(auto_now_add=True)

    email = models.EmailField(blank=True, default='')
    first_name = models.CharField(max_length=150, blank=True, default='')
    last_name = models.CharField(max_length=150, blank=True, default='')

    def __str__(self):
        return f'{self.username} ({self.nickname})'