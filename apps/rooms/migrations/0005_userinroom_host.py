# Generated by Django 4.2.7 on 2023-11-24 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0004_alter_room_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinroom',
            name='host',
            field=models.BooleanField(default=False),
        ),
    ]
