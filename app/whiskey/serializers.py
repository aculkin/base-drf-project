from rest_framework import serializers

from core.models import Tag, Place


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class PlaceSerializer(serializers.ModelSerializer):
    """Serializer for place objects"""

    class Meta:
        model = Place
        fields = ('id', 'name')
        read_only_fields = ('id',)
