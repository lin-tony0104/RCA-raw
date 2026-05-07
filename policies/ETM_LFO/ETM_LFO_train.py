#在資料夾內執行
# K:前K筆, B:batch, L:未來L筆 
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))) 

import json
from ETM import ETM,Local_ID_Mapper

from collections import deque, defaultdict

import numpy as np
import random
import torch

from cache import Cache,Cache_obj

from torch.utils.data import IterableDataset, DataLoader

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
    


class ETMiterDataset(IterableDataset):
    def __init__(self, trace_path, lru_instance, K, B):
        self.trace_path = trace_path
        self.lru = lru_instance
        self.K = K
        self.B = B
        self.local_ID_mapper = Local_ID_Mapper(self.K)
        # print(f"內部 LRU ID: {id(self.lru)}")



    #每次觸發  算出一個sample 並回傳
    def __iter__(self):
        with open(self.trace_path,"r")as f:
            temp={"o_id":[], "o_size":[], "local_o_id":[], "c_free":[], "target":[]} # o: obj,  c: cache .    ex: c_free -> cache_free
            for req_cunter, req in enumerate(f):
                req_temp=req.split()
                

                o_id = int(req_temp[0])
                o_size = int(req_temp[1])
                target = float(req_temp[2])
                local_o_id = self.local_ID_mapper.get_local_id(o_id)
                c_size = self.lru.size

                # temp["o_id"].append(o_id)
                temp["o_size"].append(o_size)
                temp['local_o_id'].append(local_o_id)
                temp["c_free"].append(self.lru.free)
                temp["target"].append(target)


                if len(temp["target"]) >=self.K+self.B:        
                    norm_o_size = [_o_size/c_size for _o_size in temp['o_size']]
                    norm_c_free = [c_free/c_size for c_free in temp["c_free"]]
                    # print(temp['local_o_id'])
                    # break
                    sample={
                        "hist_local_IDs":torch.tensor(temp['local_o_id'][:-1], dtype=torch.long),
                        "curr_local_IDs":torch.tensor(temp['local_o_id'][-self.B:], dtype=torch.long),
                        "norm_o_sizes":torch.tensor(norm_o_size[-self.B:], dtype=torch.float),
                        "norm_c_free":torch.tensor(norm_c_free[-self.B:], dtype=torch.float),
                        "target":torch.tensor(temp["target"][-self.B:], dtype=torch.float)
                    }
                    
                    yield sample # 將smaple回傳
                    temp={"o_id":[], "o_size":[], "local_o_id":[], "c_free":[], "target":[]}

                self.lru.request(Cache_obj(req_temp[0],req_temp[1]),target)
                
                


            
# ========================================================================================================================            d
def parse_config(exp_name):
    #開啟config
    config=None
    config_path="../../experiments/"+exp_name+"/config.json"
    with open(config_path,"r") as f:
        config=json.load(f)
    #拆出各自config
    basic_config=config["basic_config"]
    policy_config=config["policy_config"]
    #初始化各功能
    trace = "../../trace/"+basic_config["trace_for_train"]
    result_path = "../../experiments/"+exp_name+"/trained_model/"+"/model.pth"

    return policy_config, trace,result_path





if __name__ == "__main__":
    #取得實驗名稱
    if len(sys.argv)==2:
        try:
            exp=sys.argv[1]
            open("../../experiments/"+exp+"/config.json",'r')
        except Exception as e:
            print(e)
            sys.exit()
    else:
        print("參數格式:")
        print("python ETM_labeling.py [experiment_name]")
        sys.exit()
    loss_log = open("../../experiments/"+exp+"/train_loss_log.txt", "w", encoding="utf-8")
    config, trace_path, result_path = parse_config(exp)

    lru=LRU(config["cache_size"])   
    # print(f"外部 LRU ID: {id(lru)}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model=ETM(config['ETM']).to(device)
    print("Using ",device," for ETM")

    
    #ETM參數
    __config = config['ETM']
    # K, B, L = __config['K'], __config['B'], __config['L']
    K, B = __config['K'], __config['B']

    
    #訓練參數
    __config = config['train']
    epoch = __config['epoch']
    sample_pool = deque(maxlen=__config['sample_pool_size'])
    n_sample = __config['n_sample']
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    for i in range(epoch):            
        print(f"Epoch {i+1}/{epoch} start")
        sample_pool.clear()
        model.train()
        
        dataset = ETMiterDataset(trace_path, lru, K, B)
        dataloader = DataLoader(dataset, batch_size=1, num_workers=0)
        data_iter = iter(dataloader)

        COUNTER = 0
        train_counter =0 
        while(True):
            COUNTER+=1
            try:
                data = next(data_iter)
                # print(f"curr_local_IDs_shape: {data['curr_local_IDs'].shape}")
                # print(f"target_shape: {data['target'].shape}")
                
                data = {k: v.to(device) for k, v in data.items()} #將data搬入gpu
                sample_pool.append(data) 
                # print(f"smaple_num: {COUNTER}")
            except StopIteration:
                break
            #池滿開始訓練
            if len(sample_pool) >= sample_pool.maxlen:
                loss_val = []
                for _ in range(n_sample):
                    s = random.choice(sample_pool)
                    # print(f"s['norm_o_sizes'].shape: {s['norm_o_sizes'].shape}, s['curr_local_IDs'].shape: {s['curr_local_IDs'].shape}")
                    pred = model(s['hist_local_IDs'], s['curr_local_IDs'], s['norm_o_sizes'], s['norm_c_free']).squeeze(-1)

                    loss_fn = torch.nn.BCEWithLogitsLoss()
                    # print(f"pred: {pred.shape}, target: {s['target'].shape}")
                    loss = loss_fn(pred, s['target'])   # pred.shape[1,len], target.shape[1,len]
                    loss.backward()
                    optimizer.step()
                    optimizer.zero_grad()
                    # print(f"pred_shape:{pred.shape} ,target_shape:{s['target'].shape} , n_sample:{n_sample}, loss:{loss.item()}  ")
                    loss_log.write(f"{loss.item()}\n")
                    loss_val.append(loss.item())
                print(f"smaple_num/pool_size : {COUNTER}/{sample_pool.maxlen}, avg_loss: {np.mean(loss_val)}")  
        torch.save(model.state_dict(), result_path+"_e"+str(i))












