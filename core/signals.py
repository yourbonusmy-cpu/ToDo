from django.contrib.auth.hashers import make_password
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserPin


@receiver(post_save, sender=User)
def create_user_pin(sender, instance, created, **kwargs):
    if created:
        UserPin.objects.create(
            user=instance, pin_hash=make_password("0000"), is_pin_enabled=False
        )
