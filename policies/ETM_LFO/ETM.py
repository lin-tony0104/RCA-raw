import torch
import torch.nn as nn
# from utils.TCN import TemporalConvNet
from pytorch_tcn import TCN

import collections

class Local_ID_Mapper:
    def __init__(self, window_size):
        self.K = window_size
        self.window = collections.deque()  # 模擬長度為 K 的滑動視窗
        # 核心映射與計數
        self.id_to_local = {}              # Stream_ID -> Local_ID
        self.ref_count = collections.Counter() # Stream_ID 在視窗內的出現次數
        # 可用的 Local_ID 池 (使用 Queue 達到 O(1) 取用與回收)
        self.free_locals = collections.deque(range(window_size+1))  # K: window_size, 1: curr_id
        
    def get_local_id(self, o_id):
        # 1. 處理進入視窗的 ID
        if o_id not in self.id_to_local:
            # 如果是新 ID 且不在當前視窗，分配一個 local_id
            if not self.free_locals:
                # 正常情況下，只要 window_size >= 視窗內獨特 ID 數，這不會發生
                raise RuntimeError("視窗內獨特 ID 數量超過上限 K+1")
            self.id_to_local[o_id] = self.free_locals.popleft()
        # 更新計數與視窗
        self.ref_count[o_id] += 1
        self.window.append(o_id)
        assigned_local = self.id_to_local[o_id]
        # 2. 處理移出視窗的 ID (滑動視窗邏輯)    K+1 -> K
        if len(self.window) > self.K:
            out_id = self.window.popleft()
            self.ref_count[out_id] -= 1
            
            # 當該 ID 在當前視窗完全消失時，回收其 local_id
            if self.ref_count[out_id] == 0:
                freed_local = self.id_to_local.pop(out_id)
                self.free_locals.append(freed_local) # 回收到隊列末尾
                del self.ref_count[out_id] # 清理記憶體
        return assigned_local


class MLP(nn.Module):
    def __init__(self, input_dim, hidden_dims, output_dim=1):
        super().__init__()
        dims = [input_dim] + hidden_dims + [output_dim]
        layers = []
        for i in range(len(dims) - 1):
            layers.append(nn.Linear(dims[i], dims[i + 1]))
            if i < len(dims) - 2:
                layers.append(nn.ReLU())
        self.net = nn.Sequential(*layers)
    
    def forward(self,x):
        return self.net(x)
        

class Embedding(nn.Module):
    def __init__(self, num_buckets, emb_dim):
        super().__init__()
        W = torch.randn(num_buckets, emb_dim)
        W = torch.nn.functional.normalize(W, dim=1)
        self.embedding = nn.Embedding.from_pretrained(W, freeze=True)

    def forward(self, o_ids):
        return self.embedding(o_ids)



class ETM(nn.Module):
    def __init__(self, config):
        super().__init__()
        #init mlp, tcn, embedding
        
        self.embedding = Embedding(
                config['K']+1,
                config['emb_dim']
            )
        self.tcn = TCN(
                num_inputs = config['emb_dim'],
                num_channels = config['tcn_channels'],
                kernel_size = 10,
                dilations = [10**(i+1) for i in range(len(config['tcn_channels']))],
            )
        self.mlp=MLP(
            config['tcn_channels'][-1] + config['emb_dim']+2, # +2 for obj_size_norm, cache_free_norm
            config['mlp_hidden_dims'],
            output_dim=1
        )

        # for eval
        mlp_feature_width = config['tcn_channels'][-1] + config['emb_dim']+2
        self.register_buffer("mlp_feature_buffer", torch.zeros((1, 1, mlp_feature_width)))
    
    def forward(self, hist_ids, curr_ids, obj_size_norm, cache_free_norm): #hist_ids.shape=[batch,seq_len] , curr_ids.shape=[batch,pred_len]
        if self.training:
            obj_size_norm = obj_size_norm.unsqueeze(-1) 
            cache_free_norm = cache_free_norm.unsqueeze(-1) 

            pred_len = curr_ids.shape[1]
            hist_emb = self.embedding(hist_ids)                 # shape [Batch, seq_len, emb_dim]
            hist_emb = hist_emb.permute(0, 2, 1)                # shape [Batch, emb_dim, seq_len]
            tcn_out = self.tcn(hist_emb,inference= (not self.training))[:, :, -pred_len:]      # shape [Batch, out_channel, pred_len]  #train/eval會改變行為
            tcn_out = tcn_out.permute(0, 2, 1)                  # shape [Batch, pred_len, out_channel]
            curr_emb = self.embedding(curr_ids)                 # shape [Batch, pred_len, emb_dim]

            mlp_feature = torch.cat([tcn_out, curr_emb, obj_size_norm, cache_free_norm], dim=-1)
            pred = self.mlp(mlp_feature)                  # shape [Batch, pred_len, 1]  
            return pred #不需要squeeze 因為通常loss_fn是需要最後一個維度的
        else:
            obj_size_norm = obj_size_norm.unsqueeze(-1) 
            cache_free_norm = cache_free_norm.unsqueeze(-1) 

            pred_len = curr_ids.shape[1]
            hist_emb = self.embedding(hist_ids)                 # shape [Batch, seq_len, emb_dim]
            hist_emb = hist_emb.permute(0, 2, 1)                # shape [Batch, emb_dim, seq_len]
            tcn_out = self.tcn(hist_emb,inference=True)[:, :, -pred_len:]      # shape [Batch, out_channel, pred_len]  #train/eval會改變行為
            tcn_out = tcn_out.permute(0, 2, 1)                  # shape [Batch, pred_len, out_channel]
            curr_emb = self.embedding(curr_ids)                 # shape [Batch, pred_len, emb_dim]
            
            w1, w2, w3, w4 = tcn_out.shape[-1], curr_emb.shape[-1], obj_size_norm.shape[-1], cache_free_norm.shape[-1]
            self.mlp_feature_buffer[0, 0, :w1] = tcn_out
            self.mlp_feature_buffer[0, 0, w1 : w1+w2] = curr_emb
            self.mlp_feature_buffer[0, 0, w1+w2 : w1+w2+w3] = obj_size_norm
            self.mlp_feature_buffer[0, 0, w1+w2+w3 : w1+w2+w3+w4] = cache_free_norm
            pred = self.mlp(self.mlp_feature_buffer)                  # shape [Batch, pred_len, 1]  
            return pred #不需要squeeze 因為通常loss_fn是需要最後一個維度的    


    def reset_tcn_buffer(self):
        self.tcn.reset_buffers()
            