from django.core.management.base import BaseCommand
from django.core.cache import cache

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        cache.clear()
        print dir(cache)
        print 'Cleared cache\n'
