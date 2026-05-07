from utils.deque import deque

#obj類別
class Cache_obj():
    def __init__(self,o_id,o_size):
        self.o_id=int(o_id)
        self.o_size=int(o_size)
    def __eq__(self, other):    # dict需實作 
        return self.o_id == other.o_id
    def __hash__(self):         # dict需實作
        return hash(self.o_id)

#cache類別      
class Cache(deque):
    def __init__(self,cache_size):
        super().__init__()
        self.size=cache_size #快取大小
        self.used=0#已用空間
        self.cache_dict={}
    @property
    def free(self):
        return self.size-self.used

    def insert_left(self, val):
        super().insert_left(val)
        self.used+=val.o_size
        self.cache_dict[val]=self.head #指向node物件
        

    def insert_right(self, val):
        super().insert_right(val)
        self.used+=val.o_size
        self.cache_dict[val]=self.tail #指向node物件
        
    
    def pop_left(self):
        victim=super().pop_left()
        del self.cache_dict[victim]
        self.used-=victim.o_size
        
    
    def pop_right(self):
        victim=super().pop_right()
        del self.cache_dict[victim]
        self.used-=victim.o_size
        
# deque沒有從中驅逐功能 此處新增    
    def pop_obj(self,val):
        node=self.cache_dict[val]
        if node.prev:
            node.prev.nxt=node.nxt
        else:
            self.head=node.nxt
        
        if node.nxt:
            node.nxt.prev=node.prev
        else:
            self.tail=node.prev
        del self.cache_dict[val]
        self.used-=val.o_size
#實作in 功能
    def __contains__(self,val):
        return val in self.cache_dict



