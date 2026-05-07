'''
run.py完成下列項目:
1. CMD介面+功能
2. 選擇演算法
'''


from policies.BasePolicy import BasePolicy

from policies.RCA_noClip.cache_system import cache
import matplotlib.pyplot as plt

#evict_policy
from policies.RCA_noClip.evict_policy.lru import LRU
#admit_policy
from policies.RCA_noClip.admit_policy.size_reuse_distance_v12 import SRDb_v12




class RCA_policy(BasePolicy):
    def __init__(self,config):
        cache_size=config["cache_size"]
        self.region_size=config["region_size"]
        self.alpha=config["alpha"]
        self.alg = cache(SRDb_v12(cache_size),LRU(cache_size),cache_size)


    def request(self, lba, size,other_feature):
        hit = self.alg.requests(int(lba),int(size),-1)
        return hit ,""