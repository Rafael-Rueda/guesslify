# Generated by Django 4.2.7 on 2023-11-29 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_queuemusic_ended'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlistcontrol',
            name='blacklisted',
            field=models.BooleanField(default=False),
        ),
    ]
