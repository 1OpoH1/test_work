from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

from .models import Event, EventImage
from .serializers import EventSerializer, EventImageSerializer
from .permissions import IsSuperUser


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_permissions(self):
        """
        Только суперпользователь может создавать/изменять/удалять.
        Для чтения доступ открыт всем, но queryset фильтруется.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'upload_image']:
            permission_classes = [IsAuthenticated, IsSuperUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Суперпользователь видит все мероприятия.
        Остальные видят только опубликованные с датой публикации не позже текущего момента.
        """
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            return Event.objects.all()
        now = timezone.now()
        return Event.objects.filter(status='published', pub_datetime__lte=now)

    def perform_create(self, serializer):
        """Автором автоматически становится текущий пользователь (суперпользователь)."""
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Загрузка изображения для конкретного мероприятия."""
        event = self.get_object()
        file = request.FILES.get('image')
        if not file:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

        image = EventImage.objects.create(event=event, image=file)

        # Если у мероприятия ещё нет превью — генерируем его из первого загруженного изображения
        if not event.preview:
            self._generate_preview(event, file)

        serializer = EventImageSerializer(image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _generate_preview(self, event, image_file):
        """
        Создаёт превью 200px по наименьшей стороне и сохраняет в поле preview модели Event.
        """
        try:
            img = Image.open(image_file)
            # Определяем наименьшую сторону
            min_side = min(img.width, img.height)
            scale = 200 / min_side
            new_width = int(img.width * scale)
            new_height = int(img.height * scale)
            img = img.resize((new_width, new_height), Image.LANCZOS)

            # Сохраняем в буфер
            buffer = BytesIO()
            format = 'JPEG' if img.format == 'JPEG' else 'PNG'
            img.save(buffer, format=format)
            buffer.seek(0)

            # Сохраняем в поле preview
            filename = f"preview_{event.id}.{format.lower()}"
            event.preview.save(filename, ContentFile(buffer.read()), save=True)
        except Exception as e:
            # Логирование ошибки, но не прерываем загрузку изображения
            print(f"Error generating preview: {e}")