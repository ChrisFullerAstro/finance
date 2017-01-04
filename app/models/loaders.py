#import modules
import numpy as np
import sys
import datetime
import os
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

def filter_dicts(objs, keys):
    temp=[]
    for obj in objs:
        logging.error('{0}'.format(str(obj)))
        fobj={}
        for k,v in obj.items():
            if k in keys:
                fobj[k] = v
        temp.append(fobj)
    return temp

def load_data(fname, dtype='barclays'):
    if dtype == 'barclays':
        logging.info('Using barclays loaders')
        return load_barclays(fname)
    else:
        logging.info('Using barclaycard loaders')
        return load_barclaycard(fname)


def load_barclays(fname):
    logging.info("Loading {0}".format(fname))
    with open(fname,errors="replace") as f:
        transactions=[]
        for line in f:
            if line.startswith('Number'): continue
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

def load_barclaycard(fname):
    raise NotImplementedError
