trace="wiki2018_forETM"
result_trace="wiki2018_forETM_pop"
with open("../trace/"+trace, 'r') as f:
    counter=0
    for line in f:
        if counter>=10:
            break
        print(line)
        counter+=1


