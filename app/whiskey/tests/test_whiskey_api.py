from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Whiskey, Tag, Place

from whiskey.serializers import WhiskeySerializer, WhiskeyDetailSerializer


WHISKEY_URL = reverse('whiskey:whiskey-list')


def detail_url(whiskey_id):
    """Return whiskey detail url"""
    return reverse('whiskey:whiskey-detail', args=[whiskey_id])


def sample_tag(user, name='Bitter'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_place(user, name='Campbell Brewery'):
    '''Create and return a sample ingredient'''
    return Place.objects.create(user=user, name=name)


def sample_whiskey(user, **params):
    """Create and return a sample whiskey"""
    defaults = {
        'brand': 'Sample Whiskey',
        'style': 'Bourbon'
    }
    defaults.update(params)

    return Whiskey.objects.create(user=user, **defaults)


class PublicWhiskeyAPITest(TestCase):
    """Test unauthenticated Whiskey API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authenication is required"""
        res = self.client.get(WHISKEY_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateWhiskeyAPITest(TestCase):
    """Test authenticated Whiskey API Access"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'Test User',
            'TestPass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_whiskey(self):
        """Test retrieving a list of whiskys"""
        sample_whiskey(user=self.user)
        sample_whiskey(user=self.user)

        res = self.client.get(WHISKEY_URL)

        whiskeys = Whiskey.objects.all().order_by('-id')
        serializer = WhiskeySerializer(whiskeys, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_whiskey_limited_to_user(self):
        """Test retrieving whiskey for user"""
        user2 = get_user_model().objects.create_user(
            'Test User2',
            'Testpass123'
        )
        sample_whiskey(user=user2)
        sample_whiskey(user=self.user)

        res = self.client.get(WHISKEY_URL)

        whiskeys = Whiskey.objects.filter(user=self.user)
        serializer = WhiskeySerializer(whiskeys, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_whiskey_detail(self):
        """Test viewing a whiskey detail"""
        whiskey = sample_whiskey(user=self.user)
        whiskey.tags.add(sample_tag(user=self.user))
        whiskey.places.add(sample_place(user=self.user))

        url = detail_url(whiskey.id)
        res = self.client.get(url)

        serializer = WhiskeyDetailSerializer(whiskey)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_whiskey(self):
        """Test creating a whiskey"""
        payload = {
            'brand': 'Jack Daniels',
            'style': 'Whiskey'
        }
        res = self.client.post(WHISKEY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        whiskey = Whiskey.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(whiskey, key))

    def test_create_whiskey_with_tags(self):
        """Test creating a whiskey with tags"""
        tag1 = sample_tag(user=self.user, name='Fire')
        tag2 = sample_tag(user=self.user, name='Sweet')

        payload = {
            'brand': 'Jack Daniel',
            'style': 'Bourbon',
            'tags': {tag1.id, tag2.id}
        }

        res = self.client.post(WHISKEY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        whiskey = Whiskey.objects.get(id=res.data['id'])
        tags = whiskey.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_whiskey_with_place(self):
        """Test creating whiskey with place"""
        place1 = sample_place(user=self.user, name='Campbell Brewery')
        place2 = sample_place(user=self.user, name='BoilerMaker')

        payload = {
            'brand': 'Woodford Reserve',
            'style': 'Bourbon',
            'places': {place1.id, place2.id}
        }
        res = self.client.post(WHISKEY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        whiskey = Whiskey.objects.get(id=res.data['id'])
        places = whiskey.places.all()
        self.assertEqual(places.count(), 2)
        self.assertIn(place1, places)
        self.assertIn(place2, places)
