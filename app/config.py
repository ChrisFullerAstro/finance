import os
# Flask Config
UPLOAD_FOLDER = '/home/'
WTF_CSRF_ENABLED = True
SECRET_KEY = "84c203a1-ce62-43ea-9a44-3188cd022d1b"
DEBUG = True


#Mongo Finance Config
MONGO_PORT = 27017
MONGO_DBNAME = 'finance'
MONGO_HOST = "db"

#Mongo Config
MONGO2_PORT = 27017
MONGO2_DBNAME = 'config'
MONGO2_HOST = "db"
