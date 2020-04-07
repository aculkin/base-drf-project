from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Place, Whiskey

from whiskey import serializers


class BaseWhiskeyAttrViewset(viewsets.GenericViewSet,
                             mixins.ListModelMixin,
                             mixins.CreateModelMixin):
    """Base viewset for user owned whiskey attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a new object"""
        return serializer.save(user=self.request.user)


class TagViewSet(BaseWhiskeyAttrViewset):
    """Manage tags in the database"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class PlaceViewSet(BaseWhiskeyAttrViewset):
    """Manage places in the database"""
    queryset = Place.objects.all()
    serializer_class = serializers.PlaceSerializer


class WhiskeyViewSet(viewsets.ModelViewSet):
    """Manage Whiskeys in database"""
    serializer_class = serializers.WhiskeySerializer
    queryset = Whiskey.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Retrieve the Whiskeys for the authenticated user"""
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropiate serializer class"""
        if self.action == 'retrieve':
            return serializers.WhiskeyDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new whiskey"""
        serializer.save(user=self.request.user)
