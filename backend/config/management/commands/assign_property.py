from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.properties.models import Property


class Command(BaseCommand):
    help = 'Assign the first property to all users who have no assigned_property'

    def handle(self, *args, **kwargs):
        p = Property.objects.first()
        if not p:
            self.stdout.write(self.style.ERROR('No properties found in database.'))
            return
        self.stdout.write(f'Using property: [{p.id}] {p.name}')
        fixed = 0
        for u in User.objects.filter(assigned_property__isnull=True):
            u.assigned_property = p
            u.save(update_fields=['assigned_property'])
            self.stdout.write(f'  Fixed: {u.email} ({u.role})')
            fixed += 1
        if fixed == 0:
            self.stdout.write(self.style.SUCCESS('All users already have an assigned property.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Done: assigned property to {fixed} user(s).'))
