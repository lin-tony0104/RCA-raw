from policies.BasePolicy import BasePolicy
from policies.AdaptSize.adaptsize import AdaptSizeCache


class Adaptsize_policy(BasePolicy):
    def __init__(self, config):
        self.cache = AdaptSizeCache()
        self.cache.set_size(config["cache_size"])
        

    def request(self, o_id, o_size, o_features=None):
        o_id = int(o_id)
        o_size = int(o_size)
        hit = self.cache.lookup(o_id, o_size)
        if not hit:
            self.cache.admit(o_id, o_size)

        return hit, ""


