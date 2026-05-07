import matplotlib.pyplot as plt
from collections import defaultdict
import sys
# 物件熱門度從大牌到小的圖形


if len(sys.argv)==2:
    try:
        trace=sys.argv[1]
    except Exception as e:
        print(e)
        sys.exit()
else:
    print("參數格式:")
    print("python obj_pop.py [trace_file]")
    sys.exit()


# wiki2018 = "D:/all_Trace/ASC-IP/wiki2018"

req_count = defaultdict(int)


counter = 0
with open(trace, 'r') as f:
    for line in f:
        counter += 1
        if counter % 1000000 == 0:
            print("processed:", counter)

        temp = line.split()
        o_block = temp[0]
        req_count[o_block] += 1

sorted_req = sorted(req_count.values(), reverse=True)
ranks = list(range(1, len(sorted_req) + 1))

plt.figure()
plt.plot(ranks, sorted_req)
plt.xscale('log')
plt.yscale('log')
plt.xlabel("Object Rank")
plt.ylabel("Request Count")
plt.title(f"Popularity Rank-Frequency Plot ({trace})")
plt.grid()
plt.savefig("popularity_rank_frequency.png", dpi=300)
plt.show()