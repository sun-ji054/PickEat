from django.db import models
from django.conf import settings


class Restaurant(models.Model):
    naver_id   = naver_id = models.CharField(max_length=50, unique=True, db_index=True)
    name       = models.CharField(max_length=100)
    picture    = models.URLField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.naver_id})'


class SavedRestaurant(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_restaurants',
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='saved_by',
    )
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'restaurant')
        ordering = ['-saved_at']

    def __str__(self):
        return f'{self.user.nickname} → {self.restaurant.name}'