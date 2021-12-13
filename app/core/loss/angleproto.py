import torch
import torch.nn as nn
import torch.nn.functional as F
# import time, pdb
import numpy as np

def accuracy(output, target, topk=(1, )):
    """Computes the precision@k for the specified values of k"""
    maxk = max(topk)
    batch_size = target.size(0)

    _, pred = output.topk(maxk, 1, True, True)
    pred = pred.t()
    correct = pred.eq(target.view(1, -1).expand_as(pred))

    res = []

    for k in topk:
        correct_k = correct[:k].reshape(-1).float().sum(0, keepdim=True)
        res.append(correct_k.mul_(100.0 / batch_size))
    return res



class LossFunction(nn.Module):
    def __init__(self, init_w=10.0, init_b=-5.0, **kwargs):
        super(LossFunction, self).__init__()

        self.test_normalize = True

        self.w = nn.Parameter(torch.tensor(init_w))
        self.b = nn.Parameter(torch.tensor(init_b))
        self.criterion = torch.nn.CrossEntropyLoss()

        # print('Initialised AngleProto')

    def forward(self, x, label=None):

        assert x.size()[1] >= 2

        out_anchor = torch.mean(x[:, 1:, :], 1)
        out_positive = x[:, 0, :]
        stepsize = out_anchor.size()[0]

        cos_sim_matrix = F.cosine_similarity(
            out_positive.unsqueeze(-1),
            out_anchor.unsqueeze(-1).transpose(0, 2))
        torch.clamp(self.w, 1e-6)
        cos_sim_matrix = cos_sim_matrix * self.w + self.b

        label = torch.from_numpy(np.asarray(range(0, stepsize))).cuda()
        nloss = self.criterion(cos_sim_matrix, label)
        prec1, _ = accuracy(cos_sim_matrix.detach().cpu(),
                            label.detach().cpu(),
                            topk=(1, 5))

        return nloss, prec1
