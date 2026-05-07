#ETM_AEP => ETM_AdmitEvictPolicy

from policies.BasePolicy import BasePolicy
from .cache import Cache,cache_obj
# from utils.MinHeap import MinHeap
from .ETM import ETM

from collections import deque, defaultdict
import numpy as np
import random
import torch
# import heapq



#============================================准入,驅逐策略======================================================
# 驅逐 o_val最小者
class evict_policy:
    def __init__(self, cache):
        self.cache = cache

    def evict(self):
        victim = self.cache.pop_min() # pop o_val 最小者
        return victim


# admit用到的特徵
#   obj_size, obj_pop, obj_val
#   cache_avg_obj_size, cache_avg_obj_pop, cache_avg_val
#   val_gap ([obj_val - avg_val] 用來判斷是否能拉高平均)
# admit的訓練方法
#   
class admit_policy:
    def __init__(self, cache):
        self.cache = cache
        
        

    def admit(self, obj):
        # 有空間就准入 
        if obj.o_size <= self.cache.remaining_space:
            return True
        # print("heyyy")
        evict_set = []
        #空間不夠踢到夠為止
        while(self.cache.remaining_space < obj.o_size):
            v = self.cache.pop_min()
            evict_set.append(v)
            # print(v)
        a_pop = obj.o_pop
        e_pop = sum(v.o_pop for v in evict_set)

        #插回去
        for v in evict_set:
            self.cache.insert(v)

        return a_pop >= e_pop
        # return True
            

    

#= =================================================================================================
#策略
class ETM_AEP_policy(BasePolicy):
    def __init__(self,config):
        self.cache=Cache(config["cache_size"])
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.etm=ETM(config['ETM']).to(self.device)
        self.optimizer = torch.optim.Adam(self.etm.parameters(), lr=0.001)
        print("Using ",self.device," for ETM_AEP")


        self.L, self.K, self.B = config['ETM']['L'], config['ETM']['K'], config['ETM']['B']
        self.L_hist=deque([0]*self.L ,maxlen=self.L) #長度L的sliding window
        self.batch=[]
        self.batch_pool=deque(maxlen=config['batch_pool_size'])
        self.n_sample = config['n_sample']


        self.admit_policy=admit_policy(self.cache)
        self.evict_policy=evict_policy(self.cache)
        #DEBUG
        self.request_count = 0
        self.admit_count=0


    def request(self, o_id, o_size, o_features):
        o_id= int(o_id)  # 確保o_id是整數
        o_size = int(o_size)  # 確保o_size是整數
        o_pop= float(o_features[0]) #熱門度

        hit = False

        #DEBUG 
        self.request_count += 1
        # if not self.request_count%1000:
        #     print(self.request_count)
        #快取決策
        obj=cache_obj(o_id,o_size,o_pop,request_time=self.request_count)
        if obj.o_size>self.cache.size:
            raise ValueError("物件大小大於整體快取大小")
        
        
        #hit
        if obj in self.cache:
            hit=True
            self.cache.update_obj(obj) #更新位置
        else:
        #miss
            #admit
            if self.admit_policy.admit(obj):
                while(self.cache.remaining_space < obj.o_size):
                    victim = self.evict_policy.evict()
                    
            
                self.cache.insert(obj)
                self.admit_count+=1     
                

                
            # not admit
            else:
                #noting to do 
                pass 
        

        if self.request_count % self.L == 0:
            self.cache.decay_pop(self.request_count, self.L) #更新 popularity
        


        msg=" admit_count: "+str(self.admit_count)+" avg_pop: "+str(self.cache.get_avg_cache_pop())
        return hit, msg #miss






