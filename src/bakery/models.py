from django.db import models
# Create your models here.
class DiscordUser(models.Model):
  discord_id = models.BigIntegerField()
  boosts = models.IntegerField(blank=True, null=True)
  description = models.CharField(max_length=255, blank=True, null=True)

  def __str__(self):
    return self.description

class DiscordChannel(models.Model):
  discord_id = models.BigIntegerField()
  competitive = models.BooleanField(default=False)
  max_length = models.IntegerField(blank=True, null=True)

class IntroSound(models.Model):
  file_name = models.CharField(max_length=255)
  short = models.BooleanField(default=False)
  user = models.ForeignKey(DiscordUser, on_delete=models.CASCADE)
  generic = models.BooleanField(default=False)
  length = models.FloatField()
  last_played = models.DateTimeField(blank=True, null=True)
  condition = models.JSONField(blank=True, null=True)

class ValorantAgent(models.Model):
  name = models.CharField(max_length=255)
  smokes = models.BooleanField(null=True, blank=True)
  blinds = models.BooleanField(null=True, blank=True)
  scouts = models.BooleanField(null=True, blank=True)
  flanks = models.BooleanField(null=True, blank=True)
  duels = models.BooleanField(null=True, blank=True)
  controls = models.BooleanField(null=True, blank=True)
  initiates = models.BooleanField(null=True, blank=True)
  sentinels = models.BooleanField(null=True, blank=True)
  heals = models.BooleanField(null=True, blank=True)
  stuns = models.BooleanField(null=True, blank=True)
  aoe = models.BooleanField(null=True, blank=True)
  walls = models.BooleanField(null=True, blank=True)
  emoji = models.CharField(max_length=255)

  def __str__(self):
    return self.name