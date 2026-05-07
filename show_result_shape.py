import json
import matplotlib.pyplot as plt
import pickle
import sys
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
    print("python ETM_labeling.py [exp1, exp2, ...]")
    sys.exit()
# exp_name = "exampleLRU"

exp_names=[]
OHRs=[]
cum_hits_rates =[]
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
        OHRs.append(result_data["cum_hits_rate"][-1])
        cum_hits_rates.append(result_data["cum_hits_rate"])
        regions.append(result_data["region"])

    print(exp+" OHR:", OHRs[-1])
# print("BHR:", BHR)


for exp_name, OHR, cum_hits_rate, region in zip(exp_names, OHRs, cum_hits_rates, regions):
    print(exp_name+" cum_hits_rate_len: ", len(cum_hits_rate))



