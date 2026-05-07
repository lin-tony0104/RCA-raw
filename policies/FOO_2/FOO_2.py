from policies.BasePolicy import BasePolicy
from .cache import Cache,Cache_obj
#假設FOO真的不會准入超出cache size總量的物件。

class FOO_2_policy(BasePolicy):
    def __init__(self,config):
        self.cache=Cache(config["cache_size"])

    def request(self, o_id, o_size, o_features):# o_features目前沒用到
        obj = Cache_obj(o_id, o_size)
        hit = None
        FOO_label = float(o_features[0])
        
        if obj in self.cache:
            self.cache.pop_obj(obj)
            self.cache.insert_left(obj)
            hit = True
        else:
        #miss
            if FOO_label==1:
                while(self.cache.free < obj.o_size):
                    #evict
                    self.cache.pop_right()
                self.cache.insert_left(obj)
            hit = False
        return hit, " "


# class FOO_policy(BasePolicy):
#     def __init__(self,config):
#         # self.cache=Cache(config["cache_size"])
#         self.cache = set()


#     def request(self, o_id, o_size, o_features):# o_features目前沒用到

#         hit = o_id in self.cache
#         FOO_label=float(o_features[0])
#         # print("FOO_label:", FOO_label)
#         # print(len(self.cache))
#         if FOO_label==1:
#             self.cache.add(o_id)
#         else:
#             self.cache.discard(o_id)
#         return hit,""
    
# 功能與上面一樣，但會維護cache_size。
# class FOO_policy(BasePolicy):
#     def __init__(self,config):
#         # self.cache=Cache(config["cache_size"])
#         self.cache = set()


#     def request(self, o_id, o_size, FOO_label):# o_features目前沒用到
#         hit = o_id in self.cache

#         if FOO_label==1:
#             self.cache.add(o_id)
#         else:
#             self.cache.discard(o_id)
#         return hit,""
    