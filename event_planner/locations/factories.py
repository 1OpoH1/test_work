# locations/factories.py

import factory
from django.contrib.auth.models import User
from locations.models import Location

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    is_active = True

class SuperUserFactory(UserFactory):
    is_superuser = True
    is_staff = True

class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location
    
    name = factory.Sequence(lambda n: f'Location {n}')
    latitude = factory.Faker('latitude')
    longitude = factory.Faker('longitude')