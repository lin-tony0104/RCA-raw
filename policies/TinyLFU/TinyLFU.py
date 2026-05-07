from policies.BasePolicy import BasePolicy
from .cache import Cache,Cache_obj
from .lru import lru
from .cm4 import CM4
from .doorkeeper import Doorkeeper

class TinyLFU_policy(BasePolicy):
    def __init__(self,config):
        self.lru = lru(config["cache_size"])
        # self.CMS = CM4(config["cache_size"])
        self.CMS = CM4(1000000)
        self.doorkeeper = Doorkeeper(config["sample"], config["false_positive"])
        
        
        self.__age = 0
        self.__age_freq = config["sample"] # 衰減平率




    def request(self,o_id,o_size,o_feature=None):
        obj = Cache_obj(o_id,o_size)
        self.__age+=1
        hit = False
        self.CMS.add(o_id)
        
# aging
        if self.__age ==self.__age_freq:
            self.CMS.reset()
            self.doorkeeper.reset()        
            self.__age = 0

# replacement
        if obj in self.lru: #__contain__  HIT
            self.lru.set(obj) #只會更新位置
            hit = True
        else:   # Miss       
            hit = False
            if obj.o_size<=self.lru.cache.free:
                self.lru.set(obj) 

            if self.doorkeeper.allow(o_id): # doorkeeper過濾冷門物件
                v_id = self.lru.get_tail().o_id
                v_count = self.CMS.estimate(v_id)   # 驅逐物件的count
                o_count = self.CMS.estimate(o_id)   # 請求物件的count
                if v_count < o_count:
                    self.lru.set(obj) # 准入並驅逐

        msg = "cache_used: "+str(self.lru.cache.used)+" "   
        return hit, msg