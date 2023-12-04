from django.contrib.auth.models import User
from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=16)
    password = models.CharField(max_length=50, default=None, null=True, blank=True)
    slug = models.SlugField(unique=True)
    capacity = models.IntegerField(default=6)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class UserInRoom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    host = models.BooleanField(default=False)

class TokenForUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=999)