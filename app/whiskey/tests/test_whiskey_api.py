import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Whiskey, Tag, Place

from whiskey.serializers import WhiskeySerializer, WhiskeyDetailSerializer


WHISKEY_URL = reverse('whiskey:whiskey-list')


def image_upload_url(whiskey_id):
    """return url for whiskey image upload"""
    return reverse('whiskey:whiskey-upload-image', args=[whiskey_id])


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

    def test_update_whiskey_partial(self):
        """Test updating a whiskey with patch"""
        whiskey = sample_whiskey(user=self.user)
        whiskey.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Fire')

        payload = {'brand': 'Woodford Reserve', 'tags': [new_tag.id]}
        url = detail_url(whiskey.id)
        self.client.patch(url, payload)

        whiskey.refresh_from_db()
        self.assertEqual(whiskey.brand, payload['brand'])
        tags = whiskey.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_update_whiskey_full(self):
        """Test updating a whiskey with put"""
        whiskey = sample_whiskey(user=self.user)
        whiskey.tags.add(sample_tag(user=self.user))
        payload = {
            'brand': 'Jack Daniels',
            'style': 'Whiskey',
        }
        url = detail_url(whiskey.id)
        self.client.put(url, payload)

        whiskey.refresh_from_db()
        self.assertEqual(whiskey.brand, payload['brand'])
        self.assertEqual(whiskey.style, payload['style'])
        tags = whiskey.tags.all()
        self.assertEqual(len(tags), 0)


class WhiskeyImageUploadTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'SampleUser',
            'SamplePassword'
        )
        self.client.force_authenticate(self.user)
        self.whiskey = sample_whiskey(user=self.user)

    def teardown(self):
        self.whiskey.image.delete()

    def test_upload_image_to_whiskey(self):
        """Test uploaded an image to whiskey"""
        url = image_upload_url(self.whiskey.id)
        with tempfile.NamedTemporaryFile(suffix='.jpeg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='jpeg')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')
            self.whiskey.refresh_from_db()
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertIn('image', res.data)
            self.assertTrue(os.path.exists(self.whiskey.image.path))

    def test_upload_image_bad_request(self):
        """test uploading an invalid image"""
        url = image_upload_url(self.whiskey.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_whiskey_by_tags(self):
        """Test returning whiskey with specific tags"""
        whiskey1 = sample_whiskey(user=self.user, brand='Jack Daniels')
        whiskey2 = sample_whiskey(user=self.user, brand='WoodFord Reserve')
        tag1 = sample_tag(user=self.user, name='Bitter')
        tag2 = sample_tag(user=self.user, name='Sweet')
        whiskey1.tags.add(tag1)
        whiskey2.tags.add(tag2)
        whiskey3 = sample_whiskey(user=self.user, brand='Bud')

        res = self.client.get(
            WHISKEY_URL,
            {'tags': f'{tag1.id}, {tag2.id}'}
        )

        serializer1 = WhiskeySerializer(whiskey1)
        serializer2 = WhiskeySerializer(whiskey2)
        serializer3 = WhiskeySerializer(whiskey3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_whiskey_by_places(self):
        """Test returning whiskey with specific places"""
        whiskey1 = sample_whiskey(user=self.user, brand='Jack Daniels')
        whiskey2 = sample_whiskey(user=self.user, brand='WoodFord Reserve')
        place1 = sample_place(user=self.user, name='BoilerMaker')
        place2 = sample_place(user=self.user, name='Bjs')
        whiskey1.places.add(place1)
        whiskey2.places.add(place2)
        whiskey3 = sample_whiskey(user=self.user, brand='Bud')

        res = self.client.get(
            WHISKEY_URL,
            {'places': f'{place1.id}, {place2.id}'}
        )

        serializer1 = WhiskeySerializer(whiskey1)
        serializer2 = WhiskeySerializer(whiskey2)
        serializer3 = WhiskeySerializer(whiskey3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
