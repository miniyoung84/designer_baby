from django.db import models

# Create your models here.

class Player(models.Model):
    name = models.CharField(max_length=255)
    channel = models.IntegerField()
    silenced = models.BooleanField()
    ese = models.IntegerField()
    connections = models.ManyToManyField("self", blank=True, null=True)
class Place(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

class Dorm(models.Model):
    name = models.CharField(max_length=255)
    zone = models.CharField(max_length=3)
    place = models.ForeignKey("Place", on_delete=models.CASCADE)
    primary_color = models.CharField(max_length=7)
    secondary_color = models.CharField(max_length=7)
    team_name = models.CharField(max_length=255)

class Subject(models.Model):
    name = models.CharField(max_length=255)
    main_hall = models.ForeignKey("Place", on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
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

    #Skool
    job = models.CharField(max_length=255)
    major = models.ForeignKey("Subject", on_delete=models.CASCADE)
    minor = models.ForeignKey("Subject", on_delete=models.CASCADE)
    year = models.IntegerField(blank=True, null=True) #1 = Freshman, 2 = Sophomore, 3 = Junior, 4 = Senior
    primary_weapon = models.CharField(max_length=255, blank=True, null=True)
    secondary_weapon = models.CharField(max_length=255, blank=True, null=True)
    mutations = models.TextField(blank=True, null=True)

    #Foreign Keys
    player = models.ForeignKey("Player", on_delete=models.CASCADE)
    dorm = models.ForeignKey("Dorm", on_delete=models.CASCADE)

    #Misc
    pet = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

class Grade(models.Model):
    grade = models.IntegerField(blank=True, null=True)
    subject = models.ForeignKey("Subject", on_delete=models.CASCADE)
    student = models.ForeignKey("Character", on_delete=models.CASCADE)