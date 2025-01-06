from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import CustomUser
from .models import StoreProfile

@receiver(post_save, sender=CustomUser)
def create_store_profile(sender, instance, created, **kwargs):
    # If the user type changes to 'store' and no StoreProfile exists
    if instance.user_type == 'store' and not hasattr(instance, 'store_profile'):
        StoreProfile.objects.create(user=instance)