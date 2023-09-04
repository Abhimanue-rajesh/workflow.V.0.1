from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Staff

@receiver(pre_delete, sender=Staff)
def delete_staff_user(sender, instance, **kwargs):
    user = instance.user
    user.delete()