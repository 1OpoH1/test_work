import factory
from django.utils import timezone
from events.models import Event, EventImage, WeatherData
from locations.factories import LocationFactory, UserFactory

class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event
    
    title = factory.Sequence(lambda n: f'Event {n}')
    description = factory.Faker('text', max_nb_chars=200)
    pub_datetime = factory.LazyFunction(timezone.now)
    start_datetime = factory.LazyFunction(lambda: timezone.now() + timezone.timedelta(days=1))
    end_datetime = factory.LazyFunction(lambda: timezone.now() + timezone.timedelta(days=2))
    author = factory.SubFactory(UserFactory)
    location = factory.SubFactory(LocationFactory)
    rating = factory.Faker('random_int', min=0, max=25)
    status = 'draft'

class PublishedEventFactory(EventFactory):
    status = 'published'

class WeatherDataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WeatherData
    
    event = factory.SubFactory(EventFactory)
    temperature = factory.Faker('pyfloat', min_value=-30, max_value=40, right_digits=1)
    humidity = factory.Faker('random_int', min=30, max=100)
    pressure = factory.Faker('random_int', min=720, max=780)
    wind_direction = factory.Faker('random_element', elements=[code for code, _ in WeatherData.WIND_DIRECTION_CHOICES])
    wind_speed = factory.Faker('pyfloat', min_value=0, max_value=20, right_digits=1)