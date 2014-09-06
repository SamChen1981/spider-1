#encoding=utf8
from spider.core.management.base import BaseCommand 
from spider.core.handlers.crawl import CRAWLHandler
class Command(BaseCommand):
    def handle(self, *args, **options):
        CRAWLHandler()
            