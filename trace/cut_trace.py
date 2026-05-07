import sys

if len(sys.argv)==3:
    try:
        trace=sys.argv[1]
        cut_size=int(sys.argv[2]) * 1000000
        open("../trace/"+trace,'r')
    except Exception as e:
        print("讀檔失敗! \n",e)
        sys.exit()
else:
    print("參數格式錯誤! \n python get_trace_info.py [trace name], [cut_size in million]")
    sys.exit()



# trace="Twitter50"

#所蒐集的資訊
# cut_size = 10000000
cut_size_M = str(cut_size // 1000000)
with open("../trace/"+trace, 'r') as f, open("../trace/"+trace+"_"+cut_size_M+"M", 'w') as wf:
    counter=0
    for line in f:
        counter+=1
        wf.write(line)
        if counter>=cut_size:
            break   
        if counter % 1000000 == 0 and counter>0:
            print("Processed requests:", counter)

