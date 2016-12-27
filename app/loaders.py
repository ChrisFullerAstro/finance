#import modules
import numpy as np
import sys
import datetime
import os
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

class Loaders:
    def __init__(self):
        pass

    def load_data(self,fname, dtype):
        if dtype == 'barclays':
            logging.info('Using barclays loaders')
            return self.load_barclays(fname)
        else:
            logging.info('Using barclaycard loaders')
            return self.load_barclaycard(fname)

    def load_barclays(self,fname):
        logging.info("Loading {0}".format(fname))
        with open(fname,errors="replace") as f:
            transactions=[]
            for line in f:
                line = line.lstrip(' ,').rstrip().split(',')

                payee = line[4].split()[0]
                if payee.strip(' ')=='':
                    payee = line[4]

                transactions.append({
                    'date':line[0],
                    'account':line[1],
                    'ammount':line[2],
                    'tag':line[3],
                    'comment':line[4],
                    'payee':payee
                })
        return transactions

    def load_barclaycard(self,fname):
        raise NotImplementedError
