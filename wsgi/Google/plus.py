import gflags
import httplib2
import logging
import os
import pprint
import sys
import re

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run

FLAGS = gflags.FLAGS

CLIENT_SECRETS = 'client_secrets.json'

MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   some place

with information from the APIs Console <https://code.google.com/apis/console>.

"""

FLOW = flow_from_clientsecrets(CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/plus.login',
    message=MISSING_CLIENT_SECRETS_MESSAGE)
    
gflags.DEFINE_enum('logging_level', 'ERROR',
    ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    'Set the level of logging detail.')


class dx_gplus_crawler:
    def __init__(self):
        logging.getLogger().setLevel(getattr(logging, FLAGS.logging_level))
        storage = Storage('plus.dat')
        #if self.credentials is None or self.credentials.invalid:
        self.credentials = run(FLOW, storage)
        self.http = httplib2.Http()
        self.http = self.credentials.authorize(self.http)
        self.service = build("plus", "v1", http=self.http)
        self.person=None
        self.friends=None
        self.InfoList=None
        self.progress={'Status':'Not Ready', 'RunningJob':'Nothing', 'Progress':0}
        
    def relogin(self):
        storage = Storage('plus.dat')
        self.credentials = run(FLOW, storage)
        self.http = httplib2.Http()
        self.http = self.credentials.authorize(self.http)
        self.service = build("plus", "v1", http=self.http)
        self.person=None
        self.friends=None
        self.InfoList=None
        self.progress={'Status':'Not Ready', 'RunningJob':'Nothing', 'Progress':0}
        
    def fetchMe(self):
        self.setProgress({'Status':'Crawling Info', 'RunningJob':'Fetching User\'s own Information', 'Progress':0})
        self.person = self.service.people().get(userId='me').execute(http=self.http)
        self.fetchPersonInfo('me')
        self.setProgress({'Progress':5})
        self.friends = self.service.people().list(userId='me',collection='visible',orderBy='alphabetical', pageToken=None, maxResults=None).execute(http=self.http)
        totalfriends=0
        processedfriends=0
        if(self.friends.has_key('totalItems')):
            totalfriends=self.friends['totalItems']
        for item in self.friends.get('items', []):
            self.fetchPersonInfo(item['id'])
            self.setProgress({'RunningJob':'Fetching Information of %d / %d friends' % (processedfriends, totalfriends) , 'Progress':processedfriends/totalfriends*70+5})
        
    def parseActivity(self, activity):
        content=[]
        content.append(activity['title'])
        content.append(self.removeTag(activity['object']['content']))
        if(activity['object'].has_key('attachments')):
            for attachment in activity['object']['attachments']:
                content.append(attachment['displayName'])
                content.append(attachment['content'])
        if(activity.has_key('annotation')):
            content.append(activity['annotation'])
        if(activity.has_key('placeName')):
            content.append(activity['placeName'])
        if(activity.has_key('location')):
            if(activity['location'].has_key('displayName')):
                content.append(activity['location']['displayName'])
        return content
        
    def parseComment(self, comment):
        content=[]
        if(comment.has_key('object')):
            if(comment['object'].has_key('content')):
                content.append(self.removeTag(comment['object']['content']))
        return content
        
    def fetchPersonInfo(self, id):
        person=self.service.people().get(userId=id).execute(http=self.http)
        if(self.InfoList is None):
            self.InfoList={}
        content=[]
        if(person.has_key('organizations')):
            for org in person['organizations']:
                content.append(org['name'])
        if(person.has_key('tagline')):
            content.append(person['tagline'])
        activities_doc = self.service.activities().list(userId=id, collection='public').execute(http=self.http)
        for item in activities_doc['items']:
            activity=self.service.activities().get(activityId=item['id']).execute(http=self.http)
            content.extend(self.parseActivity(activity))
            comments=self.service.comments().list(activityId=activity['id']).execute(http=self.http)
            for comment in comments['items']:
                content.extend(self.parseComment(comment))
            while(comments.has_key('nextPageToken')):
                comments=self.service.comments().list(activityId=activity['id'], pageToken=comments['nextPageToken']).execute(http=self.http)
                for comment in comments['items']:
                    content.extend(self.parseComment(comment))
            
        while(activities_doc.has_key('nextPageToken')):
            activities_doc = self.service.activities().list(userId=id, collection='public', pageToken=activities_doc['nextPageToken']).execute(http=self.http)
            for item in activities_doc['items']:
                activity=self.service.activities().get(activityId=item['id']).execute(http=self.http)
                content.extend(self.parseActivity(activity))
                comments=self.service.comments().list(activityId=activity['id']).execute(http=self.http)
                for comment in comments['items']:
                    content.extend(self.parseComment(comment))
                while(comments.has_key('nextPageToken')):
                    comments=self.service.comments().list(activityId=activity['id'], pageToken=comments['nextPageToken']).execute(http=self.http)
                    for comment in comments['items']:
                        content.extend(self.parseComment(comment))
            
        if(id=='me'):
            moments = self.service.moments().list(userId=id, collection='vault', pageToken=None, maxResults=None, targetUrl=None, type=None).execute(http=self.http)
            if(moments.has_key('target')):
                if(moments['target'].has_key('text')):
                    content.append(moments['target']['text'])
            if(moments.has_key('result')):
                if(moments['result'].has_key('text')):
                    content.append(moments['result']['text'])
        self.InfoList[id]=self.format(content)
        
    def format(self, content):
        if(content is not None):
            for n in range(len(content)):
                temp=content[n]
                content[n]=re.sub(r'[^\w]', ' ', temp.lower())
        return content
        
    def removeTag(self, htmldoc):
        p = re.compile('<[^>]+>')
        return p.sub(" ", htmldoc)     
        
    def setProgress(self, arguments):
        if(arguments.has_key('Status')):
            self.progress['Status']=arguments['Status']
        if(arguments.has_key('RunningJob')):
            self.progress['RunningJob']=arguments['RunningJob']
        if(arguments.has_key('Progress')):
            self.progress['Progress']=arguments['Progress']
            
    def getProgress(self):
        return self.progress

if __name__ == '__main__':
    dx_crawler=dx_gplus_crawler()
    dx_crawler.fetchMe()
    print dx_crawler.InfoList
