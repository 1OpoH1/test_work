from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch, MagicMock
from datetime import timedelta
from events.tasks import publish_scheduled_events, update_event_weather
from events.factories import EventFactory, PublishedEventFactory
from events.models import WeatherData

class CeleryTasksTest(TestCase):
    def setUp(self):
        self.now = timezone.now()
        
        # Мероприятие, которое должно опубликоваться
        self.draft_event_past = EventFactory(
            status='draft',
            pub_datetime=self.now - timedelta(hours=1)
        )
        
        # Мероприятие, которое ещё не должно публиковаться
        self.draft_event_future = EventFactory(
            status='draft',
            pub_datetime=self.now + timedelta(days=1)
        )
        
        # Уже опубликованное мероприятие
        self.published_event = PublishedEventFactory(
            pub_datetime=self.now - timedelta(days=1)
        )

    def test_publish_scheduled_events(self):
        """Тест публикации запланированных мероприятий"""
        result = publish_scheduled_events()
        
        self.draft_event_past.refresh_from_db()
        self.draft_event_future.refresh_from_db()
        
        self.assertEqual(self.draft_event_past.status, 'published')
        self.assertEqual(self.draft_event_future.status, 'draft')
        self.assertEqual(self.published_event.status, 'published')
        self.assertIn('Published 1 events', result)


    def test_generate_realistic_weather(self):
        """Тест генерации реалистичных данных погоды"""
        from events.tasks import generate_realistic_weather
        
        weather = generate_realistic_weather()
        
        self.assertIn('temperature', weather)
        self.assertIn('humidity', weather)
        self.assertIn('pressure', weather)
        self.assertIn('wind_direction', weather)
        self.assertIn('wind_speed', weather)
        
        # Проверка диапазонов
        self.assertGreaterEqual(weather['temperature'], -30)
        self.assertLessEqual(weather['temperature'], 40)
        self.assertGreaterEqual(weather['humidity'], 30)
        self.assertLessEqual(weather['humidity'], 100)
        self.assertGreaterEqual(weather['pressure'], 720)
        self.assertLessEqual(weather['pressure'], 780)
        self.assertGreaterEqual(weather['wind_speed'], 0)
        self.assertLessEqual(weather['wind_speed'], 20)