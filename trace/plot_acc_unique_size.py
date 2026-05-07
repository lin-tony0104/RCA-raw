#把trace的累積相異物件size畫成圖
import numpy as np
import matplotlib.pyplot as plt
import time 
#參數
trace = "wiki2018"
sample_stride = 1_000  # 取樣頻率
cache_size = 2_748_779_070
runs = 2_000_000 #紀錄幾個就結束
#==========================
seen =set()
cum_size = 0
cum_size_list=[]
start = time.time()


with open(trace,'r') as f:
    for i, line in enumerate(f):
        o_id, o_size = line.split()
        o_id, o_size =int(o_id), int(o_size)
        if o_id not in seen:
            seen.add(o_id)
            cum_size += int(o_size)
        if i % sample_stride ==0:
            cum_size_list.append(cum_size)
        if len(cum_size_list) >= runs:
            break

        if i % 1_000_000 ==0:
            t = time.time() - start
            print(f"Processed {i} lines. time comsumed: {t:.2f} sec")
    
x = [i*sample_stride for i in range(len(cum_size_list))]
y = cum_size_list
plt.plot(x,y, label="Unique Object Size", linewidth=2)
plt.plot(x,[cache_size]*len(x), label="Cache Size", linewidth=2)  

plt.xlabel("Req_num")
plt.ylabel("Byte")
plt.title(f"Cumulative Unique Object Size\nTrace: {trace}")
plt.grid(True)
plt.show()