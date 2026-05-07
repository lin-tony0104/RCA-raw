'''
cache_system.py負責下列項目:
    1. 使用指定的 admission_policy 和 eviction_policy 達成cache功能

    2. 主程式統一處理完資料 傳給副程式使用 副程式取要用的即可

    3.新見解:只在cache有被更動到的時候更新
'''

from policies.RCA_noClip.lib.dequedict import DequeDict

class cache:
    class cache_Entry:
         def __init__(self,o_block,o_size,o_reuse,hit):
            self.o_block=o_block
            self.o_size=o_size
            self.o_reuse=o_reuse
            self.hit=hit

              
    def __init__(self,admit_policy,evict_policy,cache_size):
        self.admit_policy=admit_policy 
        self.evict_policy=evict_policy 
        self.cache_size=cache_size
        self.main_cache=DequeDict()#真實快取    {oblock:entry}
        

        #test
        self.admit_policy.init(self.evict_policy)
        
        #DEBUG_init
        self.DEBUG_requests=0        
        self.DEBUG_hitCount=0      
        self.DEBUG_RegionHitCount=0
        self.DEBUG_evict=0
        self.DEBUG_not_admit=0
        self.DEBUG_addToCache=0
        self.DEBUG_CACHE_INFO="" #在run.py設定此值



    '''看有需要什麼'''
    def request_in(self,obj):
        self.admit_policy.request(obj)
        self.evict_policy.request(obj)

    def hit(self,obj):
        self.admit_policy.hit(obj)
        self.evict_policy.hit(obj)
        #DEBUG
        self.DEBUG_hitCount+=1
        self.DEBUG_RegionHitCount+=1

    def miss(self,obj):
        self.admit_policy.miss(obj)
        self.evict_policy.miss(obj)

    def admit(self,obj):
        self.admit_policy.admit(obj)
        self.evict_policy.admit(obj)



    def evict(self):
        victim=self.evict_policy.evict()
        self.admit_policy.evict(victim)#evict_update
        del self.main_cache[victim.o_block]

        #DEBUG
        self.DEBUG_evict+=1

    def addToCache(self,obj):
        self.main_cache[obj.o_block]=obj
        self.admit_policy.addToCache(obj)
        self.evict_policy.addToCache(obj)

        #DEBUG
        self.DEBUG_addToCache+=1

    def not_admit(self,obj):
        self.evict_policy.not_admit(obj)
        self.admit_policy.not_admit(obj)
    
        #DEBUG
        self.DEBUG_not_admit+=1
    
    def end(self,obj):
        self.evict_policy.end(obj)
        self.admit_policy.end(obj)


    def DEBUG_show_useTime(self):
        miss=self.DEBUG_requests-self.DEBUG_hitCount
        admit=miss-self.DEBUG_not_admit
        hit_rate=round(100*self.DEBUG_hitCount/self.DEBUG_requests,2)
        region_hit_rate=round(100*self.DEBUG_RegionHitCount/1000000,2)
        
        self.DEBUG_RegionHitCount=0
        message="INFO: "+self.DEBUG_CACHE_INFO\
        +"  req:"+ str(self.DEBUG_requests)\
        +"  hit_rate:"+str(hit_rate)\
        +"  region_hit_rate:"+str(region_hit_rate)\
        +"  admit:"+str(admit)\
        +"  not_admit:"+str(self.DEBUG_not_admit)\
        +"  cache_count:"+str(self.main_cache.cached_count)
        
        admit_message=self.admit_policy.GET_DEBUG_MESSAGE()
        evict_message=self.evict_policy.GET_DEBUG_MESSAGE()

        result=(message+"  "+admit_message+"  "+evict_message)
        # print("req:",self.DEBUG_requests," hit:",self.DEBUG_hitCount," miss:",miss," evict:",self.DEBUG_evict," admit:",admit," not_admit:",self.DEBUG_not_admit," addToCache:",self.DEBUG_addToCache," hit_rate:",hit_rate, "      ===INFO===  ",self.DEBUG_CACHE_INFO)
        return result




    #====主要部分====
    def requests(self,o_block,o_size,o_reuse):
        self.DEBUG_requests+=1

        hit = (o_block in self.main_cache)

        req_obj=self.main_cache[o_block] if hit else self.cache_Entry(o_block,o_size,o_reuse,hit)
        req_obj.hit=hit
        req_obj.o_reuse=o_reuse
        

        self.request_in(req_obj)                #============(request)============

        if hit:
            self.hit(req_obj)                   #============(hit)============

            
        else:
            self.miss(req_obj)                  #============(miss)============
            if self.admit_policy.judge(req_obj):#==(judge)==
                self.admit(req_obj)             #============(admit)============
                while(o_size>self.cache_size-self.main_cache.cached_count):
                    self.evict()                #============(evict)============
                self.addToCache(req_obj)        #============(addToCache)============ 
            else:
                self.not_admit(req_obj)         #============(not_admit)============
        self.end(req_obj)                       #============(end)============


        # # self.evict_policy.DEBUG_show_para()
        # if not self.DEBUG_requests%1000000:
        #     self.DEBUG_show_useTime()
        #     # self.evict_policy.DEBUG()
        return hit
        