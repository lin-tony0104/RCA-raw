from MinHeap import MinHeap


class cache_obj():
    def __init__(self,o_id,o_size,o_pop,time):
        self.o_id=str(o_id)
        self.o_size=int(o_size)
        self.o_pop=int(o_pop)
        self.o_val=self.o_pop/self.o_size
        self.insert_time = time
        self.orignal_val = self.o_val  # 用於追蹤原始價值


    def __lt__(self, other):
        return self.o_val < other.o_val
    def __gt__(self, other):
        return self.o_val > other.o_val
    def __eq__(self, other):    # dict需實作 
        return self.o_id == other.o_id
    def __hash__(self):         # dict需實作
        return hash(self.o_id)
    


obj_0 = cache_obj(0,1,0,0) # o_val = 0
obj_1 = cache_obj(1,1,10,0) # o_val = 10
obj_2 = cache_obj(2,1,20,0) # o_val = 20
obj_3 = cache_obj(3,1,30,0) # o_val = 30
obj_4 = cache_obj(4,1,40,0) # o_val = 40
  

heap = MinHeap()
heap.insert(obj_0)
heap.insert(obj_1)
heap.insert(obj_2)
heap.insert(obj_3)
heap.insert(obj_4)




r = [obj.o_id for obj in heap.heap]
print("origin: ",r)
obj_0.o_val = 50
obj_1.o_val = 40
obj_2.o_val = 30
obj_3.o_val = 20
obj_4.o_val = 10
heap.heapify()

r = [obj.o_id for obj in heap.heap]
print("heapified: ",r)

r= []
r.append(heap.heap[heap.index_dict[obj_0]].o_id)
r.append(heap.heap[heap.index_dict[obj_1]].o_id)
r.append(heap.heap[heap.index_dict[obj_2]].o_id)
r.append(heap.heap[heap.index_dict[obj_3]].o_id)
r.append(heap.heap[heap.index_dict[obj_4]].o_id)
print(r) #指向的id仍是對的


