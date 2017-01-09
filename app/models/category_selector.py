from collections import Counter
import numpy as np
import logging
import editdistance
import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')

DEFULT_CATS = [
'House + Baby',
'House + Giving',
'House + Groceries',
'House + Home Improvements',
'House + Medical',
'House + Monthlys',
'House + Other',
'House + Subscriptions - TV/Audio',
'Income + Financial Gift',
'Income + Other',
'Income + Salarys',
'Leisure + Amazon',
'Leisure + Chris Personal',
'Leisure + Clothing',
'Leisure + Entertainment',
'Leisure + Esther Personal',
'Leisure + Gifts',
'Leisure + Holidays',
'Leisure + Leisure Other',
'Other + Fees',
'Other + Other',
'Other + Work Expenses',
'Transfer + Transfer',
'Travel + Car Annuals',
'Travel + Fuel',
'Travel + Other',
'Travel + Train Tickets'
]

def get_config(db):
    config_data = [x for x in db.find().sort('timestamp',DESCENDING).limit(1)]

    if config_data == []:
        config_data = {
        "SIMILARITY_THRESHOLD" : 0.1,
        "timestamp": int(datetime.datetime.utcnow().strftime('%s'))
        }

        update_config(db, config_data)
    else:
        config_data = config_data[0]

    if config_data.get('_id') != None:
        del config_data['_id']

    return config_data

def update_config(db, data):
    data['timestamp'] = int(datetime.datetime.utcnow().strftime('%s'))
    try:
        db.insert_one(data)
    except Exception as e:
        logging.error(e)

def get_categorys(db):
    cats_dict = [x for x in db.find({})]
    if cats_dict == []:
        cats_lst = DEFULT_CATS
        update_categorys(db, [{'sub_category':x} for x in cats_lst])
        return sorted(cats_lst)
    return [x["sub_category"] for x in cats_dict]

def update_categorys(db, data):
    for doc in data:
        if db.find_one(doc)!=None:
            pass
        else:
            db.insert_one(doc)

def distance_to_all_stored_comments(target,data):

        distances = [{
            'distance':editdistance.eval(target,x['comment']),
            'category':x['category']}
            for x in data]

        res=[]
        simalarties=[]
        length = len(target)
        for obj in sorted(distances, key=lambda x: x['distance']):
            if obj['category'] not in res:
                #temp.append(obj)
                simalarties.append(obj['distance']/float(length))
                res.append(obj['category'])
        return res, simalarties

def suggest_category(transaction, config, db=None, data=None):
    logging.debug('Suggesting category for: {0}'.format(transaction['comment']))

    if data==None:
        data=[x for x in db.find({})]

    if db!=None and db.find_one()==None:
        logging.info('No Transactions found in processtransactions skipping suggest_category')
        transaction.update({'suggestions':[None]})
        return transaction, False

    # Compute levenshtein distance and make array of suggestions
    categories, simalarties = distance_to_all_stored_comments(transaction['comment'], data)

    transaction.update({'suggestions':categories})

    if simalarties[0] <= config['SIMILARITY_THRESHOLD']:
        return transaction, True

    return transaction, False
