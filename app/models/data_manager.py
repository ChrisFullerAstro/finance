from pymongo import MongoClient, ASCENDING, DESCENDING
import datetime
import sys
import logging
from collections import Counter
import time
from models import loaders
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

class DummyDataManager:
    def __init__(self):

        self.require_user_class =[
            {'comment': 'Surfing Shop', 'suggestions:': ['Leisure + Entertainment', 'House + Groceries'], 'tag': 'PAYMENT', 'ammount': '-1000.0', 'account': '20-60-64 13010430', 'payee': 'surf', 'date': '09/12/2016'},
            {'comment': 'Coffee Shop', 'suggestions:': ['Leisure + Entertainment', 'House + Groceries'], 'tag': 'PAYMENT', 'ammount': '-100.0', 'account': '20-60-64 13010430', 'payee': 'coffee#2', 'date': '10/12/2016'},
            {'comment': 'Baby Shop', 'suggestions:': ['Leisure + Entertainment', 'House + Groceries'], 'tag': 'PAYMENT', 'ammount': '-10.0', 'account': '20-60-64 13010430', 'payee': 'babysrus', 'date': '11/12/2016'}
                    ]
        self.classfied=[]
        self.current_transaction = None

    def get_new_transaction(self):
        try:
            self.current_transaction = self.require_user_class.pop(0)
        except IndexError:
            self.current_transaction = None

class DataManager(object):
    """docstring for DataManager"""
    def __init__(self):

        self.__connect_to_mongo()
        self.__index_mongo()
        self.master = self.client.finance.master
        self.categories_db = self.client.config.categories
        self.categories = self.__update_categories()
        self.cs_config = self.client.config.cs_config
        self.processtransactions = self.client.finance.processtransactions
        self.input_data = None
        self.automatic_classfied = []
        self.users_input_required = []
        self.classfied=[]
        self.current_transaction = None

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

    def get_new_transaction(self):
        try:
            self.current_transaction = self.users_input_required.pop(0)
        except:
            self.current_transaction = None

    def load_input_data(self,fname):
        l=loaders.Loaders()
        logging.info('Loading data into data manager')
        self.input_data = l.load_data(fname)

    def save_transactions_bulk(self, transactions):
        self.processtransactions.insert_many(transactions)

    def save_transaction(self, transaction):
        self.processtransactions.insert_one(transaction)

    def load_current_transactions(self):
        data = [x for x in self.processtransactions.find({})]
        #data = [x for x in self.master.find({})]
        logging.info('Returned {0} transactions from database'.format(len(data)))
        return data

    # def get_cs_config(self):
    #     return [x for x in self.dm.cs_config.find({})]
