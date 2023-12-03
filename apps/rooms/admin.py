from django.contrib import admin
from apps.rooms import models

admin.site.register(models.Room)
admin.site.register(models.UserInRoom)
