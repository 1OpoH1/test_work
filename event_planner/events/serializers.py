from rest_framework import serializers
from .models import Event, EventImage, WeatherData
from locations.serializers import LocationSerializer

class WeatherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherData
        fields = ['temperature', 'humidity', 'pressure', 'wind_direction', 'wind_speed', 'updated_at']
        read_only_fields = fields


class EventImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventImage
        fields = ['id', 'image', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

class EventImageUploadSerializer(serializers.Serializer):
    """Сериализатор для загрузки изображения мероприятия"""
    image = serializers.ImageField(
        help_text='Изображение для мероприятия (поддерживаются JPG, PNG, GIF)',
        allow_empty_file=False,
        use_url=False
    )
    
    class Meta:
        ref_name = 'EventImageUpload'


class EventSerializer(serializers.ModelSerializer):
    location_detail = LocationSerializer(source='location', read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    images = EventImageSerializer(many=True, read_only=True)
    weather_data = WeatherDataSerializer(read_only=True)  # добавляем вложенный объект погоды

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'pub_datetime', 'start_datetime', 'end_datetime',
            'author', 'author_username', 'location', 'location_detail', 'weather_data',
            'rating', 'status', 'preview', 'images', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'preview', 'created_at', 'updated_at', 'weather_data']