from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Har bir yangi User yaratilganda, unga avtomatik Profile biriktiradi.
    """
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()