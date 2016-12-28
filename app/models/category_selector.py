from collections import Counter
import numpy as np

import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')


class Category_Selector(object):
    """docstring for Category_Selector."""
    def __init__(self, dm):
        self.dm=dm
        self.THRESHOLD_ACCEPT_LIKELYHOOD_EM=0.1
        self.THRESHOLD_ACCEPT_LIKELYHOOD_LD=0.1
        self.THRESHOLD_ACCEPT_DISTANCE=50.0

    def _likelyhood_matches(self,x):
        likelyhoods = [{'category':c, 'likelyhood':x.count(c)/float(len(x))}
                        for c in set(x)]
        return likelyhoods

    def is_exact_match(self, comment):
        matches = [
            x['category'] for
            x in self.dm.master.find({"comment":comment})]

        if len(matches)==0:
            return []
        elif len(matches)>0:
            return self._likelyhood_matches(matches)
        else:
            raise Exception('Error with exact match')

    def suggest_category(self, transaction):
        logging.debug('Suggesting category for: {0}'.format(transaction['comment']))

        # Check if already indexed
        results_em = self.is_exact_match(transaction['comment'])

        logging.debug('Checking if an exact match exists')
        # Check if more than one that the likelyhood is greater than THRESHOLD_ACCEPT_LIKELYHOOD
        results_em_gt_threshold = [x for x in results_em
            if x['likelyhood']>=self.THRESHOLD_ACCEPT_LIKELYHOOD_EM]

        if results_em_gt_threshold != []:
            logging.debug('{0} categorys found that are an exact match'.format(len(results_em_gt_threshold)))
            category_top = sorted(results_em_gt_threshold,
                                key=lambda x:-x['likelyhood'])[0]

            transaction.update({'category':category_top['category']})
            return True,transaction

        logging.debug('No exact match found, computing levenshtein distances')

        # Compute levenshtein distance and make array of suggestions
        results_ld = self._distance_to_all_stored_comments(transaction['comment'])

        min_distance = min([x['distance'] for x in results_ld])
        logging.debug('{0} = Min distance'.format(min_distance))

        # Check if more than one that the likelyhood is greater than THRESHOLD_ACCEPT_DISTANCE
        if min_distance <= self.THRESHOLD_ACCEPT_DISTANCE:
            logging.debug('Min distance less than THRESHOLD_ACCEPT_DISTANCE')
            top_categorys = [x['category'] for x in results_ld if x['distance'] == min_distance]

            results_lm_with_lh = self._likelyhood_matches(top_categorys)

            # Check if more than one that the likelyhood is greater than THRESHOLD_ACCEPT_LIKELYHOOD
            results_lm_gt_threshold = [x for x in results_lm_with_lh
                if x['likelyhood']>=self.THRESHOLD_ACCEPT_LIKELYHOOD_LD]

            if results_lm_gt_threshold != []:
                logging.debug('{0} Categoryies exist above THRESHOLD_ACCEPT_LIKELYHOOD_LD'.format(len(results_lm_gt_threshold)))
                category_top = sorted(results_lm_gt_threshold,
                                    key=lambda x:-x['likelyhood'])[0]

                transaction.update({'category':category_top['category']})
                return True,transaction

        #no automatic category found request user selection
        logging.debug('No category found submitting best suggestions to user')
        best = sorted(results_ld,
                            key=lambda x:x['distance'])[:4]

        transaction.update({'suggestions:':[x['category'] for x in best]})
        return False, transaction



    def _distance_to_all_stored_comments(self,target):
        distances = [{
            'distance':self._levenshtein(target,x['comment']),
            'category':x['category']}
            for x in self.dm.master.find({})]
        return distances


    def _levenshtein(self, source, target):
        if len(source) < len(target):
            return self._levenshtein(target, source)

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
