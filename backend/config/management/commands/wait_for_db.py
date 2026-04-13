"""
Django management command to wait for database availability.
"""
import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Wait for database to be available."""

    help = 'Wait for database to be available'

    def handle(self, *args, **options):
        """Handle the command."""
        self.stdout.write('Waiting for database...')
        db_conn = None
        retries = 30
        
        for i in range(retries):
            try:
                db_conn = connections['default']
                db_conn.cursor()
                break
            except OperationalError:
                self.stdout.write(
                    f'Database unavailable, waiting 1 second... ({i+1}/{retries})'
                )
                time.sleep(1)
        
        if db_conn:
            self.stdout.write(self.style.SUCCESS('Database available!'))
        else:
            self.stdout.write(
                self.style.ERROR(f'Database unavailable after {retries} attempts')
            )
            raise OperationalError('Could not connect to database')
