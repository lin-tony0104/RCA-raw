import pickle
import time
class OHR():
    def __init__(self, region):
        self.region = region
        self.regionHit = []
        self.regionReq = []
        
        self.req=0
        self.total_hit=0
        self.temp_req=0
        self.temp_hit=0


        
    def append(self, hit):
        self.req+=1
        self.temp_req+=1
        self.temp_hit+=hit
        if self.req%self.region==0:
            self.regionReq.append(self.temp_req)
            self.regionHit.append(self.temp_hit)
            
            self.total_hit+=self.temp_hit
            self.temp_hit= 0
            self.temp_req = 0

    def get_OHR(self):
        return round(self.total_hit/self.req,4)
    
    def get_segOHR(self):
        return round(self.regionHit[-1]/self.regionReq[-1],4)





class BHR():
    def __init__(self, region):
        self.region = region
        self.regionHitByte = []
        self.regionByte = []
        
        self.req=0
        self.total_hit_byte=0
        self.total_req_byte=0
        self.req_byte=0
        self.hit_byte=0

    def append(self, hit, o_size):
        self.req+=1
        self.req_byte+=o_size
        if hit:
            self.hit_byte+=o_size
        if self.req%self.region==0:
            self.regionHitByte.append(self.hit_byte)
            self.regionByte.append(self.req_byte)
            
            self.total_hit_byte+=self.hit_byte
            self.total_req_byte+=self.req_byte
            self.hit_byte=0
            self.req_byte=0
    
    def get_BHR(self):
        return round(self.total_hit_byte/self.total_req_byte,4)
    
    def get_segBHR(self):
        return round(self.regionHitByte[-1]/self.regionByte[-1],4)



class CacheEvaluator():
    def __init__(self,config, exp_name):
        self.exp_name=exp_name
        self.verbose=config["verbose"]#秀細節
        self.region=config["region"]
        self.warmup=config["warmup"]
        self.requests=0
        self.ohr=OHR(self.region)
        self.bhr=BHR(self.region)
        self.start = time.time()    

    def record(self,hit,o_size,message=""):
        o_size=int(o_size)
        self.requests+=1        
        self.ohr.append(hit)
        self.bhr.append(hit,o_size)
        
        if not self.requests%self.region:
            if self.verbose:
                t=time.time()-self.start 
                

                print("exp: "+self.exp_name+" req: ",self.requests ," OHR: ",self.ohr.get_OHR() ," segOHR: ",self.ohr.get_segOHR(), " time: ",round(t,4),"  ",message)
            


    
    def save_result(self):
        save_data={
            "region":self.region,
            'wall_time': time.time() - self.start,

            "ohr_regionReq": self.ohr.regionReq,
            "ohr_regionHit": self.ohr.regionHit,
            "bhr_regionReqByte": self.bhr.regionByte,
            "bhr_regionHitByte": self.bhr.regionHitByte
        }

        with open("experiments/"+self.exp_name+"/result/result.pkl","wb") as f:
            pickle.dump(save_data,f)