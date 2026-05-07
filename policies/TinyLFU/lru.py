from .cache import Cache,Cache_obj


class lru():
    def __init__(self,cache_size):
        self.cache = Cache(cache_size)

    def __contains__(self,obj):
        return obj in self.cache
    
    def get_tail(self):
        return self.cache.tail.val # obj
    
    def set(self,obj):
        if obj in self.cache:
            self.cache.pop_obj(obj)
            self.cache.insert_left(obj)
        else:
            while(self.cache.free < obj.o_size):
                self.cache.pop_right()
            self.cache.insert_left(obj)
