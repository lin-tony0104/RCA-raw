from policies.BasePolicy import BasePolicy
from policies.LeCaR.dequedict import DequeDict
from policies.LeCaR.heapdict import HeapDict
import numpy as np


class LeCaR_policy(BasePolicy):

    class LeCaR_Entry:
        def __init__(self, oblock, freq=1, time=0,osize=1):
            self.oblock = oblock
            self.freq = freq
            self.time = time
            self.evicted_time = None
            self.osize=osize
        def __lt__(self, other):
            if self.freq == other.freq:
                return self.oblock < other.oblock
            return self.freq < other.freq

        def __repr__(self):
            return "(o={}, f={}, t={})".format(self.oblock, self.freq,
                                               self.time)


    def __init__(self, config):
        np.random.seed(123)
        self.time = 0
        #self.debug=[]
        self.cache_size = config['cache_size']
        self.lru = DequeDict()
        self.lfu = HeapDict()

        self.history_size = config['cache_size']
        self.lru_hist = DequeDict()
        self.lfu_hist = DequeDict()

        self.initial_weight = 0.5

        self.learning_rate = 0.45

        self.discount_rate = 0.005**(1 / self.cache_size)

        self.W = np.array([self.initial_weight, 1 - self.initial_weight],
                          dtype=np.float32) #[W_LRU,W_LFU]


    def __contains__(self, oblock):
        return oblock in self.lru


    def addToCache(self, oblock, freq,osize):
        x = self.LeCaR_Entry(oblock, freq, self.time,osize)
        self.lru[oblock] = x
        self.lfu[oblock] = x

    def getLRU(self, dequeDict):
        return dequeDict.first()

    def getHeapMin(self):
        return self.lfu.min()

    def getChoice(self):
        return 0 if np.random.rand() < self.W[0] else 1

#---------------------以下是LeCaR功能、以上是---------------------

    def addToHistory(self, x, policy):#給定lru,lfu

        policy_history = None
        if policy == 0:
            policy_history = self.lru_hist
        else:
            policy_history = self.lfu_hist

        while(x.osize>(self.history_size-policy_history.cached_count)):
            evicted = self.getLRU(policy_history)
            del policy_history[evicted.oblock]
        policy_history[x.oblock] = x




    def evict(self):
        lru = self.getLRU(self.lru)
        lfu = self.getHeapMin()

        evicted = lru
        policy = self.getChoice()


        if policy == 0:
            evicted = lru
            evicted.evicted_time = self.time#用來算reqgret的
            self.addToHistory(evicted, policy)#先判斷有沒有滿 才放入histroy

            #delete from cache
            del self.lru[evicted.oblock]
            del self.lfu[evicted.oblock]
        else:
            evicted = lfu
            evicted.evicted_time = self.time#
            self.addToHistory(evicted, policy)#先判斷有沒有滿 才放入histroy

            #delete from cache
            del self.lru[evicted.oblock]
            del self.lfu[evicted.oblock]

        

        return evicted.oblock, policy


    def hit(self, oblock):
        x = self.lru[oblock]
        x.time = self.time

        self.lru[oblock] = x

        x.freq += 1
        self.lfu[oblock] = x


    # def adjustWeights(self, rewardLRU, rewardLFU):
    #     reward = np.array([rewardLRU, rewardLFU], dtype=np.float32)
    #     self.W = self.W * np.exp(self.learning_rate * reward)
    #     self.W = self.W / np.sum(self.W)

    #     if self.W[0] >= 0.99:
    #         self.W = np.array([0.99, 0.01], dtype=np.float32)
    #     elif self.W[1] >= 0.99:
    #         self.W = np.array([0.01, 0.99], dtype=np.float32)

    def adjustWeights(self,policy,reward): #W=[w_lru,w_lfu]
        if policy=="LRU":
            self.W[1]=self.W[1]*np.exp(self.learning_rate*reward)    
        elif policy=="LFU":
            self.W[0]=self.W[0]*np.exp(self.learning_rate*reward)
        
        self.W[0] = self.W[0] / (self.W[0]+self.W[1])
        self.W[1] = 1-self.W[0]

        if self.W[0] >= 0.99:
            self.W = np.array([0.99, 0.01], dtype=np.float32)
        elif self.W[1] >= 0.99:
            self.W = np.array([0.01, 0.99], dtype=np.float32)



    def miss(self, oblock,osize):
        evicted = None
        freq = 1
        policy="None"
        reward=0
        if oblock in self.lru_hist:
            policy="LRU"
            entry = self.lru_hist[oblock]
            freq = entry.freq + 1
            del self.lru_hist[oblock]
            reward=-(self.discount_rate**(self.time - entry.evicted_time))#為什麼加負號
            
        elif oblock in self.lfu_hist:
            policy="LFU"
            entry = self.lfu_hist[oblock]
            freq = entry.freq + 1
            del self.lfu_hist[oblock]
            reward=-(self.discount_rate**(self.time - entry.evicted_time))#為什麼加負號

        #更新權重
        self.adjustWeights(policy,reward)
        
        while(osize>self.cache_size-self.lru.cached_count):
            evicted, policy = self.evict()

        self.addToCache(oblock, freq,osize)

        return evicted


    def request(self, oblock,osize,o_features=None):
        oblock = int(oblock)
        osize = int(osize)
        miss = True
        evicted = None

        self.time += 1

        if oblock in self:
            miss = False
            self.hit(oblock)
        else:
            evicted = self.miss(oblock,osize)
        #self.debug.append(self.lru.cached_count)

        return not miss
