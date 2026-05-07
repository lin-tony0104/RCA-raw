import numpy as np
import json
import pickle
import sys


def Atype(data):
    data = np.array(data)
    mean = np.mean(data)     # 平均
    s = np.std(data, ddof=1) # 樣本標準差
    uA = s/np.sqrt(len(data))# A類不確定度
    return mean, uA



    #取得實驗名稱
if len(sys.argv)>=2:
    try:
        exps=sys.argv[1:]
        for exp in exps:
            open("experiments/"+exp+"/config.json",'r')
    except Exception as e:
        print(e)
        sys.exit()
else:
    print("參數格式:")
    print("python TypeAu.py [exp1, exp2, ...]")
    sys.exit()
# exp_name = "exampleLRU"





OHRs= []
Tines= []
for exp in exps:
    with open("experiments/" + exp + "/result/result.pkl", "rb") as f:
        result_data = pickle.load(f)
        total_req = result_data['region'] * len(result_data['ohr_regionHit'])
        OHR = sum(result_data['ohr_regionHit'])/total_req
        OHR = round(OHR*100,2)
        
        wall_time = round(result_data['wall_time'],2)
        
        OHRs.append(OHR)
        Tines.append(wall_time)
print(OHRs)

mean, uA = Atype(OHRs)
mean, uA = round(mean,2), round(uA,2)
print("OHR_mean:", mean, "OHR_uA:", uA)

mean, uA = Atype(Tines)
mean, uA = round(mean,2), round(uA,2)
print("wall_time_mean:", mean, "wall_time_uA:", uA)
