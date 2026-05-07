import torch
import torch.nn as nn

torch.manual_seed(42)

class rand_embedding(nn.Module):
    def __init__(self, num_buckets, emb_dim):
        super().__init__()
        W = torch.randn(num_buckets, emb_dim)
        W = torch.nn.functional.normalize(W, dim=1)

        self.embedding = nn.Embedding.from_pretrained(W, freeze=True)

    def forward(self, o_ids):
        return self.embedding(o_ids)
            