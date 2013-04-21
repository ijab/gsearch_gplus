#!/usr/bin/env python
import re
import os
from pymongo import MongoClient


key = "field"
value = "tags"

field_list = ["Software", "Hardware", "Internet", "Technical_Other", "Medical"]
Technical_Set = {"Software", "Hardware", "Internet", "Technical_Other"}

ip = os.environ['OPENSHIFT_INTERNAL_IP']
port = 27017

def connect_database():
    client = MongoClient(ip, port)
    db = client.category_db
    db.authenticate('ijab', 'ijab')
    coll = db.docs
    return coll

def get_field_by_term(term, coll):
    term = term.lower()
    for doc in coll.find({value: term}):
        return doc[key]
    return None

def get_fields_by_term(term, coll):
    term = term.lower()
    fields = []
    for doc in coll.find({value: {'$regex': term}}):
        fields.append(doc[key])
    return fields

def get_field_by_tf(tf_dict):
    coll = connect_database()
    score = {}
    for field in field_list:
        score[field] = 0.0
    for tf in tf_dict.items():
        #print tf[0] + "-------"
        field = get_field_by_term(tf[0], coll)
        if field == None:
            fields = get_fields_by_term(tf[0], coll)
            for field in fields:
                score[field] += (0.707 / len(fields)) * tf[1]
        else:
            score[field] += 1.0 * tf[1]
        #print score
    return max(score, key = score.get)

def get_field_by_query(query):
    coll = connect_database()
    score = {}
    for field in field_list:
        score[field] = 0.0
    for term in query.split():
        field = get_field_by_term(term, coll)
        if field == None:
            fields = get_fields_by_term(term, coll)
            for field in fields:
                score[field] += 0.707 / len(fields)
        else:
            score[field] += 1.0
    return max(score, key = score.get)

def get_relavance(f1, f2):
    if f1 == f2:
        return 1.0
    elif (f1 in Technical_Set) and (f2 in Technical_Set):
        return 0.5
    else:
        return 0.0

def get_url_by_field(field, query=""):
    url = {
        'Software': 'http://www.verticalsearch.com/search.jsp?js=true&category=11&x=0&y=0&keywords=',
        'Hardware': 'http://hardwarenews-info.com/?s=',
        'Internet': 'http://www.verticalsearch.com/search.jsp?js=true&category=9&x=51&y=17&keywords=',
        'Technical_Other': 'http://www.verticalsearch.com/search.jsp?category=12&x=37&y=11&js=true&keywords=',
        'Medical': 'http://www.verticalsearch.com/search.jsp?category=6&x=0&y=0&js=true&keywords='
        }.get(field, 'http://www.google.com/search?hl=en&q=')
    if query:
        url += query
    return url

if __name__ == '__main__':
    tf_dict = {"Software": 1.2, "Hardware": 0.6, "Back": 1.0, "Bitmap": 50.0}
    print get_field_by_tf(tf_dict)
    print get_field_by_query("Internet overflow")
    print get_url_by_field("medical", 'Hardware')



