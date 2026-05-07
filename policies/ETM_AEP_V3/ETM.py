import torch
import torch.nn as nn
from utils.TCN import TemporalConvNet

class ETM(nn.Module):
    def __init__(self, config):
        super().__init__()
        #init mlp, tcn, embedding
        self.embedding = HashEmbedding(
                config['num_buckets'],
                config['emb_dim']
            )
        self.tcn = TemporalConvNet(
                config['emb_dim'],
                config['tcn_channels']
            )
        self.mlp=MLP(
            config['tcn_channels'][-1] + config['emb_dim'],
            config['mlp_hidden_dims'],
            output_dim=1
        )
    def forward(self, hist_ids, curr_ids): #hist_ids.shape=[batch,seq_len] , curr_ids.shape=[batch,pred_len]
        pred_len = curr_ids.shape[1]
        hist_emb = self.embedding(hist_ids)                 # shape [Batch, seq_len, emb_dim]
        hist_emb = hist_emb.permute(0, 2, 1)                # shape [Batch, emb_dim, seq_len]
        tcn_out = self.tcn(hist_emb)[:, :, -pred_len:]      # shape [Batch, out_channel, pred_len]
        tcn_out = tcn_out.permute(0, 2, 1)                  # shape [Batch, pred_len, out_channel]
        curr_emb = self.embedding(curr_ids)                 # shape [Batch, pred_len, emb_dim]
        pred = self.mlp(tcn_out, curr_emb)                  # shape [Batch, pred_len, 1]  
        return pred #不需要squeeze 因為通常loss_fn是需要最後一個維度的

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
    
    def forward(self, tcn_out, curr_emb):
        x = torch.cat([tcn_out, curr_emb], dim=-1)
        return self.net(x)
        
class HashEmbedding(nn.Module):
    def __init__(self, num_buckets, emb_dim):
        super().__init__()
        self.num_buckets = num_buckets
        self.embedding = nn.Embedding(num_buckets, emb_dim)

    def forward(self, o_ids):
        hashed = o_ids % self.num_buckets
        return self.embedding(hashed)