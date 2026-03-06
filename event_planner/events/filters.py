# events/filters.py
import django_filters
from .models import Event
from locations.models import Location

class EventFilter(django_filters.FilterSet):
    # Фильтры по диапазону дат начала
    start_datetime_from = django_filters.DateTimeFilter(field_name='start_datetime', lookup_expr='gte')
    start_datetime_to = django_filters.DateTimeFilter(field_name='start_datetime', lookup_expr='lte')

    # Фильтры по диапазону дат завершения
    end_datetime_from = django_filters.DateTimeFilter(field_name='end_datetime', lookup_expr='gte')
    end_datetime_to = django_filters.DateTimeFilter(field_name='end_datetime', lookup_expr='lte')

    # Фильтр по месту проведения (множественный выбор)
    location = django_filters.ModelMultipleChoiceFilter(
        field_name='location',
        queryset=Location.objects.all(),
        label='Место проведения (можно выбрать несколько)'
    )

    # Фильтр по рейтингу (диапазон)
    rating_min = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    rating_max = django_filters.NumberFilter(field_name='rating', lookup_expr='lte')

    class Meta:
        model = Event
        fields = []