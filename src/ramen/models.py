from django.db import models
from bakery.models import DiscordUser, DiscordChannel
from django.core.exceptions import ValidationError
import re

def validate_hex_color(value):
    # Regular expression to match hex color code in the format #RRGGBB or #RGB
    hex_color_pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'

    # Validate the value against the pattern
    if not re.match(hex_color_pattern, value):
        raise ValidationError('Enter a valid hex color code.')

class Player(models.Model):
    name = models.CharField(max_length=255)
    channel_id = models.ForeignKey(DiscordChannel, on_delete=models.CASCADE)
    discord_user = models.ForeignKey(DiscordUser, on_delete=models.CASCADE)
    silenced = models.BooleanField(default=False)
    ese = models.IntegerField()
    connections = models.ManyToManyField("self", blank=True)
    money = models.IntegerField(default=0)
    income = models.IntegerField(default=0)

    def __str__(self):
        return self.name
class Place(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Dorm(models.Model):
    name = models.CharField(max_length=255)
    zone = models.CharField(max_length=3)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    primary_color = models.CharField(max_length=7, validators=[validate_hex_color])
    secondary_color = models.CharField(max_length=7, validators=[validate_hex_color])
    team_name = models.CharField(max_length=255)
    funds = models.IntegerField(default=0)
    income = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=255)
    main_hall = models.ForeignKey(Place, on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
class Character(models.Model):
    #Name
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255)
    nick_name = models.CharField(max_length=255, blank=True, null=True)

    #Things Liberals Are Obsessed With
    pronouns = models.CharField(max_length=255)
    age = models.IntegerField(blank=True, null=True)
    ethnicity = models.CharField(max_length=255, blank=True, null=True)
    species = models.CharField(max_length=255, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    alive = models.BooleanField(default=True)
    hair_color = models.CharField(max_length=255, blank=True, null=True)
    eye_color = models.CharField(max_length=255, blank=True, null=True)
    height = models.IntegerField(blank=True, null=True) #inches
    injury_status = models.CharField(max_length=255, blank=True, null=True)
    fav_color = models.CharField(max_length=7, validators=[validate_hex_color])

    #Skool
    job = models.CharField(max_length=255)
    major = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='major_students')
    minor = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='minor_students')
    year = models.IntegerField(blank=True, null=True) #1 = Freshman, 2 = Sophomore, 3 = Junior, 4 = Senior
    primary_weapon = models.CharField(max_length=255, blank=True, null=True)
    secondary_weapon = models.CharField(max_length=255, blank=True, null=True)
    mutations = models.TextField(blank=True, null=True)

    #Foreign Keys
    player = models.ForeignKey(Player, on_delete=models.CASCADE, blank=True, null=True)
    dorm = models.ForeignKey(Dorm, on_delete=models.CASCADE, blank=True, null=True)

    #Misc
    pet = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Grade(models.Model):
    grade = models.IntegerField(blank=True, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    student = models.ForeignKey(Character, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student} - {self.subject}: {self.grade}"