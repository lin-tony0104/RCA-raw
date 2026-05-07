from policies.BasePolicy import BasePolicy
from .cache import Cache,Cache_obj


#策略
class LRU_policy(BasePolicy):
    def __init__(self,config):
        self.cache=Cache(config["cache_size"])

    def request(self, o_id, o_size, o_features=None):# o_features目前沒用到
        hit = False
        obj=Cache_obj(o_id,o_size)
        if obj.o_size>self.cache.size:
            raise ValueError("物件大小大於整體快取大小")

        
        #hit
        if obj in self.cache:
            self.cache.pop_obj(obj)
            self.cache.insert_left(obj)
            hit = True
        else:
        #miss
            while(self.cache.remaining_space < obj.o_size):
                #evict
                self.cache.pop_right()

            self.cache.insert_left(obj)
        return hit, ""


