#省去每個policy都要寫一些沒用到的函數

class evict_BASE:
    def __init__(self,cache_size):
        pass
    def request(self,obj):
        pass
    def hit(self,obj):
        pass
    def miss(self,obj):
        pass
    def admit(self,objj):
        pass
    def addToCache(self,obj):
        pass
    def not_admit(self,obj):
        pass
        
    def evict(self):
        raise NotImplementedError("This method should be overridden by subclasses")
        
    def end(self,obj):#考慮要不要刪
        pass
    
    def GET_DEBUG_MESSAGE(self):
        return ""