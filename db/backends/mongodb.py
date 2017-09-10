# encoding=utf8

import logging
from pymongo import MongoClient

LOG = logging.getLogger(__name__)

uri = "mongodb://user:password@example.com/default_db?authSource=admin"


class MongoDBStorage(object):
    def __init__(self):
        """初始化mongodb

        """
        self.client = MongoClient()

    def save(self, content, **kwargs):
        """保存json数据到mongodb"""
        if not content:
            return
        db = kwargs["db"]
        collection = kwargs["collection"]
        if isinstance(content, list):
            obj_ids = self.client[db][collection].insert_many(
                content).inserted_ids
            LOG.info("save content to mongodb: {0}".format(obj_ids))
            return obj_ids
        elif isinstance(content, dict):
            obj_id = self.client[db][collection].insert_one(
                content).inserted_id
            LOG.info("save content to mongodb: {0}".format(obj_id))
            return obj_id
        else:
            return
