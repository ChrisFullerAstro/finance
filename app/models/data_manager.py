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
        self.categories_db = self.client.config.categories
        self.categories = self.__update_categories()
        self.processtransactions = self.client.finance.processtransactions
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

    def __update_categories(self):
        return [x['sub_category'] for x in self.categories_db.find({})]


    def __index_mongo(self):
        self.client.finance.master.create_index([('comment', ASCENDING)])

    def load_input_data(self,fname):
        l=loaders.Loaders()
        logging.info('Loading data into data manager')
        self.input_data = l.load_data(fname)

    def save_transactions_bulk(self, transactions):
        self.processtransactions.insert_many(transactions)

    def save_transaction(self, transaction):
        self.processtransactions.insert_one(transaction)
