import struct
import sys

if len(sys.argv) != 2:
    print("get_trace_len.exe <source>")
    sys.exit(1) 
else:
    trace = sys.argv[1]



with open(trace,"rb") as s:
    counter = 0
    for _ in s:
        counter += 1
        if counter % 1_000_000 == 0:
            print(f"processed: {counter}")

    print(f"Total number of records: {counter}")    

