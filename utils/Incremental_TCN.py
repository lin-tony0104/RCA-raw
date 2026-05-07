"""
原論文code : https://github.com/locuslab/TCN/blob/master/TCN/tcn.py
無修改 只加入註解
"""

"""
dilation:擴張率，卷積層的取樣間隔
channels: 輸入的單個元素維度(神經網路要用多少維度來傳遞資訊)
batch_size: 批次大小(一次丟進TCN的序列數量， 不是指序列長度，而是多少個一樣長度的序列)
"""
import torch
import torch.nn as nn
from torch.nn.utils import weight_norm

# chomp1d 用來將多餘的輸出切掉
# 由於conv1d的padding會左右都padding，會導致多算padding個結果，所以要將尾部多出來的切掉
class Chomp1d(nn.Module):
    def __init__(self, chomp_size):
        super(Chomp1d, self).__init__()
        self.chomp_size = chomp_size

    def forward(self, x):
        return x[:, :, :-self.chomp_size].contiguous() #格式:[barch_size, channel, length] 這是Conv1d的輸出格式   channel:元素的特徵維度, length: 序列長度

# 由 兩層卷積層和殘差連接組成 
class TemporalBlock(nn.Module):
    def __init__(self, n_inputs, n_outputs, kernel_size, stride, dilation, padding, dropout=0.2):
        super(TemporalBlock, self).__init__()

        #兩層卷積 目的是增強block表達能力 不然其實一層也能運作。
        self.conv1 = weight_norm(nn.Conv1d(n_inputs, n_outputs, kernel_size,
                                           stride=stride, padding=padding, dilation=dilation))
        self.chomp1 = Chomp1d(padding) #切掉多餘的輸出
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(dropout)

        self.conv2 = weight_norm(nn.Conv1d(n_outputs, n_outputs, kernel_size,
                                           stride=stride, padding=padding, dilation=dilation))
        self.chomp2 = Chomp1d(padding)
        self.relu2 = nn.ReLU()
        self.dropout2 = nn.Dropout(dropout)


        # # 組裝網路 / 由於iTCN需要 改在forward拆開寫
        # self.net = nn.Sequential(self.conv1, self.chomp1, self.relu1, self.dropout1,
        #                          self.conv2, self.chomp2, self.relu2, self.dropout2)
        
        # 殘差連接
        self.downsample = nn.Conv1d(n_inputs, n_outputs, 1) if n_inputs != n_outputs else None
        self.relu = nn.ReLU()

        # 初始化權重
        self.init_weights()


        # 推理時用的buffer , Double-Buffering方法避免cat
        self.receptive_field = (kernel_size-1)*dilation+1
        self.register_buffer("buffer1", torch.zeros(1, n_inputs, self.receptive_field*2))
        self.register_buffer("buffer2", torch.zeros(1, n_outputs, self.receptive_field*2))
        self.register_buffer("ptr", torch.zeros(1, dtype=torch.long))
        

    def init_weights(self):
        self.conv1.weight.data.normal_(0, 0.01)
        self.conv2.weight.data.normal_(0, 0.01)
        if self.downsample is not None:
            self.downsample.weight.data.normal_(0, 0.01)

    def forward(self, x):
        #layer1
        out = self.conv1(x)
        out = self.chomp1(out)
        out = self.relu1(out)
        out = self.dropout1(out)
        #layer2
        out = self.conv2(out)
        out = self.chomp2(out)
        out = self.relu2(out)
        out = self.dropout2(out)

        res = x if self.downsample is None else self.downsample(x)
        return self.relu(out + res)
    
    def forward_step(self,x):
        # update buffer
        p = self.ptr.item()
        max_len = self.buffer1.size(-1)//2

        #layer1
        self.buffer1[:,:,p]= x.squeeze(-1)
        self.buffer1[:,:,p+max_len]= x.squeeze(-1)
        buf = self.buffer1[:,:,p+1:p+max_len+1]
        out = torch.nn.functional.conv1d(buf, self.conv1.weight, self.conv1.bias,
                                         stride=self.conv1.stride, padding=0, dilation=self.conv1.dilation)
        # out = self.chomp1(out)
        out = self.relu1(out)
        out = self.dropout1(out)
        #layer2
        self.buffer2[:,:,p]= out.squeeze(-1)
        self.buffer2[:,:,p+max_len]= out.squeeze(-1)
        buf = self.buffer2[:,:,p+1:p+max_len+1]
        out = torch.nn.functional.conv1d(buf, self.conv2.weight, self.conv2.bias,
                                         stride=self.conv2.stride, padding=0, dilation=self.conv2.dilation)
        # out = self.chomp2(out)
        out = self.relu2(out)
        out = self.dropout2(out)

        res = x if self.downsample is None else self.downsample(x)
       
        self.ptr.add_(1).remainder_(max_len) # in_place: ptr = (ptr+1)%receptive_field , ptr = [0,max_len)
        return self.relu(out + res)

class TemporalConvNet(nn.Module):
    # def __init__(self, num_inputs, num_channels, kernel_size=2, dropout=0.2):
    def __init__(self, num_inputs, num_channels, kernel_size=10, dropout=0.2):
        super(TemporalConvNet, self).__init__()
        layers = []
        num_levels = len(num_channels) #卷積層層數，越大總結的感受野越大
        for i in range(num_levels):
            # dilation_size = 2 ** i #擴張率，卷積層的取樣間隔大小 (越上層越大，即感受野越大，可以對感受野資訊做總結)
            dilation_size = 10 ** i #擴張率，卷積層的取樣間隔大小 (越上層越大，即感受野越大，可以對感受野資訊做總結)
            in_channels = num_inputs if i == 0 else num_channels[i-1]
            out_channels = num_channels[i]
            layers += [TemporalBlock(in_channels, out_channels, kernel_size, stride=1, dilation=dilation_size,
                                     padding=(kernel_size-1) * dilation_size, dropout=dropout)]

        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)
    
    def forward_step(self,x):        
        output = x
        # self.network 裡面包含多個 TemporalBlock
        for layer in self.network:
            output = layer.forward_step(output)
        return output
