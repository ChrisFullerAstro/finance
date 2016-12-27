# Load categories data into the mongo database
# Uses with python3 <input file>

from pymongo import MongoClient
import datetime
import sys
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

logging.info("Connecting to MongoDB.")
client = MongoClient('localhost', 5001)
db = client.config
db_collection = db.categories

logging.info("Opening file {0}".format(sys.argv[1]))
with open(sys.argv[1],errors='ignore') as ifile:
    data = set([x.rstrip() for x in ifile])
    data_dict = [{
        "main_category":x.split(',')[0],
        "sub_category":x.split(',')[1]}
        for x in data]

logging.info('Inserting {0} records into database.'.format(len(data)))
db_collection.insert_many(data_dict)
