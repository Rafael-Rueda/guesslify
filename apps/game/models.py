from django.contrib.auth.models import User
from django.db import models

from apps.rooms.models import Room


class PlaylistControl(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    room = models.ForeignKey(to=Room, on_delete=models.CASCADE)
    playlist_preview_url = models.CharField(max_length=500, null=True)
    playlist_cover = models.CharField(max_length=500, null=True)
    playlist_name = models.CharField(max_length=500, null=True)
    playlist_artist = models.CharField(max_length=500, null=True)
    blacklisted = models.BooleanField(default=False)

class QueueMusic(models.Model):
    queue = models.ForeignKey(to=PlaylistControl, on_delete=models.CASCADE, null=True)
    room = models.ForeignKey(to=Room, on_delete=models.CASCADE)
    ended = models.BooleanField(default=False)
    voting = models.BooleanField(default=False)

class VoteTimer(models.Model):
    room = models.ForeignKey(to=Room, on_delete=models.CASCADE)
    seconds = models.IntegerField(default=15)
    results = models.BooleanField(default=False)