import torch
import torch.nn as nn
from torch.quasirandom import SobolEngine

class sobal_embedding(nn.Module):
    def __init__(self, num_buckets, emb_dim):
        super().__init__()
        sobol = SobolEngine(dimension=emb_dim, scramble=True)
        weight = sobol.draw(num_buckets) * 2 - 1
        weight = torch.nn.functional.normalize(weight, p=2, dim=1)
        self.embedding = nn.Embedding.from_pretrained(weight, freeze=True)

    def forward(self, o_ids):
        return self.embedding(o_ids)