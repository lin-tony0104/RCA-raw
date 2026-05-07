#在資料夾內執行
# L:前L筆, B:batch, K:未來K筆 
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))) 

import json
from policies.ETM_AEP_V2.ETM import ETM
from collections import deque, defaultdict
import numpy as np
import random
import torch
import matplotlib.pyplot as plt

class TrackDeque:
    def __init__(self, maxlen):
        self.deque = deque(maxlen=maxlen)
        self.maxlen = maxlen
    
    def append(self, item):
        dropped = None
        if len(self.deque) == self.maxlen:
            dropped = self.deque[0]  # 最舊元素
        self.deque.append(item)
        return dropped

class recoder: #用來記錄展示結果list
    def __init__(self, region):
        self.region = region
        self.datas = []
        self.datas_temp = []

    def append(self, data):
        self.datas_temp.append(data)
        if len(self.datas_temp) >= self.region:
            print("recording: ", len(self.datas)*self.region)
            avg = sum(self.datas_temp) / self.region
            self.datas.append(avg)
            self.datas_temp = [] 

    def get_result(self):
        return self.datas
    
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
    evaluator_config = config["evaluator_config"]
    #初始化各功能
    trace_path = "../../trace/"+basic_config["trace"]

    return policy_config, evaluator_config, trace_path




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


    print("label CHECK")
    policy_config, eval_config, trace= parse_config(exp)
    # print(config)

    L, B, K = policy_config['ETM']['L'], policy_config['ETM']['B'], policy_config['ETM']['K']
    region = eval_config['region']

    with open(trace, 'r') as f:
        sliding_window = TrackDeque(L)
        window_counter = defaultdict(int)
        
        #真實值與預測值
        targets = recoder(region)
        preds = recoder(region)
        diff = recoder(region)
        pred_pops_for_diff = deque()

        for i, line in enumerate(f):
            temp = line.split()
            o_id = int(temp[0])
            pop = float(temp[2])
            preds.append(pop)
            pred_pops_for_diff.append(pop)
            
            # print(o_id, pop)
            rear_obj = sliding_window.append(o_id)
        
            window_counter[o_id]+=1
            if rear_obj is not None: #滿
                window_counter[rear_obj]-=1
                if window_counter[rear_obj]==0:
                    del window_counter[rear_obj]
                targets.append(window_counter[rear_obj])
                diff.append(abs(window_counter[rear_obj]-pred_pops_for_diff.popleft()))# 計算 預測與真實的絕對差值

            if (i+1)%10000000==0:
                break
            
        for line in ["-1 0 0\n"]*L: #[-1 0 0] dummy trace data
            temp = line.split()
            o_id = int(temp[0])
            pop = temp[2]
            # print(o_id, pop)
            rear_obj = sliding_window.append(o_id)
        
            window_counter[o_id]+=1
            if rear_obj is not None:
                window_counter[rear_obj]-=1
                if window_counter[rear_obj]==0:
                    del window_counter[rear_obj]
                targets.append(window_counter[rear_obj])
                diff.append(abs(window_counter[rear_obj]-pred_pops_for_diff.popleft()))# 計算 預測與真實的絕對差值


        print("len targets:", len(targets.get_result())
              ," len preds:", len(preds.get_result()))
        x = [x*region for x in range(len(targets.get_result()))]

        plt.figure()  # 建立圖表
        plt.plot(x, preds.get_result(), label="Prediction", linewidth=2)  # 藍色預設，label用於圖例
        plt.plot(x, targets.get_result(), label="Target", linewidth=2)     # 紅色預設會自動分配
        plt.plot(x, diff.get_result(), label="abs Diff", linewidth=2, color="0.7")     

        plt.title("Pred vs Target")       # 標題
        plt.xlabel("Request Index")       # x軸標註
        plt.ylabel("reuse")               # y軸標註

        plt.legend()  # 顯示圖例（標註曲線是什麼）
        plt.grid(True)  # 可選：顯示網格讓曲線更好讀

        plt.show()


