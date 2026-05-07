trace="wiki2018_2M_for01FOO"


with open(trace, 'r') as f:
    counter_1=0
    counter_req = 0 
    for line in f:
        temp = line.split()
        label = temp[2]
        counter_1 += int(label)
        counter_req +=1
    
    print(f"1_ratio: {counter_1/counter_req},  total_req_num: {counter_req}")
    
