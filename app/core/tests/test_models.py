from django.test import TestCase
from django.contrib.auth import get_user_model


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
