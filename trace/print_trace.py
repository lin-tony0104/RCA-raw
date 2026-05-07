trace="Twitter50"

with open("../trace/"+trace, 'r') as f:
    counter=0
    for line in f:
        if counter>=10:
            break
        print(line)
        counter+=1


