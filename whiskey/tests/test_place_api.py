from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Place, Whiskey

from whiskey.serializers import PlaceSerializer

PLACE_URL = reverse('whiskey:place-list')


class PublicPlaceAPITest(TestCase):
    """Test the publicly available places API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """test that login is required to access the endpoint"""
        res = self.client.get(PLACE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePlaceAPITest(TestCase):
    """Test place can be retrieved by authorized user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='Test User',
            password='TestPassword'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_place_list(self):
        """Test retrieving a list of places"""
        Place.objects.create(user=self.user, name='BoilerMaker')
        Place.objects.create(user=self.user, name='Lazy Dog')

        res = self.client.get(PLACE_URL)

        places = Place.objects.all().order_by('-name')
        serializer = PlaceSerializer(places, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_place_limited_to_user(self):
        """Test that places for the authenticated user are returned"""
        user2 = get_user_model().objects.create_user(
            'Test User2',
            'TestPass234'
        )
        Place.objects.create(user=user2, name='Speakeasy SF')
        place = Place.objects.create(user=self.user, name='Campbell Brewery')
        res = self.client.get(PLACE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], place.name)

    def test_create_place_successful(self):
        """Test creating place"""
        payload = {'name': 'Campbell Brewery'}
        self.client.post(PLACE_URL, payload)

        exists = Place.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_place_invalid(self):
        """Test creating invalid place fails"""
        payload = {'name': ''}
        res = self.client.post(PLACE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_places_assigned_to_whiskey(self):
        """Test filtering places by those assigned to whiskey"""
        place1 = Place.objects.create(
            user=self.user, name='Boiler Maker'
        )
        place2 = Place.objects.create(
            user=self.user, name="BJ's Brewery"
        )
        whiskey = Whiskey.objects.create(
            brand='Woodford Reserve',
            style='Bourbon',
            user=self.user
        )
        whiskey.places.add(place1)

        res = self.client.get(PLACE_URL, {'assigned_only': 1})

        serializer1 = PlaceSerializer(place1)
        serializer2 = PlaceSerializer(place2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_places_assigned_unique(self):
        '''Test filtering places by assigned returns unique items'''
        place = Place.objects.create(user=self.user, name='BoilerMaker')
        Place.objects.create(user=self.user, name='BJs')
        whiskey1 = Whiskey.objects.create(
            user=self.user,
            brand='Woodford',
            style='Whiskey'
        )
        whiskey1.places.add(place)
        whiskey2 = Whiskey.objects.create(
            user=self.user,
            brand='Mitchers',
            style='Bourbon'
        )
        whiskey2.places.add(place)

        res = self.client.get(PLACE_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
