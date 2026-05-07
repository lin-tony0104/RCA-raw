from utils.MinHeap import MinHeap

#obj類別
class cache_obj():
    def __init__(self,o_id,o_size,o_val):
        self.o_id=str(o_id)
        self.o_size=int(o_size)
        self.o_val=int(o_val)
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
        self.cache_dict={}
    @property
    def remaining_space(self):
        return self.size-self.used
    @property
    def cache_val(self):
        if self.obj_count == 0:
            return 0
        return self.val_count/self.obj_count
    
    def insert(self, val):
        super().insert(val)

        self.used+=val.o_size
        self.obj_count+=1
        self.val_count+=val.o_val

        self.cache_dict[val]=val

    def pop_min(self):
        victim=super().pop_min()

        self.used-=victim.o_size
        self.obj_count-=1
        self.val_count-=victim.o_val

        del self.cache_dict[victim]
        return victim
    
    def pop_obj(self, val):
        assert val in self.cache_dict, "Object not in cache"
        if len(self.heap) == 1:
            obj=self.heap.pop()

            self.used -= obj.o_size
            self.obj_count -= 1
            self.val_count -= obj.o_val

            del self.cache_dict[val]
            return obj
        
        obj=self.cache_dict[val]

        
        i=self.index_dict[val]
        self.heap[i]=self.heap.pop()  # Move the last element to the position of the removed object
        if i>0 and self.heap[i] < self.heap[(i-1)//2]:
            self._bubble_up(i)
        else:
            self._trickle_down(i)

        self.used-=obj.o_size
        self.obj_count -= 1
        self.val_count -= obj.o_val 

        del self.cache_dict[val]
        del self.index_dict[val]
        return obj
    
##update_obj 可能會需要更新cache_val  ?
    def update_obj(self,val):
        assert val in self.cache_dict, "Object not in cache"
        i = self.index_dict[val]
        #更新cache_val
        self.val_count += (val.o_val - self.cache_dict[val].o_val)
        self.cache_dict[val] = val

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
        return val in self.cache_dict

    

if __name__ == "__main__":
    # 建立 cache
    cache = Cache(cache_size=100)

    # 建立 cache_obj
    a = cache_obj("A", 10, 5)   # val=5
    b = cache_obj("B", 20, 2)   # val=2（最小）
    c = cache_obj("C", 15, 8)   # val=8

    print("=== Insert Test ===")
    cache.insert(a)
    cache.insert(b)
    cache.insert(c)

    # heap 應該是：B(2), A(5), C(8)
    print("Heap order:", [obj.o_id for obj in cache.heap])
    print("Used:", cache.used)  # 10+20+15 = 45
    print("Obj count:", cache.obj_count)
    print("Val count:", cache.val_count)

    print("\n=== pop_min Test ===")
    victim = cache.pop_min()
    print("pop_min victim:", victim.o_id)  # 應為 B

    # 剩 A(5), C(8)
    print("Heap order:", [obj.o_id for obj in cache.heap])
    print("Used:", cache.used)
    print("Obj count:", cache.obj_count)
    print("Val count:", cache.val_count)

    print("\n=== pop_obj Test ===")
    cache.pop_obj(a)  # 移除 A
    print("After pop_obj(A):", [obj.o_id for obj in cache.heap])
    print("Used:", cache.used)
    print("Obj count:", cache.obj_count)
    print("Val count:", cache.val_count)

    print("\n=== Update Test ===")
    # 插入新物件再測 update
    d = cache_obj("D", 10, 3)
    cache.insert(d)

    print("Before update:", [(obj.o_id, obj.o_val) for obj in cache.heap])

    # 將 C 的 val 改得更小 → 應 bubble 到 root
    c.o_val = 1
    cache.update_obj(c)

    print("After update:", [(obj.o_id, obj.o_val) for obj in cache.heap])

    print("\n=== Contains Test ===")
    print("C in cache?", c in cache)
    print("A in cache?", a in cache)

    print("\n=== All tests completed ===")
