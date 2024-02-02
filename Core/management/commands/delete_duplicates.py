# delete_duplicates.py

from django.core.management.base import BaseCommand
from Core.crud import delete_duplicate_customers

class Command(BaseCommand):
    help = 'Deletes duplicate customer records'

    def handle(self, *args, **kwargs):
        delete_duplicate_customers()
        self.stdout.write(self.style.SUCCESS('Duplicate customer records deleted successfully'))
