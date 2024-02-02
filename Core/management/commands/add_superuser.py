from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    """
    Command to create superuser with username and password

    Arguments:
        email: email of the superuser (optional, default: admin@cryptbee.com)
        password: password of the superuser (optional, default: cryptbee)

    Usage:
        python manage.py add_superuser --email <email> --password <password>
    """

    help = 'Create superuser with username and password'

    def handle(self, *args, **kwargs):
        """Function to create superuser with username and password"""
        # reading email and password from the command line arguments
        username = kwargs.get('username', 'admin')
        email = kwargs.get('email', 'admin@admin.com')
        password = kwargs.get('password', 'admin')

        # checking if the user with the given email already exists
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR('User with this email already exists'))
            return

        # creating the superuser
        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(
            self.style.SUCCESS(
                'Superuser created successfully'
                )
            )