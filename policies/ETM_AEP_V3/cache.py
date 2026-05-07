from utils.MinHeap import MinHeap

#obj類別
class cache_obj():
    def __init__(self,o_id,o_size,o_pop,time):
        self.o_id=str(o_id)
        self.o_size=int(o_size)
        self.o_pop=o_pop
        self.insert_time = time
        self.orignal_val = self.o_val  # 用於追蹤原始價值

    @property
    def o_val(self):
        return self.o_pop / self.o_size 

    def __lt__(self, other):
        return self.o_val < other.o_val
    def __gt__(self, other):
        return self.o_val > other.o_val
    def __eq__(self, other):    # dict需實作 
        return self.o_id == other.o_id
    def __hash__(self):         # dict需實作
        return hash(self.o_id)

#cache類別  
class Cache(MinHeap):
    def __init__(self,cache_size):
        super().__init__()
        self.size=cache_size #快取大小
        self.used=0 #已用空間
        self.obj_count=0
        self.pop_count=0
        # self.cache_dict={}

    @property
    def remaining_space(self):
        return self.size-self.used

    def get_cached_obj(self, obj):
        return self.heap[self.index_dict[obj]]

    def decay_pop(self, time, L):#L 是未來L步的那個參數
        for i in range(len(self.heap)):
            obj = self.heap[i]
            d_time = time - obj.insert_time
            obj.o_pop = obj.o_pop * (d_time/L)
        self.heapify()





    def insert(self, val):
        super().insert(val)

        self.used+=val.o_size
        self.obj_count+=1

        # self.cache_dict[val]=val

    def pop_min(self):
        victim=super().pop_min()

        self.used-=victim.o_size
        self.obj_count-=1

        # del self.cache_dict[victim]
        return victim
    
    def pop_obj(self, val):
        # assert val in self.cache_dict, "Object not in cache"
        assert val in self, "Object not in cache"
        
        if len(self.heap) == 1:
            obj=self.heap.pop()
            del self.index_dict[obj]

            self.used -= obj.o_size
            self.obj_count -= 1

            # del self.cache_dict[val]
            return obj
        
        # obj=self.cache_dict[val]
        obj = self.get_cached_obj(val)
        
        #val與最後一個交換
        i=self.index_dict[val]
        self._swap(i, len(self.heap)-1)
        
        #移除val
        self.heap.pop()
        del self.index_dict[val]

        if i>0 and self.heap[i] < self.heap[(i-1)//2]:
            self._bubble_up(i)
        else:
            self._trickle_down(i)

        self.used-=obj.o_size
        self.obj_count -= 1

        # del self.cache_dict[val]

        return obj
    
##update_obj 可能會需要更新cache_val  ?
    def update_obj(self,val):
        # assert val in self.cache_dict, "Object not in cache"
        assert val in self, "Object not in cache"
        i = self.index_dict[val]
        #更新cache_val
        old_obj = self.get_cached_obj(val)
        
        #更新物件
        self.heap[i]=val

        #更新物件在heap中的位置
        parent = (i - 1) // 2
        if i > 0 and self.heap[i] < self.heap[parent]:
            self._bubble_up(i)
        else:
            self._trickle_down(i)
        
#實作in 功能
    def __contains__(self,val):
        # return val in self.cache_dict
        return val in self.index_dict
    

    