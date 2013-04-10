import re
import operator

from plus import dx_gplus_crawler
from Classer import TypeIdentifier

typeIdentifier=TypeIdentifier()

class dx_indexer:
    def __init__(self):
        self.dictionary=None
        self.Type=None
        self.friendTypes=None
        self.plus=dx_gplus_crawler()
        self.plus.fetchMe()
        self.stopwords=set()
        self.loadStopWords()
        self.TFbyID={}
        self.TFtotal={}
        self.rightAjContext={}
        self.buildTF()
        self.plus.setProgress({'Status':'Reday','RunningJob':'Nothing', 'Progress':0})
        
        
    def logout(self):
        self.dictionary=None
        self.Type=None
        self.friendTypes=None
        self.plus.relogin()
        self.plus.fetchMe()
        self.TFbyID={}
        self.TFtotal={}
        self.rightAjContext={}
        self.buildTF()
        self.plus.setProgress({'Status':'Reday','RunningJob':'Nothing', 'Progress':0})
        
    def loadStopWords(self):
        file = open("stop_words.txt")
        while 1:
            line = file.readline()
            if not line:
                break
            line=re.sub(r'[^\w]', '', line)
            self.stopwords.add(line)
            
    def buildTF(self):
        self.plus.setProgress({'Status':'Building index','RunningJob':'Building indexes', 'Progress':0})
        if(self.plus.InfoList is not None):
            for id in self.plus.InfoList.keys():
                TF={}
                for item in self.plus.InfoList[id]:
                    recent=None
                    for word in item.split():
                        if(len(word)>0 and word not in self.stopwords):
                            if(recent is not None):
                                if(self.rightAjContext.has_key(recent)):
                                    if(self.rightAjContext[recent].has_key(word)):
                                        self.rightAjContext[recent][word]=self.rightAjContext[recent][word]+1
                                    else:
                                        self.rightAjContext[recent][word]=1
                                else:
                                    self.rightAjContext[recent]={word:1}
                            if(TF.has_key(word)):
                                TF[word]=TF[word]+1
                            else:
                                TF[word]=1
                            recent=word
                        else:
                            recent=None
                    self.TFbyID[id]=TF
                    self.TFtotal.update(TF)
        self.plus.setProgress({'Progress':100})      
        
    def getRightWordList(self, word):
        if(self.rightAjContext.has_key(word)):
            return sorted(self.rightAjContext[word].iteritems(), key=operator.itemgetter(1), reverse=True)
        else:
            return None
            
    def guessWord(self, chars):
        if(self.dictionary is None):
            self.dictionary=sorted(self.rightAjContext.keys())
        candidates=self.dictionary
        for i in range(len(chars)):
            temp=[]
            for word in candidates:
                if(word[i]==chars[i]):
                    temp.append(word)
            if(len(candidates)==0):
                return None
            else:
                candidates=temp
        return candidates
        
    def queryCompletion(self, query):
        chars=None
        qwords=query.split()
        cursor=len(qwords)-1
        while(cursor>=0 and len(qwords[cursor])==0):
            cursor=cursor-1
        if(cursor>=0):
            suggestions=[]
            temp=''
            sug = ''
            for n in range(cursor-1):
                if(len(qword[n])>=0 and qword[n]!=' '):
                    temp=temp+qwords[n]+' '

            chars=qwords[cursor]
            if(self.rightAjContext.has_key(chars)):
                if(len(temp)>0):
                    temp=temp+' '+chars
                else:
                    temp=chars
                for w in self.rightAjContext[chars]:
                    sug=temp+' '+w
            else:
                for w in self.guessWord(chars):
                    sug=temp+' '+w

            suggestions.append({'id':sug, 'label':sug, 'value':sug})
            return {'suggestions':suggestions}
        else:
            return {'suggestions':[]}
            
    def getUserType(self):
        if(self.Type is None):
            self.Type=typeIdentifier.getTypeByTF(self.TFbyID['me'])
        return {'type':self.Type}
        
    def getHelperList(self, query):
        if(self.friendTypes is None):
            self.friendTypes={}
            if(self.plus.friends is None):
                return {'error':'No friends'}
            else:
                for id in self.plus.InfoList.keys():
                    if(id!='me' and self.TFbyID.has_key(id)):
                        type=typeIdentifier.getTypeByTF(self.TFbyID[id])
                        self.friendTypes[id]=type
        queryType=typeIdentifier.getTypeByQuery(query)
        result={}
        for id in self.friendTypes.keys():
            fitlevel=typeIdentifier.contains(queryType,self.friendTypes[id])
            if(fitlevel>=0.5):
                result[id]=fitlevel
        sorted(result.iteritems(), key=operator.itemgetter(1), reverse=True)
        
        return [{'jid':'%s@gmail.com' % x, 'name':self.getNameById(x)} for x in result.keys()]
        
    def getNameById(self, id):
        for friend in self.plus.friends['items']:
            if(id==friend['id']):
                return friend['displayName']
        return id
        
    def getProgress(self):
        return self.plus.progress
    
if __name__ == '__main__':
    index=dx_indexer()
    print index.getNameById('114813190598462470004')
    print index.queryCompletion('data ')
    print index.getHelperList('data ')
    index.logout()
    print index.queryCompletion('information ')
    
