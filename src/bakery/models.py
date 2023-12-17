from django.db import models

# Create your models here.

class DiscordUser(models.Model):
    discord_id = models.IntegerField()

class DiscordChannel(models.Model):
    discord_id = models.IntegerField()
    competitive = models.BooleanField(default=False)

class IntroSound(models.Model):
    file_name = models.CharField()
    desc = models.TextField()
    short = models.BooleanField(default=False)
    user = models.ForeignKey(DiscordUser, on_delete=models.CASCADE)
    generic = models.BooleanField(default=False)
    length = models.IntegerField()