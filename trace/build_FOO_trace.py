import sys

if len(sys.argv)>=2:
    traces=sys.argv[1:]
else:
    print("參數格式錯誤! \n python build_FOO_trace.py [trace name1], [trace name2] ...")
    sys.exit()



# trace="Twitter50"

#所蒐集的資訊
# cut_size = 10000000

for trace in traces:
    with open("../trace/"+trace, 'r') as f, open("../trace/"+trace+"_forFOO", 'w') as wf:
        counter=0
        for i,line in enumerate(f):
            r = str(i)+" "+line
            counter+=1
            wf.write(r)
            if counter % 1000000 == 0 and counter>0:
                print("Processed requests:", counter)

