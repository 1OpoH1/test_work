import random
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from .models import Event, WeatherData

def generate_realistic_weather():
    """
    Генерация случайных, но реалистичных погодных данных.
    """
    # Температура от -30 до +40
    temperature = round(random.uniform(-30.0, 40.0), 1)
    # Влажность 30-100%
    humidity = random.randint(30, 100)
    # Давление 720-780 мм рт.ст.
    pressure = random.randint(720, 780)
    # Направление ветра (выбор из 16 направлений)
    wind_direction_choices = [code for code, _ in WeatherData.WIND_DIRECTION_CHOICES]
    wind_direction = random.choice(wind_direction_choices)
    # Скорость ветра 0-20 м/с
    wind_speed = round(random.uniform(0.0, 20.0), 1)
    return {
        'temperature': temperature,
        'humidity': humidity,
        'pressure': pressure,
        'wind_direction': wind_direction,
        'wind_speed': wind_speed,
    }

@shared_task
def send_event_notification(event_id, recipient_list, subject, message):
    """
    Отправка email-уведомления о новом мероприятии.
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )
    return f"Notification sent for event {event_id}"

@shared_task
def publish_scheduled_events():
    """
    Публикация мероприятий, у которых наступило время публикации.
    """
    now = timezone.now()
    events = Event.objects.filter(status='draft', pub_datetime__lte=now)
    count = 0
    for event in events:
        event.status = 'published'
        event.save(update_fields=['status'])
        # Отправляем уведомления при публикации (если есть подписчики)
        recipient_list = getattr(settings, 'NOTIFICATION_EMAIL_LIST', [])
        if recipient_list:
            subject = f"Новое мероприятие: {event.title}"
            message = (
                f"Опубликовано мероприятие: {event.title}\n"
                f"Описание: {event.description}\n"
                f"Дата начала: {event.start_datetime}\n"
                f"Место: {event.location.name if event.location else 'Не указано'}"
            )
            send_event_notification.delay(event.id, recipient_list, subject, message)
        count += 1
    return f"Published {count} events."

@shared_task
def update_event_weather():
    """
    Обновление прогноза погоды для мероприятий, начинающихся в ближайшие 7 дней.
    """
    now = timezone.now()
    end_range = now + timezone.timedelta(days=7)
    events = Event.objects.filter(
        start_datetime__gte=now,
        start_datetime__lte=end_range,
        location__isnull=False
    )

    updated = 0
    for event in events:
        weather_data = generate_realistic_weather()
        weather_obj, created = WeatherData.objects.update_or_create(event=event, defaults=weather_data)
        updated += 1
    return f"Weather updated for {updated} events."

def fetch_weather(lat, lon, target_datetime):
    """
    Получение прогноза погоды из OpenWeatherMap (пример).
    """
    api_key = getattr(settings, 'OPENWEATHER_API_KEY', None)
    if not api_key:
        return None
    # Здесь должен быть реальный запрос к API прогноза
    # Для демонстрации возвращаем заглушку
    # url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=ru"
    # response = requests.get(url)
    # if response.status_code == 200:
    #     data = response.json()
    #     # Найти прогноз, ближайший к target_datetime
    #     return f"{data['list'][0]['main']['temp']}°C, {data['list'][0]['weather'][0]['description']}"
    return "Солнечно, +20°C"  # временная заглушка