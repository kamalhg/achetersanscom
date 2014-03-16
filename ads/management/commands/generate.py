from django.core.management.base import BaseCommand, CommandError
from ads.factories import AdFactory, SearchFactory, AccountFactory


class Command(BaseCommand):
    args = '<ads_number>'
    help = 'Generate random data for ads and search'

    def handle(self, *args, **options):
        number = 10
        if len(args) > 0:
            number = int(args[0])
        AccountFactory.create_batch(number)
        AdFactory.create_batch(number)
        SearchFactory.create_batch(number)
        self.stdout.write('Successfully generated items')
