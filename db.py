from pymongo import MongoClient
import gridfs
import pandas as pd
import json

client= MongoClient("mongodb://localhost:27017")

db=client['Registration']
collection=db['User_detatails']



def upload_file(fs,data,name):
    fs.put(data,filename = name)

