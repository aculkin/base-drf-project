from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Whiskey

from whiskey.serializers import TagSerializer

TAGS_URL = reverse('whiskey:tag-list')


class PublicTagsAPITest(TestCase):
    """Test publically available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test taht login is required for retrieving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITest(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'TestUser',
            'TestPassword123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='Bourbon')
        Tag.objects.create(user=self.user, name='Rye')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            'user2',
            'testpass123'
        )
        Tag.objects.create(user=user2, name='Scotch')
        tag = Tag.objects.create(user=self.user, name='Southern')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {'name': 'Test Tag'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            name='Test Tag',
            user=self.user
        ).exists()

        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test create tag with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_whiskey(self):
        '''test filtering tags by those assigned to whiskeys'''
        tag1 = Tag.objects.create(user=self.user, name='Night Out')
        tag2 = Tag.objects.create(user=self.user, name='Steak Whiskey')
        whiskey = Whiskey.objects.create(
            brand='Jack Daniels',
            style='Whiskey',
            user=self.user
        )
        whiskey.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        """test filtering tags assigned returns unique items"""
        tag = Tag.objects.create(user=self.user, name='Night Out')
        Tag.objects.create(user=self.user, name='Steak Whiskey')
        whiskey1 = Whiskey.objects.create(
            brand='Woodford Reserve',
            style='Bourbon',
            user=self.user
        )
        whiskey1.tags.add(tag)
        whiskey2 = Whiskey.objects.create(
            brand='Jack Daniels',
            style='Whiskey',
            user=self.user
        )
        whiskey2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
