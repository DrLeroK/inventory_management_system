import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)
User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Creates a profile only if one doesn't exist
    (as a fallback for when users are created outside the form)
    """
    if created:
        try:
            instance.profile
        except ObjectDoesNotExist:
            from .models import Profile
            Profile.objects.create(user=instance)
            logger.info(f"Created fallback profile for user {instance.pk}")

@receiver(post_save, sender=User)
def sync_user_profile(sender, instance, created, **kwargs):
    """
    Syncs user data with profile (for existing users only)
    """
    if created:
        return
        
    try:
        profile = instance.profile
        if instance.email and not profile.email:
            profile.email = instance.email
            profile.save(update_fields=['email'])
    except ObjectDoesNotExist:
        pass