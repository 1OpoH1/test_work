from rest_framework import serializers
from .models import Event, EventImage
from locations.serializers import LocationSerializer  # создадим ниже, если ещё нет

class EventImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventImage
        fields = ['id', 'image', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class EventSerializer(serializers.ModelSerializer):
    # Вложенное представление места проведения для GET-запросов
    location_detail = LocationSerializer(source='location', read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    images = EventImageSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'pub_datetime', 'start_datetime', 'end_datetime',
            'author', 'author_username', 'location', 'location_detail', 'weather',
            'rating', 'status', 'preview', 'images', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'preview', 'created_at', 'updated_at']