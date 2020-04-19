from django.urls import path, include
from rest_framework.routers import DefaultRouter

from whiskey import views


router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('places', views.PlaceViewSet)
router.register('whiskeys', views.WhiskeyViewSet)

app_name = 'whiskey'

urlpatterns = [
    path('', include(router.urls))
]
