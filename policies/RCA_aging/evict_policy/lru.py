#已完成
from policies.RCA_aging.lib.dequedict import DequeDict
# from evict_BASE import evict_BASE
from policies.RCA_aging.evict_policy.evict_BASE import evict_BASE
"""
主要功能: 決定出要evict的obj
其他程式碼: 計算驅逐對象的
"""



class LRU(evict_BASE):
    def __init__(self,cache_size):
        self.cache_size=cache_size
        self.cache=DequeDict()



#=============================
    def hit(self, obj):
        self.cache[obj.o_block]=obj #刷新位置
        
    def addToCache(self,obj):
        #剛清完空間，把obj放入cache
        self.cache[obj.o_block]=obj
        
    def evict(self):
        return self.cache.popFirst()
     

    
    def DEBUG_show_para(self):
        """ print方法所用到的所有超參數 """
        # print("LRU counter:",self.DEBUG_counter)
        