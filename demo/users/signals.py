# users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile, Transaction
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        Transaction.objects.create(user=instance)
