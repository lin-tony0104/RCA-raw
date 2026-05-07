import sys

if len(sys.argv)==2:
    trace=sys.argv[1]
    try:
        open("../trace/"+trace,'r')
        print()
    except Exception as e:
        print("讀檔失敗! \n",e)
else:
    print("參數格式錯誤! \n python get_trace_info.py [trace name]")



result="INFO_"+trace+".txt"

#所蒐集的資訊
total_requests=0
unique_objects=0
working_set_size=0

with open("../trace/"+trace, 'r') as f:
    obj_size_map = {}
    for line in f:
        if total_requests % 1000000 == 0 and total_requests>0:
            print("Processed requests:", total_requests)
        temp = line.split()
        o_id = int(temp[0])
        o_size = int(temp[1])
        total_requests += 1
        obj_size_map[o_id] = o_size

    unique_objects = len(obj_size_map)
    working_set_size = sum(obj_size_map.values())

with open("../trace/"+result, 'w') as wf: 
    wf.write("Trace: "+trace+"\n")
    wf.write("Total Requests: "+str(total_requests)+"\n")
    wf.write("Unique Objects: "+str(unique_objects)+"\n")
    wf.write("Working Set Size (bytes): "+str(working_set_size)+"\n")