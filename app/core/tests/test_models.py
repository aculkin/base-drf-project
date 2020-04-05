from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(username='TestUser', password='TestPass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(username, password)


class ModelTests(TestCase):

    def test_create_user_with_username_successful(self):
        """Test Creating a New User with an username is successful"""
        username = 'testuser'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            username=username,
            password=password
        )

        self.assertEqual(user.username, username)
        self.assertTrue(user.check_password(password))

    def test_create_new_superuser(self):
        '''test creating a new superuser'''
        user = get_user_model().objects.create_superuser(
            'testAdmion',
            'passAdmin123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Bourbon'
        )

        self.assertEqual(str(tag), tag.name)

    def test_places_str(self):
        """Test the places string representation"""
        place = models.Place.objects.create(
            user=sample_user(),
            name='BoilerMaker'
        )

        self.assertEqual(str(place), place.name)

    def test_whiskey_str(self):
        """Test the Whiskey string representation"""
        whiskey = models.Whiskey.objects.create(
            user=sample_user(),
            brand='Jack Daniels',
            style='Bourbon',
            )
        self.assertEqual(str(whiskey), whiskey.brand)
