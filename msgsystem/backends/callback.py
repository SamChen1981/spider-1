
import json

from spider.utils.log import logger


class StartFuture(object):
    def __init__(self, _process):
        self._process = _process

    def callback(self, ch, method, properties, body):
        logger.info(" [x] Received %r" % (body,))
        urlpack = body
        if not urlpack:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        packed = json.loads(urlpack)
        self._process(packed)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(" [x] Done")
