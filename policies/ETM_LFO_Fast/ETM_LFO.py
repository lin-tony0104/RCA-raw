#ETM_AEP => ETM_AdmitEvictPolicy

from policies.BasePolicy import BasePolicy
from .cache import Cache,Cache_obj

# from utils.MinHeap import MinHeap
from .ETM import ETM, Local_ID_Mapper

from collections import deque, defaultdict
import numpy as np
import random
import torch
# import heapq



class LRU(Cache):
    def request(self, obj, admit):
        admit = admit>0.5   # 可接受0/1 也可接受0~1
        hit = obj in self
        if hit:
            self.pop_obj(obj)
            self.insert_left(obj)
        else:
            if admit:
                while self.free < obj.o_size:
                    self.pop_right()
                self.insert_left(obj)
        return hit

#============================================准入,驅逐策略======================================================
class ETM_LFO_policy(BasePolicy):
    def __init__(self,config):

        self.lru = LRU(config["cache_size"])
        self.admit_count = 0
        self.req_counter = 0
        self.log_file = open("experiments/"+config["exp_name"]+"/admit_log.txt", "w", encoding="utf-8")
        # self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.device = torch.device("cpu")
        # load model
        model_path = "experiments/"+config["exp_name"]+"/trained_model/"+config["model_name"]
        state = torch.load(model_path, map_location=self.device)
        self.etm = ETM(config['ETM']).to(self.device)
        self.etm.load_state_dict(state)
        self.etm.eval()
        # self.etm = torch.compile(self.etm, mode="reduce-overhead") 

        self.local_ID_mapper = Local_ID_Mapper(config['ETM']['K'])
        dummy_id = 0
        dummy_local_id = self.local_ID_mapper.get_local_id(dummy_id)
        self.prev_local_id = torch.tensor([dummy_local_id], dtype=torch.long, device=self.device).unsqueeze(0)  # shape [1, 1] ,[B,id]
        self.curr_local_id = torch.zeros((1,1), dtype=torch.long, device=self.device)
        self.cache_free_norm = torch.zeros((1,1), dtype=torch.float32, device=self.device)
        self.obj_size_norm = torch.zeros((1,1), dtype=torch.float32, device=self.device)
        print("Using ",self.device," for ETM_LFO")

        # self.prev_id = torch.tensor([0], dtype=torch.long, device=self.device).unsqueeze(0)  # Dummy previous object

    def request(self, o_id, o_size, o_features=None):
        with torch.inference_mode(): # 加上這行
            obj = Cache_obj(int(o_id), int(o_size))
            o_local_id = self.local_ID_mapper.get_local_id(int(o_id))
            self.curr_local_id[0,0] = o_local_id
            self.cache_free_norm[0,0] = self.lru.free/self.lru.size
            self.obj_size_norm[0,0] = obj.o_size/self.lru.size
            # curr_local_id = torch.tensor([int(o_local_id)], dtype=torch.long, device=self.device).unsqueeze(0)  # shape [1, 1] ,[B,id]
            # cache_free_norm = torch.tensor([self.lru.free/self.lru.size], dtype=torch.float32, device=self.device).unsqueeze(0) # Shape[1,1], [B,size]
            # obj_size_norm = torch.tensor([obj.o_size/self.lru.size], dtype=torch.float32, device=self.device).unsqueeze(0)# Shape[1,1], [B,size]
            
            admit = self.etm(self.prev_local_id, self.curr_local_id, self.obj_size_norm, self.cache_free_norm)
            # admit = admit.item()>0
            admit = torch.sigmoid(admit).item()
            
            hit = self.lru.request(obj, admit)
            
            # __admit01 = 1 if admit>0.5 else 0
            # self.log_file.write(f"{__admit01}\n")
            self.req_counter+=1
            if admit>0.5:
                self.admit_count += 1
            # msg = f"admit_count:{self.admit_count} not_admit_count: {self.req_counter -self.admit_count}"
            msg = ""
            self.prev_local_id[0,0]= self.curr_local_id[0,0]
            return hit, msg








    

