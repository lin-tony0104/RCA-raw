import json
import matplotlib.pyplot as plt
import pickle
import sys
import numpy as np
    #取得實驗名稱
#==========================其他函數==============================
# 超參數
window_size = 100

# 只看最近 window_size個值，算他們的平均。 輸入長度L，輸出長度L-W+1
def moving_average(data):
    weights = np.ones(window_size) / window_size
    return np.convolve(data, weights, mode='valid')

def average(data):
    result_data = [round(sum(data[i:i+window_size])/float(len(data[i:i+window_size])),4) for i in range(0,len(data),window_size)]
    return result_data



#====================可用的功能函數=======================
def get_OHR(regionHit, regionReq):
    return round(sum(regionHit)/sum(regionReq),4)

def get_segOHR(regionHit, regionReq):
    result=[]
    for hit, req in  zip(regionHit, regionReq):
        result.append(round(hit/req,4))

    # return moving_average(result)
    return average(result)

def get_cumOHR(regionHit, regionReq):
    result = []
    cum_req = 0
    cum_hit = 0
    for hit, req in  zip(regionHit, regionReq):
        cum_req += req
        cum_hit += hit
        r = round(cum_hit/cum_req,4)
        result.append(r)
    return result 

def get_BHR(regionHitByte, regionByte):
    return round(sum(regionHitByte)/sum(regionByte),4)

def get_segBHR(regionHitByte, regionByte):
    result=[]
    for hit_byte, byte in  zip(regionHitByte, regionByte):
        result.append(round(hit_byte/byte,4))
    return result

def get_cumBHR(regionHitByte, regionByte):
    result = []
    cum_byte = 0
    cum_hit_byte = 0
    for hit_byte, byte in  zip(regionHitByte, regionByte):
        cum_byte += byte
        cum_hit_byte += hit_byte
        r = round(cum_hit_byte/cum_byte,4)
        result.append(r)
    return result







#===============================主程式=========================================
if len(sys.argv)==3:
    try:
        exps=sys.argv[1:]
        for exp in exps:
            open("experiments/"+exp+"/config.json",'r')
    except Exception as e:
        print(e)
        sys.exit()
else:
    print("參數格式:")
    print("python show_result_diff.py [exp1, exp2, ...]")
    sys.exit()
# exp_name = "exampleLRU"

exp_names=[]
OHRs=[]
segOHRs =[]
regions = []
print("result: ")
for exp in exps:
    exp_names.append(exp)
    config_path = "experiments/" + exp + "/config.json"
    with open(config_path, "r") as f:
        config = json.load(f)
        print("config: ")
        print(json.dumps(config, indent=4, ensure_ascii=False))  # ✅漂亮縮排

    with open("experiments/" + exp + "/result/result.pkl", "rb") as f:
        result_data = pickle.load(f)

        OHRs.append(get_OHR(result_data['ohr_regionHit'], result_data['ohr_regionReq']))
        segOHRs.append(get_segOHR(result_data['ohr_regionHit'], result_data['ohr_regionReq']))
        regions.append(result_data["region"])


    print(exp+" OHR:", OHRs[-1])
# print("BHR:", BHR)

#==============diff===============  
diff_name = f"{exp_names[0][9:-5]} - {exp_names[1][9:-5]} "
diff = [ohr1 - ohr2 for ohr1, ohr2 in zip(segOHRs[0], segOHRs[1]) ]
diff_region = regions[0]  # 假設兩個實驗的region相同




for exp_name, OHR in zip(exp_names, OHRs):
    print(exp_name+" OHR:", OHR)


plt.figure(figsize=(6, 4))  # 建立圖表
# for exp_name, OHR, segOHR, region in zip(exp_names, OHRs, segOHRs, regions):
    # plt.plot([region*(x+1) for x in range(len(segOHR))], segOHR, label=exp_name, linewidth=2)  # 藍色預設，label用於圖例

# plt.plot(x, targets.get_result(), label="Target", linewidth=2)     # 紅色預設會自動分配


# diff  
plt.plot([diff_region*(x+1) for x in range(len(diff))], diff, label=diff_name, linewidth=2) # diff 
# avg
avg = sum(diff)/len(diff)
plt.plot([diff_region*(x+1) for x in range(len(diff))], [avg]*len(diff), label="avg", linewidth=2) # diff 
print("avg:", avg)


plt.title("OHR difference")       # 標題
plt.xlabel("cum_Request")       # x軸標註
plt.ylabel("Hitrate")               # y軸標註

# plt.legend(loc='upper right')  # 顯示圖例（標註曲線是什麼）
plt.legend(loc='lower right', bbox_to_anchor=(1, 0))
plt.tight_layout()

plt.grid(True)  # 可選：顯示網格讓曲線更好讀

plt.show()












