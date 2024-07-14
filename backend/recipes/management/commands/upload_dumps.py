from os import system

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting upload process...'))
        system('python manage.py loaddata ingredients.json')
        system('python manage.py loaddata tags.json')
        self.stdout.write(self.style.SUCCESS('Finished upload process.'))
