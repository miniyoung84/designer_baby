# Generated by Django 5.0.4 on 2024-05-22 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bakery', '0002_alter_discordchannel_discord_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='discorduser',
            name='description',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
