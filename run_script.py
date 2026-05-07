import subprocess

# 可用policy列表：
# TinyLFU, LRU, AdaptSize, FOO, 
# RCA, RCA_aging, RCA_EMACacheCost, RCA_noClip, RCA_noInit, RCA_prob, RCA_val , RCA_noInit_noClip
# RCA2, RCA2_prob, RCA2_val, RCA2_Clip, RCA2_Init ,RCA2_EMACacheCost, RCA2_aging

cache_size ="005"
trace ="wiki"
policy="RCA2_Init"


exps = [f"{cache_size}_{trace}_{policy}_seg{i}" for i in range(10)]


for exp in exps:
    # run() 會等待程序執行完畢才繼續下一個迴圈
    print(f"正在執行: {exp}...")
    subprocess.run(["python", "run.py", exp], check=True)

print("所有腳本已按順序執行完畢！")
