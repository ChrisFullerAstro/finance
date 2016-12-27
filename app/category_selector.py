from collections import Counter

THRESHOLD=1.0

class Category_Selector(object):
    """docstring for Category_Selector."""
    def __init__(self, dm):
        self.dm = dm

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

        # Check if already indexed
        results = self.is_exact_match(transaction['comment'])

        if True in [x['likelyhood']>=THRESHOLD for x in results]:
            transaction.update({'suggestions':results})
            return transaction

        # Compute levenshtein distance and make array of suggestions
        
