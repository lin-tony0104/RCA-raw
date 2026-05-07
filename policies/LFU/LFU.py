from policies.BasePolicy import BasePolicy
from .cache import Cache,cache_obj

class LFU_policy(BasePolicy):
    def __init__(self,config):
        self.cache=Cache(config["cache_size"])

    def request(self, o_id, o_size, o_features=None):# o_features目前沒用到
        obj=cache_obj(o_id,o_size)
        if obj.o_size>self.cache.size:
            raise ValueError("物件大小大於整體快取大小")

        
        #hit
        if obj in self.cache:
            #更新頻率
            obj=self.cache.cache_dict[obj] #更新物件
            obj.o_freq+=1
            self.cache.update_obj(obj) #更新位置
            return True #hit
        else:
        #miss
            while(self.cache.remaining_space < obj.o_size):
                #evict
                self.cache.pop_min()
            self.cache.insert(obj)
        return False #miss

        




