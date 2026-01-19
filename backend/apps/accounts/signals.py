from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, StaffProfile


@receiver(post_save, sender=User)
def create_staff_profile(sender, instance, created, **kwargs):
    """Create StaffProfile for staff users when created."""
    if created and instance.role != User.Role.GUEST:
        if not hasattr(instance, 'staff_profile'):
            StaffProfile.objects.create(
                user=instance,
                employee_id=f"EMP-{instance.pk:05d}"
            )
