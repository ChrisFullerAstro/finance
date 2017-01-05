from collections import Counter
import numpy as np
import logging
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
        "THRESHOLD_ACCEPT_LIKELYHOOD_EM" : 0.8,
        "THRESHOLD_ACCEPT_LIKELYHOOD_LD" : 0.8,
        "THRESHOLD_ACCEPT_DISTANCE" : 10.0,
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

def levenshtein(source, target):
    if len(source) < len(target):
        return levenshtein(target, source)

    # So now we have len(source) >= len(target).
    if len(target) == 0:
        return len(source)

    # We call tuple() to force strings to be used as sequences
    # ('c', 'a', 't', 's') - numpy uses them as values by default.
    source = np.array(tuple(source))
    target = np.array(tuple(target))

    # We use a dynamic programming algorithm, but with the
    # added optimization that we only need the last two rows
    # of the matrix.
    previous_row = np.arange(target.size + 1)
    for s in source:
        # Insertion (target grows longer than source):
        current_row = previous_row + 1

        # Substitution or matching:
        # Target and source items are aligned, and either
        # are different (cost of 1), or are the same (cost of 0).
        current_row[1:] = np.minimum(
                current_row[1:],
                np.add(previous_row[:-1], target != s))

        # Deletion (target grows shorter than source):
        current_row[1:] = np.minimum(
                current_row[1:],
                current_row[0:-1] + 1)

        previous_row = current_row

    return previous_row[-1]

def distance_to_all_stored_comments(target,db):
        distances = [{
            'distance':levenshtein(target,x['comment']),
            'category':x['category']}
            for x in db.find({})]
        return distances

def is_exact_match(comment, db):
    matches = [
        x['category'] for
        x in db.find({"comment":comment})]

    if len(matches)==0:
        return []
    elif len(matches)>0:
        return likelyhood_matches(matches)
    else:
        raise Exception('Error with exact match')

def likelyhood_matches(x):
        likelyhoods = [{'category':c, 'likelyhood':x.count(c)/float(len(x))}
                        for c in set(x)]
        return likelyhoods

def suggest_category(transaction, config, db):
    if db.find_one()==None:
        return False
        logging.debug('Suggesting category for: {0}'.format(transaction['comment']))

        # Check if already indexed
        results_em = is_exact_match(transaction['comment'], db)

        logging.debug('Checking if an exact match exists')
        # Check if more than one that the likelyhood is greater than THRESHOLD_ACCEPT_LIKELYHOOD
        results_em_gt_threshold = [x for x in results_em
            if x['likelyhood']>=config['THRESHOLD_ACCEPT_LIKELYHOOD_EM']]

        if results_em_gt_threshold != []:
            logging.debug('{0} categorys found that are an exact match'.format(len(results_em_gt_threshold)))
            category_top = sorted(results_em_gt_threshold,
                                key=lambda x:-x['likelyhood'])[0]

            transaction.update({'category':category_top['category']})
            return True,transaction

        logging.debug('No exact match found, computing levenshtein distances')

        # Compute levenshtein distance and make array of suggestions
        results_ld = distance_to_all_stored_comments(transaction['comment'], db)

        min_distance = min([x['distance'] for x in results_ld])
        logging.debug('{0} = Min distance'.format(min_distance))

        # Check if more than one that the likelyhood is greater than THRESHOLD_ACCEPT_DISTANCE
        if min_distance <= config['THRESHOLD_ACCEPT_DISTANCE']:
            logging.debug('Min distance less than THRESHOLD_ACCEPT_DISTANCE')
            top_categorys = [x['category'] for x in results_ld if x['distance'] == min_distance]

            results_lm_with_lh = likelyhood_matches(top_categorys)

            # Check if more than one that the likelyhood is greater than THRESHOLD_ACCEPT_LIKELYHOOD
            results_lm_gt_threshold = [x for x in results_lm_with_lh
                if x['likelyhood']>=config['THRESHOLD_ACCEPT_LIKELYHOOD_LD']]

            if results_lm_gt_threshold != []:
                logging.debug('{0} Categoryies exist above THRESHOLD_ACCEPT_LIKELYHOOD_LD'.format(len(results_lm_gt_threshold)))
                category_top = sorted(results_lm_gt_threshold,
                                    key=lambda x:-x['likelyhood'])[0]

                transaction.update({'category':category_top['category']})
                return True,transaction

        #no automatic category found request user selection
        logging.debug('No category found submitting best suggestions to user')
        best = sorted(results_ld,
                            key=lambda x:x['distance'])#[:4]

        suggestions=[]
        for x in best:
            if x['category']  not in suggestions:
                suggestions.append(x['category'])

        transaction.update({'suggestions':suggestions})
        return False, transaction

def suggest_categoies_bulk(transactions, config, db):

        ts=[suggest_category(x, config, db) for x in transactions]

        users_input_required = [t for ui,t in ts if not ui]
        automatic_classfied = [t for ui,t in ts if ui]

        logging.info('{0} Require User Classfication'.format(len(users_input_required)))
        logging.info('{0} Automatic Classfication'.format(len(automatic_classfied)))
        return automatic_classfied, users_input_required
