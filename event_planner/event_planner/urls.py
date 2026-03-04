from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/', include('locations.urls')),
    path('api-auth/', include('rest_framework.urls')),  # для удобного входа в браузере
]
