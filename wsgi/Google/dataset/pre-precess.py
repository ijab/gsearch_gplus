#!/usr/bin/env python
import csv
import re

csv_file = csv.reader(open("./Glossory of Medical Terminology  English-Hmong.csv", "rb")) 
#header = csv_file.next()
x = []
n = 0
for row in csv_file:
    if len(row) > 0:
        s = row[0]
        to = s.find("(")
        if to == -1:
            to = len(s) - 1
        else:
            to -= 1
        while s[to] == ' ':
            to -= 1
        if s[0].isalpha():
            #print s[0:to+1].replace("  "," ")
            x.append(s[0:to+1].replace("  "," "))

cw = csv.writer(open('./Medical/Medical.csv', "wb"))
for r in x:
    cw.writerow([r]);
    print [r]

print "finish"
