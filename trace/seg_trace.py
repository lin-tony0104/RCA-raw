import sys
from itertools import islice

# source = "wiki2018"
# output_folder = "seg_wiki/"
# TRACE_LENGTH = 2800_000_000
# seg_size=2_000_000
# seg_num = 10
# stride = TRACE_LENGTH // seg_num # 抽樣間隔

# result_files = [open(f"{output_folder}wiki_seg{i}", 'w') for i in range(seg_num)]   # wiki_seg0, wiki_seg1, ..., wiki_seg9  

# source = "Twitter45"
# output_folder = "seg_twitter/"
# TRACE_LENGTH = 119_112_869
# seg_size=2_000_000
# seg_num = 10
# stride = TRACE_LENGTH // seg_num # 抽樣間隔

# result_files = [open(f"{output_folder}wiki_seg{i}", 'w') for i in range(seg_num)]   # wiki_seg0, wiki_seg1, ..., wiki_seg9  


# seg_trace.exe wiki seg_wiki/ 2800000000 2000000 10
if len(sys.argv) != 6:
    print("seg_trace.exe <source> <output_folder> <TRACE_LENGTH> <seg_size> <seg_num>")
    print("Example: seg_trace.exe wiki seg_wiki/ 2800000000 2000000 10")
    sys.exit(1) 
else:
    source = sys.argv[1]
    output_folder = sys.argv[2]
    TRACE_LENGTH = int(sys.argv[3])
    seg_size = int(sys.argv[4])
    seg_num = int(sys.argv[5])
    stride = TRACE_LENGTH // seg_num

    result_files = [open(f"{output_folder}{source}_seg{i}", 'w') for i in range(seg_num)]   # wiki_seg0, wiki_seg1, ..., wiki_seg9  




with open(source, "r") as s:
    for i,line in enumerate(s):
            seg_index = i // stride
            if seg_index >= seg_num:  # 超過最後一個 segment 就停止
                break

            file = result_files[seg_index]
            if i % stride < seg_size: # 在抽樣區間內
                file.write(line)

            if i % 1_000_000 == 0:
                 print(f"porcessed: {i}, seg_index: {seg_index}, ")

for file in result_files:
    file.close()