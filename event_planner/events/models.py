from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from locations.models import Location  # модель из первого этапа

class Event(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('published', 'Опубликовано'),
        ('cancelled', 'Отменено'),
    ]

    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    pub_datetime = models.DateTimeField(verbose_name='Дата и время публикации')
    start_datetime = models.DateTimeField(verbose_name='Дата и время начала')
    end_datetime = models.DateTimeField(verbose_name='Дата и время завершения')
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='events',
        verbose_name='Автор'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='events',
        verbose_name='Место проведения'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(25)],
        verbose_name='Рейтинг (0-25)'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Статус')
    preview = models.ImageField(upload_to='previews/', blank=True, null=True, verbose_name='Превью')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'
        ordering = ['-pub_datetime']

    def __str__(self):
        return self.title

class WeatherData(models.Model):
    WIND_DIRECTION_CHOICES = [
        ('N', 'Северный'),
        ('NNE', 'Северо-северо-восточный'),
        ('NE', 'Северо-восточный'),
        ('ENE', 'Восточно-северо-восточный'),
        ('E', 'Восточный'),
        ('ESE', 'Восточно-юго-восточный'),
        ('SE', 'Юго-восточный'),
        ('SSE', 'Юго-юго-восточный'),
        ('S', 'Южный'),
        ('SSW', 'Юго-юго-западный'),
        ('SW', 'Юго-западный'),
        ('WSW', 'Западно-юго-западный'),
        ('W', 'Западный'),
        ('WNW', 'Западно-северо-западный'),
        ('NW', 'Северо-западный'),
        ('NNW', 'Северо-северо-западный'),
    ]

    event = models.OneToOneField(
        'Event',
        on_delete=models.CASCADE,
        related_name='weather_data',
        verbose_name='Мероприятие'
    )
    temperature = models.FloatField(verbose_name='Температура (°C)')
    humidity = models.PositiveSmallIntegerField(verbose_name='Влажность (%)')
    pressure = models.PositiveSmallIntegerField(verbose_name='Давление (мм рт. ст.)')
    wind_direction = models.CharField(
        max_length=3,
        choices=WIND_DIRECTION_CHOICES,
        verbose_name='Направление ветра'
    )
    wind_speed = models.FloatField(verbose_name='Скорость ветра (м/с)')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время обновления')

    class Meta:
        verbose_name = 'Данные погоды'
        verbose_name_plural = 'Данные погоды'

    def __str__(self):
        return f"Погода для {self.event.title} на {self.updated_at}"

class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='event_images/', verbose_name='Изображение')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Изображение мероприятия'
        verbose_name_plural = 'Изображения мероприятий'

    def __str__(self):
        return f"Изображение для {self.event.title}"