import matplotlib.pyplot as plt

# ===== 讀檔 =====
sizes = []
pops = []
counter=0
with open("wiki2018_forETM", "r") as f:
    for line in f:

        line = line.strip()
        if counter%100000==0:
            print(counter)

        obj_id, size, pop = line.split()
        pops.append(float(pop))
        counter+=1

        if counter > 10000000:
            break
req=range(len(pops))
# ===== 畫 scatter plot =====
plt.figure()
plt.scatter(req, pops)
plt.xlabel("req")
plt.ylabel("popularity")
plt.title("Size vs Popularity")
plt.show()
