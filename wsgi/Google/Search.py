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
##    client = MongoClient()
    client = MongoClient(ip, port)
    db = client.category_db
    db.authenticate('ijab', 'ijab')
    coll = db.docs
    return coll

##def get_field_by_term(term, coll):
##    term = term.lower()
##    fields = []
##    for doc in coll.find({value: term}):
##        fields.append(doc[key])
##    if len(fields) > 0:
##        return fields
##    else:
##        return None

def get_fields_by_term(term, coll):
    term = term.lower()
    fields = []
    for doc in coll.find({value: term}):
        fields.append(doc[key])
    if len(fields) > 0:
        return (True, fields)
    else:
        for doc in coll.find({value: {'$regex': term}}):
            fields.append(doc[key])
        return (False, fields)


def get_field_by_tf(tf_dict):
    coll = connect_database()
    score = {}
    for field in field_list:
        score[field] = 0.0
    for tf in tf_dict.items():
        #print tf[0] + "-------"
        (flag, fields) = get_fields_by_term(tf[0], coll)
        #print fields
        if len(fields) > 0:
            para = 0.707
            if flag:
                para = 1.0
            for field in fields:
                score[field] += (para / len(fields)) * tf[1]
        else:
            return "Unknown"
        #print score
    return max(score, key = score.get)

def get_field_by_query(query, field):
    coll = connect_database()
    score = {}
    for each_field in field_list:
        score[each_field] = 0.0
        
    for term in query.split():
        (flag, fields) = get_fields_by_term(term, coll)
        if len(fields) > 0:
            para = 0.707
            if flag:
                para = 1.0
            for each_field in fields:
                score[each_field] += para / len(fields)
    #print score
    rankList = [k for k,v in sorted(score.items(), key=lambda item: item[1], reverse=True)]
    for i in range(0,3):
        if rankList[i] == field:
            return field
    return rankList[0]

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
    tf_dict = {"Software": 4.2, "Hardware": 0.6, "Back": 1.0, "Bitmap": 2.0}
    print get_field_by_tf(tf_dict)
    print get_field_by_query("Internet Software Web", "Software")
    print get_url_by_field("medical", 'Hardware')



