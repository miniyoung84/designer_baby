from django.test import TestCase
from .models import Character, Subject
from cogs.report_card_cog import parse_name
import datetime

# Create your tests here.
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
        parsed_name = parse_name(first_name, last_name, nick_name)
        self.assertEqual(parsed_name, "Skibidi Sigma")