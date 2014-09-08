#encoding=utf8
from spider.core.management.base import BaseCommand 
from spider.core.handlers.crawl import CRAWLHandler
class Command(BaseCommand):
    def create_parser(self, prog_name, subcommand):
        parser=super(Command,self).create_parser(prog_name, subcommand)
        
        parser.add_option("-t","--spidername",action="store",type="string",dest="spidername")
        
        return parser
    
    def handle(self, *args, **options):
        
        CRAWLHandler(options['spidername'])
            