# from django.contrib.auth import get_user_model
# from django.test import TestCase
# from django.urls import reverse

# from rest_framework import status
# from rest_framework.test import APIClient

# from core.models import Whiskey, Tag, Place

# from whiskey.serializers import WhiskeySerializer, WhiskeyDetailSerializer


# WHISKEY_URL = reverse('whiskey:whiskey-list')


# def detail_url(whiskey_id):
#     """Return whiskey detail url"""
#     return reverse('whiskey:whiskey-detail', args=[whiskey_id])


# def sample_tag(user, name='Bitter'):
#     """Create and return a sample tag"""
#     return Tag.objects.create(user=user, name=name)


# def sample_place(user, name='Campbell Brewery'):
#     '''Create and return a sample ingredient'''
#     return Place.objects.create(user=user, name=name)


# def sample_whiskey(user, **params):
#     """Create and return a sample whiskey"""
#     defaults = {
#         'brand': 'Sample Whiskey',
#         'style': 'Bourbon'
#     }
#     defaults.update(params)

#     return Whiskey.objects.create(user=user, **defaults)


# class PublicWhiskeyAPITest(TestCase):
#     """Test unauthenticated Whiskey API access"""

#     def setUp(self):
#         self.client = APIClient()

#     def test_auth_required(self):
#         """Test that authenication is required"""
#         res = self.client.get(WHISKEY_URL)

#         self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# class PrivateWhiskeyAPITest(TestCase):
#     """Test authenticated Whiskey API Access"""

#     def setUp(self):
#         self.user = get_user_model().objects.create_user(
#             'Test User',
#             'TestPass123'
#         )
#         self.client = APIClient()
#         self.client.force_authenticate(self.user)

#     def test_retrieve_whiskey(self):
#         """Test retrieving a list of whiskys"""
#         sample_whiskey(user=self.user)
#         sample_whiskey(user=self.user)

#         res = self.client.get(WHISKEY_URL)

#         whiskeys = Whiskey.objects.all().order_by('-id')
#         serializer = WhiskeySerializer(whiskeys, many=True)

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data, serializer.data)

#     def test_whiskey_limited_to_user(self):
#         """Test retrieving whiskey for user"""
#         user2 = get_user_model().objects.create_user(
#             'Test User2',
#             'Testpass123'
#         )
#         sample_whiskey(user=user2)
#         sample_whiskey(user=self.user)

#         res = self.client.get(WHISKEY_URL)

#         whiskeys = Whiskey.objects.filter(user=self.user)
#         serializer = WhiskeySerializer(whiskeys, many=True)

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(res.data), 1)
#         self.assertEqual(res.data, serializer.data)

#     def test_view_whiskey_detail(self):
#         """Test viewing a whiskey detail"""
#         whiskey = sample_whiskey(user=self.user)
#         whiskey.tag.add(sample_tag(user=self.user))
#         whiskey.places.add(sample_place(user=self.user))

#         url = detail_url(whiskey.id)
#         res = self.client.get(url)

#         serializer = WhiskeyDetailSerializer(whiskey)
#         self.assertEqual(res.data, serializer.data)
