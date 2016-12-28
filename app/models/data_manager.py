from pymongo import MongoClient, ASCENDING
import datetime
import sys
import logging
from collections import Counter
import time
from models import loaders
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')


class DataManager(object):
    """docstring for DataManager"""
    def __init__(self):

        self.__connect_to_mongo()
        self.__index_mongo()
        self.master = self.client.finance.master
        self.input_data = None

    def __connect_to_mongo(self):
        while True:
            try:
                client = MongoClient('localhost', 5001, serverSelectionTimeoutMS=500)
                res=client.server_info()
                logging.info('Connected to MongoDB successfully.')
                break
            except Exception as e:
                logging.error('Failed to MongoDB sleeping for 10 seconds.')
                time.sleep(10)
        self.client = client

    def __index_mongo(self):
        self.client.finance.master.create_index([('comment', ASCENDING)])

    def load_input_data(self,fname):
        l=loaders.Loaders()
        logging.info('Loading data into data manager')
        self.input_data = l.load_data(fname)
