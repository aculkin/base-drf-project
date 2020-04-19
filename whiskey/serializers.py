from rest_framework import serializers

from core.models import Tag, Place, Whiskey


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


class WhiskeySerializer(serializers.ModelSerializer):
    """Serialize a Whiskey"""
    places = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Place.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Whiskey
        fields = (
            'id', 'brand', 'style', 'year',
            'price', 'link', 'tags', 'places'
        )
        read_only_fields = ('id',)


class WhiskeyDetailSerializer(WhiskeySerializer):
    """Serialize a whiskey detail"""
    places = PlaceSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)


class WhiskeyImageSerializer(serializers.ModelSerializer):
    """Serialize a whiskey image"""

    class Meta:
        model = Whiskey
        fields = ('id', 'image')
        read_only = ('id',)
