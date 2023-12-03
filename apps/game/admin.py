from django.contrib import admin

from apps.game.models import PlaylistControl, QueueMusic, VoteTimer

admin.site.register(PlaylistControl)
admin.site.register(QueueMusic)
admin.site.register(VoteTimer)
