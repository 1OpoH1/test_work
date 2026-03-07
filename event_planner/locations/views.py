from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Location
from .serializers import LocationSerializer
from .permissions import IsSuperUser

class LocationViewSet(viewsets.ModelViewSet):
    """
    CRUD для мест проведения. Доступ только суперпользователю.
    """
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated, IsSuperUser]  # требует аутентификации и прав суперпользователя