#set indexes

from pymongo import MongoClient, ASCENDING

client = MongoClient('localhost', 5001)

client.finance.exact_matches.create_index([('comment', ASCENDING)])
client.finance.suggestions.create_index([('comment', ASCENDING)])
client.finance.master.create_index([('comment', ASCENDING)])
