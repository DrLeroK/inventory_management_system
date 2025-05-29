from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Purchase

@receiver(post_save, sender=Purchase)
def update_item_quantity_on_purchase(sender, instance, created, **kwargs):
    """
    Automatically increases item stock when a new Purchase is created.
    """
    if created and instance.status == 'D':  # Only delivered stock should be added
        item = instance.item
        item.quantity += instance.quantity
        item.save()
