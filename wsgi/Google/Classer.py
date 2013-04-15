import Search
import sys

class TypeIdentifier:
    def getTypeByTF(self, TF):
        print TF
        return Search.get_field_by_tf(TF)
        
    def getTypeByQuery(self, query):
        print query
        return Search.get_field_by_query(query)
        
    def contains(self, type1, type2):
        return Search.get_relavance(type1, type2)

    def getUrlByType(self,type):
        return None


