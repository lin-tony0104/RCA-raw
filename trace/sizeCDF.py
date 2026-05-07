import matplotlib.pyplot as plt
from collections import defaultdict
import sys
# 物件大小數量 由小到達累積分布

if len(sys.argv)==2:
    try:
        trace=sys.argv[1]
    except Exception as e:
        print(e)
        sys.exit()
else:
    print("參數格式:")
    print("python sizeCDF.py [trace_file]")
    sys.exit()


# wiki2018 = "D:/all_Trace/ASC-IP/wiki2018"

seen = set()
size_count = defaultdict(int)

counter = 0
with open(trace, 'r') as f:
    for line in f:
        counter += 1

        temp = line.split()
        o_block = temp[0]
        o_size = int(temp[1])

        # unique object
        if o_block not in seen:
            seen.add(o_block)
            size_count[o_size] += 1


        if counter % 10000000 == 0:
            
            print("processed:", counter)
print("unique objects:", len(seen))

# ===== 計算 CDF =====
sorted_sizes = sorted(size_count.keys())

total = sum(size_count.values())
cum = 0

x = []
y = []

for s in sorted_sizes:
    cum += size_count[s]
    x.append(s)
    y.append(cum / total)

# ===== 畫圖 =====
plt.figure()
plt.plot(x, y)

# 很重要：size 通常差很多
plt.xscale('log')

plt.xlabel("Object Size")
plt.ylabel("CDF")
plt.title(f"Object Size CDF ({trace})")
plt.grid()

# ===== 存圖 =====
# plt.savefig("object_size_cdf.png", dpi=300)

# ===== 顯示 =====
plt.show()