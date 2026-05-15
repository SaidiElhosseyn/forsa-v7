"""
python manage.py create_admin
Reads ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_USERNAME from environment.
Safe to run multiple times — skips if user already exists.
"""
import os
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create default admin user from environment variables'

    def handle(self, *args, **options):
        from accounts.models import User

        username = os.environ.get('ADMIN_USERNAME', 'admin')
        email    = os.environ.get('ADMIN_EMAIL', 'admin@forsa.dz')
        password = os.environ.get('ADMIN_PASSWORD', '')

        if not password:
            self.stdout.write(self.style.WARNING('[skip] ADMIN_PASSWORD not set — skipping admin creation.'))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'[skip] User "{username}" already exists.'))
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            role='admin',
        )
        self.stdout.write(self.style.SUCCESS(f'[OK] Admin user "{username}" created.'))
