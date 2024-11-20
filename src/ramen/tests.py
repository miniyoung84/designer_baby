from django.test import TestCase
from .models import *
from bakery.models import *
from cogs.bridging_cog import BridgingCog
from cogs.report_card_cog import parse_name
import datetime
    

class BridgingCogTestCase(TestCase):
    def setUp(self):
        p1 = Player.objects.create(name="Quinn", channel=DiscordChannel.objects.create(discord_id=12345678),
                                   discord_user=DiscordUser.objects.create(discord_id=5483845),
                                   ese=0)
        p2 = Player.objects.create(name="Zoe", channel=DiscordChannel.objects.create(discord_id=2342365),
                                   discord_user=DiscordUser.objects.create(discord_id=4363673457),
                                   ese=0)
    
    def test_one(self):
        cog = BridgingCog()
        result = BridgingCog.get_party_members(cog, 5483845)

        self.assertEqual(result, None)

class ReportCardCogTestCase(TestCase):
    def test_parse_name(self):

        sub = Subject(name="Cooking", description="Massaging")
        sub.save()

        # Create a random character
        sample_character = Character(
            first_name='Skibidi',
            last_name='Sigma',
            pronouns='he/him',
            age=30,
            ethnicity='Caucasian',
            species='Human',
            birthday=datetime.date(1992, 3, 26),
            alive=True,
            hair_color='Brown',
            eye_color='Blue',
            height=72,  # inches
            injury_status='Healthy',
            fav_color='#FF5733',  # Example hex color
            job='Adventurer',
            year=4,  # Senior
            primary_weapon='Sword',
            secondary_weapon='Shield',
            mutations='None',
            pet='Dragon',
            notes='Known for his bravery and strength.',
            major=sub,
            minor=sub
        )

        # Save the character to the database
        sample_character.save()


        # Make the same query as in report_card_cog.py
        first_name = Character.objects.get(id=sample_character.id).first_name
        nick_name = Character.objects.get(id=sample_character.id).nick_name
        last_name = Character.objects.get(id=sample_character.id).last_name

        # Test the parse_name function
        parsed_name = parse_name(first_name, nick_name, last_name)
        self.assertEqual(parsed_name, "Skibidi Sigma")