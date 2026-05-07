trace="wiki2018_2M_forFOO"


with open(trace, 'r') as f:
    counter_1=0
    counter_req = 0 
    for line in f:
        temp = line.split()
        label = float(temp[2])
        if label >=0.99:
            counter_1 += 1
        counter_req +=1
    
    print(f"1_ratio: {counter_1/counter_req},  total_req_num: {counter_req}")
    
