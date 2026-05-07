from utils.MinHeap import MinHeap

#obj類別
class cache_obj():
    def __init__(self,o_id,o_size,o_val,o_pop):
        self.o_id=str(o_id)
        self.o_size=int(o_size)
        self.o_val=int(o_val)
        self.o_pop=o_pop
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
        self.val_count=0
        self.pop_count=0
        # self.cache_dict={}

    @property
    def remaining_space(self):
        return self.size-self.used
    @property
    def cache_val(self):
        if self.obj_count == 0:
            return 0
        return self.val_count/self.obj_count
    def get_cached_obj(self, obj):
        return self.heap[self.index_dict[obj]]

    def insert(self, val):
        super().insert(val)

        self.used+=val.o_size
        self.obj_count+=1
        self.val_count+=val.o_val
        self.pop_count+=val.o_pop

        # self.cache_dict[val]=val

    def pop_min(self):
        victim=super().pop_min()

        self.used-=victim.o_size
        self.obj_count-=1
        self.val_count-=victim.o_val
        self.pop_count-=victim.o_pop

        # del self.cache_dict[victim]
        return victim
    
    def pop_obj(self, val):
        # assert val in self.cache_dict, "Object not in cache"
        assert val in self, "Object not in cache"
        
        if len(self.heap) == 1:
            obj=self.heap.pop()

            self.used -= obj.o_size
            self.obj_count -= 1
            self.val_count -= obj.o_val
            self.pop_count -= obj.o_pop

            # del self.cache_dict[val]
            return obj
        
        # obj=self.cache_dict[val]
        obj = self.get_cached_obj(val)
        
        i=self.index_dict[val]
        self.heap[i]=self.heap.pop()  # Move the last element to the position of the removed object
        if i>0 and self.heap[i] < self.heap[(i-1)//2]:
            self._bubble_up(i)
        else:
            self._trickle_down(i)

        self.used-=obj.o_size
        self.obj_count -= 1
        self.val_count -= obj.o_val 
        self.pop_count -= obj.o_pop 

        # del self.cache_dict[val]
        del self.index_dict[val]
        return obj
    
##update_obj 可能會需要更新cache_val  ?
    def update_obj(self,val):
        # assert val in self.cache_dict, "Object not in cache"
        assert val in self, "Object not in cache"
        i = self.index_dict[val]
        #更新cache_val
        old_obj = self.get_cached_obj(val)
        self.val_count += (val.o_val - old_obj.o_val)
        self.pop_count += (val.o_pop - old_obj.o_pop)
        
        # self.cache_dict[val] = val

        #更新位置
        parent = (i - 1) // 2
        if i > 0 and self.heap[i] < self.heap[parent]:
            self._bubble_up(i)
        else:
            self._trickle_down(i)
        
    def _bubble_up(self, i):
        parent = (i - 1) // 2
        if i > 0 and self.heap[i] < self.heap[parent]:
            val=self.heap[i]
            parent_val=self.heap[parent]
            self.index_dict[val],self.index_dict[parent_val]=parent,i
            self.heap[i], self.heap[parent] = self.heap[parent], self.heap[i]
            self._bubble_up(parent)           


    def _trickle_down(self, i):
        left = 2 * i + 1
        right = 2 * i + 2
        smallest = i
        
        if left < len(self.heap) and self.heap[left] < self.heap[smallest]:
            smallest = left
        if right < len(self.heap) and self.heap[right] < self.heap[smallest]:
            smallest = right
        
        if smallest != i:
            val=self.heap[i]
            smallest_val=self.heap[smallest]
            self.index_dict[val],self.index_dict[smallest_val]=smallest,i
            self.heap[i], self.heap[smallest] = self.heap[smallest], self.heap[i]

            self._trickle_down(smallest)        

        
#實作in 功能
    def __contains__(self,val):
        # return val in self.cache_dict
        return val in self.index_dict
    
# 可以改的點 目前看起來 這個avg_cache_val貌似是錯的，怎麼會是用obj_count來算平均，好像該用cached_size來算
    def get_avg_cache_value(self):
        if self.used==0:
            return 0
        return self.val_count/self.used
    
    def get_avg_cache_pop(self):
        if self.obj_count==0:
            return 0
        return self.pop_count/self.obj_count  