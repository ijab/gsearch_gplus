import re
import operator
import time

from plus import dx_gplus_crawler
from Classer import TypeIdentifier

typeIdentifier=TypeIdentifier()

class dx_indexer:
    def __init__(self, code):
        self.dictionary=None
        self.Type=None
        self.friendTypes=None
        self.plus=dx_gplus_crawler(code)
        self.plus.setCallback(self.buildTF)
        if self.plus.getProgress()['Status'] != 'error': 
            self.plus.startCrawl()
        self.stopwords=set()
        self.loadStopWords()
        self.TFbyID={}
        self.TFtotal={}
        self.rightAjContext={}
        
        
    def logout(self, code):
        self.dictionary=None
        self.Type=None
        self.friendTypes=None
        self.plus.relogin(code)
        self.plus.setCallback(self.buildTF)
        self.plus.startCrawl()
        self.TFbyID={}
        self.TFtotal={}
        self.rightAjContext={}
        
    def loadStopWords(self):
        #file = open("stop_words.txt")
        #while 1:
        #    line = file.readline()
        #    if not line:
        #        break
        #    line=re.sub(r'[^\w]', '', line)
        #    self.stopwords.add(line)
        import stop_words
        for x in stop_words.stop_words:
            self.stopwords.add(x)
            
    def buildTF(self):
        self.plus.setProgress({'Status':'Building index','RunningJob':'Building indexes', 'Progress':75})
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
                if( i < len(word) and word[i] == chars[i]):
                    temp.append(word)
                    
            if(len(candidates) == 0):
                return None
            else:
                candidates = temp
        return candidates
        
    def queryCompletion(self, query):
        chars=None
        query = re.sub(r'[^\w]', ' ', query.lower())
        query = query.strip()
        
        qwords=query.split()
        cursor=len(qwords)

        if(cursor > 0):
            suggestions=[]
            temp=''
            sug = ''
            # Append previous words
            for n in range(cursor - 1):
                if(len(qwords[n])>=0 and qwords[n]!=' '):
                    temp=temp+qwords[n]+' '

            chars=qwords[cursor-1]
            if(self.rightAjContext.has_key(chars)):
                if(len(temp)>0):
                    temp=temp+' '+chars
                else:
                    temp=chars
                for w in self.rightAjContext[chars]:
                    sug=temp+' '+w
                    suggestions.append({'id':sug, 'label':sug, 'value':sug})
            else:
                cadidates = self.guessWord(chars)
                if cadidates:
                    for w in self.guessWord(chars):
                        sug=temp+' '+w
                        suggestions.append({'id':sug, 'label':sug, 'value':sug})
            return {'suggestions':suggestions, 'query_type':typeIdentifier.getTypeByQuery(query)}
        else:
            return {'suggestions':[], 'query_type' : ''}
            
    def getUserType(self):
        _type = 'Unknown'
        
        if(self.Type is None):
            if self.TFbyID.has_key('me'):
                sorted(self.TFbyID['me'].iteritems(), key=operator.itemgetter(1), reverse=True)
                
                sorted_keys = self.TFbyID['me'].keys()[:100]
                top_tf = {}
                for x in sorted_keys:
                    top_tf[x] = self.TFbyID['me'][x]
                self.Type=typeIdentifier.getTypeByTF(top_tf)
        
        if self.Type is not None:
            _type = self.Type

        return {'type':_type}
        
    def getHelperList(self, query):
        query=re.sub(r'[^\w]', ' ', query.lower())
        
        if(self.friendTypes is None):
            self.friendTypes={}
            if(self.plus.friends is None):
                return {'error':'No friends'}
            else:
                for id in self.plus.InfoList.keys():
                    if(id!='me' and self.TFbyID.has_key(id)):
                        sorted(self.TFbyID[id].iteritems(), key=operator.itemgetter(1), reverse=True)
                        sorted_keys = self.TFbyID[id].keys()[:100]
                        top_tf = {}
                        for x in sorted_keys:
                            top_tf[x] = self.TFbyID[id][x]
                            
                        type=typeIdentifier.getTypeByTF(top_tf)
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

    def getUrlByType(self,type):
        return typeIdentifier.getUrlByType(type)
    
if __name__ == '__main__':
    index=dx_indexer("ssas")
    while 1:
        print index.getProgress()
        time.sleep(2)
        if(index.getProgress()['Status']=='Ready'):
            print index.queryCompletion('data ')
    #print index.getNameById('114813190598462470004')
    #print index.queryCompletion('data ')
    #print index.getHelperList('data ')
    #index.logout()
    #print index.queryCompletion('information ')
    
