from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from locations.factories import LocationFactory, SuperUserFactory, UserFactory
from events.models import Event, EventImage, WeatherData
from events.factories import EventFactory, PublishedEventFactory, WeatherDataFactory
import io
import openpyxl
from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
import PIL.Image
from io import BytesIO

class EventModelTest(APITestCase):
    def setUp(self):
        self.event = EventFactory()

    def test_event_creation(self):
        """Тест создания модели Event"""
        self.assertIsInstance(self.event, Event)
        self.assertEqual(str(self.event), self.event.title)

    def test_weather_data_creation(self):
        """Тест создания данных погоды"""
        weather = WeatherDataFactory(event=self.event)
        self.assertIsInstance(weather, WeatherData)
        self.assertEqual(weather.event, self.event)
        self.assertIsNotNone(weather.temperature)
        self.assertIsNotNone(weather.humidity)


class EventAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.superuser = SuperUserFactory()
        self.regular_user = UserFactory()
        self.token = Token.objects.create(user=self.superuser)
        self.list_url = reverse('event-list')
        
        # Создаем тестовые данные
        self.location = LocationFactory()
        self.published_event = PublishedEventFactory(
            location=self.location,
            pub_datetime=timezone.now() - timedelta(days=1)
        )
        self.draft_event = EventFactory(
            location=self.location,
            status='draft',
            pub_datetime=timezone.now() + timedelta(days=1)
        )

    def test_list_events_unauthenticated(self):
        """Неавторизованный пользователь видит только опубликованные мероприятия"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Учитываем пагинацию
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], self.published_event.title)

    def test_list_events_superuser(self):
        """Суперпользователь видит все мероприятия"""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 2)

    def test_create_event_superuser(self):
        """Суперпользователь может создать мероприятие"""
        self.client.force_authenticate(user=self.superuser)
        pub_dt = timezone.now()
        start_dt = timezone.now() + timedelta(days=1)
        end_dt = timezone.now() + timedelta(days=2)
        
        data = {
            'title': 'New Event',
            'description': 'Test Description',
            'pub_datetime': pub_dt.strftime('%Y-%m-%d %H:%M:%S'),
            'start_datetime': start_dt.strftime('%Y-%m-%d %H:%M:%S'),
            'end_datetime': end_dt.strftime('%Y-%m-%d %H:%M:%S'),
            'location': self.location.id,
            'rating': 15,
            'status': 'draft'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 3)

    def test_create_event_regular_user(self):
        """Обычный пользователь не может создать мероприятие"""
        self.client.force_authenticate(user=self.regular_user)
        pub_dt = timezone.now()
        start_dt = timezone.now() + timedelta(days=1)
        end_dt = timezone.now() + timedelta(days=2)
        
        data = {
            'title': 'New Event',
            'description': 'Test Description',
            'pub_datetime': pub_dt.strftime('%Y-%m-%d %H:%M:%S'),
            'start_datetime': start_dt.strftime('%Y-%m-%d %H:%M:%S'),
            'end_datetime': end_dt.strftime('%Y-%m-%d %H:%M:%S'),
            'location': self.location.id,
            'rating': 15
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class EventFilterTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = SuperUserFactory()
        self.client.force_authenticate(user=self.user)
        self.list_url = reverse('event-list')
        self.location1 = LocationFactory(name="Park")
        self.location2 = LocationFactory(name="Stadium")
        
        now = timezone.now()
        # Создаем мероприятия с разными параметрами
        self.event1 = EventFactory(
            title="Rock Concert",
            location=self.location1,
            rating=20,
            start_datetime=now + timedelta(days=1)
        )
        self.event2 = EventFactory(
            title="Jazz Festival",
            location=self.location2,
            rating=15,
            start_datetime=now + timedelta(days=5)
        )
        self.event3 = EventFactory(
            title="Art Exhibition",
            location=self.location1,
            rating=10,
            start_datetime=now + timedelta(days=10)
        )

    def test_search_by_title(self):
        """Поиск по названию"""
        response = self.client.get(self.list_url, {'search': 'Rock'})
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'Rock Concert')

    def test_filter_by_rating_range(self):
        """Фильтр по диапазону рейтинга"""
        response = self.client.get(self.list_url, {'rating_min': 12, 'rating_max': 18})
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'Jazz Festival')

    def test_filter_by_location(self):
        """Фильтр по месту проведения"""
        response = self.client.get(self.list_url, {'location': str(self.location1.id)})
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 2)
        titles = [event['title'] for event in data]
        self.assertIn('Rock Concert', titles)
        self.assertIn('Art Exhibition', titles)


class EventImageUploadTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.superuser = SuperUserFactory()
        self.client.force_authenticate(user=self.superuser)
        self.event = EventFactory()
        self.upload_url = reverse('event-upload-image', args=[self.event.id])

    def create_test_image(self):
        """Создание тестового изображения"""
        image = PIL.Image.new('RGB', (100, 100), color='red')
        output = BytesIO()
        image.save(output, format='JPEG')
        output.seek(0)
        return SimpleUploadedFile('test.jpg', output.read(), content_type='image/jpeg')

    def test_upload_image(self):
        """Тест загрузки изображения"""
        image_file = self.create_test_image()
        
        response = self.client.post(self.upload_url, {'image': image_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('image', response.data)
        self.assertEqual(EventImage.objects.count(), 1)
        
        self.event.refresh_from_db()
        self.assertIsNotNone(self.event.preview)