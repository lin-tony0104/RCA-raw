#在資料夾內執行
# L:前L筆, B:batch, K:未來K筆 
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))) 

import json
from policies.ETM_AEP.ETM import ETM
from collections import deque, defaultdict
import numpy as np
import random
import torch


def parse_config(exp_name):
    #get_config
    
    #開啟config
    config=None
    config_path="../../experiments/"+exp_name+"/config.json"
    with open(config_path,"r") as f:
        config=json.load(f)

    #拆出各自config
    basic_config=config["basic_config"]
    policy_config=config["policy_config"]

    #初始化各功能
    trace_path = "../../trace/"+basic_config["build_trace"]
    result_trace_path = "../../trace/trace_for_etm/"+basic_config["build_trace"]

    return policy_config,trace_path,result_trace_path


class ETM_trainer():
    def __init__(self, model, config, device):
        self.device = device
        self.model = model

        self.L, self.K, self.B = config['ETM']['L'], config['ETM']['K'], config['ETM']['B']
        batch_pool_size, self.n_sample = config['batch_pool_size'], config['n_sample']

        self.optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        self.batch_pool = deque(maxlen=batch_pool_size)
        self.batch = []
    
    def observe(self, o_id):
        self.batch.append(o_id)
        if len(self.batch) >= self.B + self.K + self.L:
            self.batch_pool.append(np.asarray(self.batch, dtype=np.int64))
            self.batch = []
            self.train()
    
    def train(self):
        for _ in range(self.n_sample):
            #sample
            id_seq = random.choice(self.batch_pool)
            seq,target=self.get_traing_data(id_seq,self.L,self.K,self.B)# 若改成batch_pool內儲存這個  可以減少重複計算
        
            hist_ids=seq[:self.B+self.K-1]
            curr_ids=seq[self.K:self.K+self.B]

            # 轉成tensor 並加上batch維度
            hist_ids = torch.as_tensor(hist_ids, dtype=torch.int64,device=self.device).unsqueeze(0)
            curr_ids = torch.as_tensor(curr_ids, dtype=torch.int64,device=self.device).unsqueeze(0)
            target = torch.as_tensor(target, dtype=torch.float32,device=self.device).unsqueeze(0)

            self.optimizer.zero_grad()
            preds= self.model(hist_ids,curr_ids)
            # loss_fn = torch.nn.PoissonNLLLoss(log_input=False)

            loss_fn = torch.nn.MSELoss()
            loss = loss_fn(preds, target)
            loss.backward()
            self.optimizer.step()
            print(f"Loss: {loss.item()}")        


    def get_traing_data(self,batch, L, K, B):  #len(batch)= B+K+L
        req_seq=batch[:B+K]
        target=[]
        counter = defaultdict(int)
        
        # 先處理好未來L筆的熱門度
        for i in range(L):
            o_id = batch[K+i]
            counter[o_id]+=1

        #紀錄熱門度(target)
        for i in range(B):
            tail_id = batch[K+L+i]
            head_id = batch[K+i]

            counter[tail_id]+=1
            counter[head_id]-=1
            target.append(counter[head_id])
            
            #用來防止記憶體洩漏
            if counter[head_id]<=0:
                del counter[head_id]
        target = np.asarray(target, dtype=np.int64)
        return req_seq , target





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


    print("start_building")
    config, trace_path, result_trace_path = parse_config(exp)
    result_path = result_trace_path+"_forETM"
    # print(policy_config)
    
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    etm=ETM(config['ETM']).to(device)
    print("Using ",device," for ETM")
    trainer = ETM_trainer(etm, config, device)
    sliding_window = deque([0]*(config['ETM']['L'] + config['ETM']['B']),maxlen= config['ETM']['L'] + config['ETM']['B'])
    recent_requests = deque(maxlen=config['ETM']['B'])
    


    with open(trace_path,"r")as f ,open(result_path,"w") as wf:
        counter = 0
        for req in f:
            counter+=1
            
            temp=req.split()
            o_id = int(temp[0])
            o_size = temp[1]
            trainer.observe(o_id)
            sliding_window.append(o_id)      
            recent_requests.append((o_id, o_size))

            if counter % config['ETM']['B']==0:
                print("counter:", counter)
                with torch.no_grad():
                    hist_ids = list(sliding_window)[:config['ETM']['L']]
                    curr_ids = list(sliding_window)[config['ETM']['L']:]
                    # print("Hist IDs:", hist_ids)
                    # print("Curr IDs:", curr_ids)
                    hist_ids = torch.as_tensor(hist_ids, dtype=torch.int64,device=device).unsqueeze(0)
                    curr_ids = torch.as_tensor(curr_ids, dtype=torch.int64,device=device).unsqueeze(0)
                    preds= etm(hist_ids,curr_ids)

                    for req, pop in zip(recent_requests, preds.squeeze().cpu().numpy()):
                        wf.write(f"{req[0]} {req[1]} {pop}\n")

                    # print("Preds:", preds)
            
            
