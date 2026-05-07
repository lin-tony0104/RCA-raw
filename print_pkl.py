import pickle
import sys
from pprint import pprint




if len(sys.argv)==2:
    try:
        exp=sys.argv[1]
        open("experiments/"+exp+"/config.json",'r')
    except Exception as e:
        print(e)
        sys.exit()
else:
    print("參數格式:")
    print("python ETM_labeling.py [experiment_name]")
    sys.exit()
# exp_name=sys.argv[1]

pkl_File="experiments/"+exp+"/result/result.pkl"

with open(pkl_File, "rb") as f:
    data = pickle.load(f)

pprint(data)