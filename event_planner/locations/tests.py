from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from .models import Location
from .factories import LocationFactory, SuperUserFactory, UserFactory

class LocationModelTest(APITestCase):
    def setUp(self):
        self.location = LocationFactory()

    def test_location_creation(self):
        """Тест создания модели Location"""
        self.assertIsInstance(self.location, Location)
        # Проверяем, что строковое представление - это название
        self.assertEqual(str(self.location), self.location.name)
        self.assertIsNotNone(self.location.latitude)
        self.assertIsNotNone(self.location.longitude)
        self.assertIsNotNone(self.location.created_at)
        self.assertIsNotNone(self.location.updated_at)


class LocationAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.superuser = SuperUserFactory()
        self.regular_user = UserFactory()
        self.token = Token.objects.create(user=self.superuser)
        self.list_url = reverse('location-list')

    def test_list_locations_unauthenticated(self):
        """Неавторизованный пользователь не должен видеть локации"""
        response = self.client.get(self.list_url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_list_locations_regular_user(self):
        """Обычный пользователь не должен видеть локации"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_locations_superuser(self):
        """Суперпользователь должен видеть локации"""
        self.client.force_authenticate(user=self.superuser)
        # Создаём 3 локации с разными именами
        locations = LocationFactory.create_batch(3)
        
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Учитываем пагинацию
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 3)
        
        # Проверяем, что имена соответствуют
        for i, location in enumerate(locations):
            self.assertEqual(data[i]['name'], location.name)

    def test_create_location_superuser(self):
        """Суперпользователь может создать локацию"""
        self.client.force_authenticate(user=self.superuser)
        data = {
            'name': 'Test Location',
            'latitude': 55.7558,
            'longitude': 37.6176
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Location.objects.count(), 1)
        
        # Проверяем созданную локацию
        location = Location.objects.first()
        self.assertEqual(location.name, 'Test Location')
        self.assertEqual(float(location.latitude), 55.7558)
        self.assertEqual(float(location.longitude), 37.6176)

    def test_create_location_regular_user(self):
        """Обычный пользователь не может создать локацию"""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'name': 'Test Location',
            'latitude': 55.7558,
            'longitude': 37.6176
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_update_location(self):
        """Тест обновления локации"""
        self.client.force_authenticate(user=self.superuser)
        location = LocationFactory()
        url = reverse('location-detail', args=[location.id])
        data = {'name': 'Updated Name'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        location.refresh_from_db()
        self.assertEqual(location.name, 'Updated Name')

    def test_delete_location(self):
        """Тест удаления локации"""
        self.client.force_authenticate(user=self.superuser)
        location = LocationFactory()
        url = reverse('location-detail', args=[location.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Location.objects.count(), 0)