from collections import Counter

class Category_Selector(object):
    """docstring for Category_Selector."""
    def __init__(self, dm):
        self.dm = dm

    def is_exact_match(self, comment):
        matches = [
            x['category'] for
            x in self.dm.master.find({"comment":comment})]

        if len(matches)==0:
            return {'category':None, 'likelyhood':0.0}

        elif len(matches)==1:
            return {'category':matches[0], 'likelyhood':100.0}

        elif len(matches)>=2:
            data = Counter(matches)
            top_category = data.most_common(1)[0][0]
            result = {
                'category':matches[0],
                'likelyhood':matches.count(top_category)*100./len(matches)
                    }
            return result

        else:
            raise Exception('Error with exact match')

    def suggest_category(self, transaction):

        # Check if already indexed
        result = self.is_exact_match(transaction['comment'])

        if result['likelyhood']==100.:
            transaction.update(result)
            return transaction

        else:
            pass
            # Compute levenshtein distance and make array of suggestions
