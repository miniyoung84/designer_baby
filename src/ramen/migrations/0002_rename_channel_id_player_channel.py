# Generated by Django 5.0.4 on 2024-05-22 08:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ramen', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='player',
            old_name='channel_id',
            new_name='channel',
        ),
    ]
