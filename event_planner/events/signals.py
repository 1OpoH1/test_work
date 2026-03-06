from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Event
from .tasks import send_event_notification

@receiver(post_save, sender=Event)
def event_post_save(sender, instance, **kwargs):
    # Проверяем, изменился ли статус на 'published'
    if instance.status == 'published':
        # Чтобы избежать циклических вызовов, проверяем предыдущее состояние
        try:
            old = Event.objects.get(pk=instance.pk)
            if old.status == 'published':
                return
        except Event.DoesNotExist:
            pass
        # Отправляем уведомления
        recipient_list = getattr(settings, 'NOTIFICATION_EMAIL_LIST', [])
        if recipient_list:
            subject = f"Новое мероприятие: {instance.title}"
            message = (
                f"Опубликовано мероприятие: {instance.title}\n"
                f"Описание: {instance.description}\n"
                f"Дата начала: {instance.start_datetime}\n"
                f"Место: {instance.location.name if instance.location else 'Не указано'}"
            )
            send_event_notification.delay(instance.id, recipient_list, subject, message)