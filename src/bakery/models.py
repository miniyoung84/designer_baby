from django.db import models

# Create your models here.

class DiscordUser(models.Model):
    booster = models.BooleanField(default=False)
    discord_id = models.IntegerField()