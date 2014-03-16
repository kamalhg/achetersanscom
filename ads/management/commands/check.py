from django.core.management.base import BaseCommand, CommandError
from ads.factories import AdFactory, SearchFactory, AccountFactory


class Command(BaseCommand):
    args = ''
    help = 'Should check for relations between ads and searches'

    def handle(self, *args, **options):
        pass
