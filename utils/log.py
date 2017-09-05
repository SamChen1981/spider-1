import logging


FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(level="INFO", format=FORMAT)

logger = logging.getLogger(__name__)
