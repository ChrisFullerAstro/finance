from data_manager import DataManager
from loaders import Loaders
from category_selector import Category_Selector

import sys
import logging
from pprint import pprint

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

def main(**kwargs):
    dm = DataManager()
    loaders = Loaders()
    category_selector = Category_Selector(dm)

    transactions = loaders.load_data(fname=kwargs['fname'], dtype=kwargs['dtype'])
    for transaction in transactions:
        pprint(category_selector.suggest_category(transaction))




if __name__ == "__main__":
    main(fname=sys.argv[1], dtype=sys.argv[2])
