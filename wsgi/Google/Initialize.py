#!/usr/bin/env python
import os
import csv
from pymongo import MongoClient

technical_dir  = "./dataset/Technical/"
medical_dir = "./dataset/Medical/"
sub_set = ("Software", "Hardware", "Internet")

key = "field"
value = "tags"

def read_data(file_path):
    # The file should be in csv format.
    csv_file = csv.reader(open(file_path, "rb")) 
    #header = csv_file.next()
    x = []
    for row in csv_file:
        x.append(row[0].lower())
    return x

client = MongoClient()
db = client.category_db
coll = db.docs
coll.drop()

docList = []
technical_other = []
for filename in os.listdir(technical_dir):
    if filename[:-4] in sub_set:
        current_dict = {key: filename[:-4]}
        current_dict[value]= read_data(technical_dir + filename)
        docList.append(current_dict)
    else:
        temp = read_data(technical_dir + filename)
        technical_other += temp

for filename in os.listdir(medical_dir):
    current_dict = {key: filename[:-4]}
    current_dict[value]= read_data(medical_dir + filename)
    docList.append(current_dict)

technical_other.sort()
current_dict = {key: "Technical_Other"}
current_dict[value]= technical_other
docList.append(current_dict)
coll.insert(docList)
coll.create_index(key)

print "Database Created!"

client.disconnect()

