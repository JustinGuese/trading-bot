import os
import math
import logging

import numpy as np


def sigmoid(x):
    """Performs sigmoid operation
    """
    try:
        if x < 0:
            return 1 - 1 / (1 + math.exp(x))
        return 1 / (1 + math.exp(-x))
    except Exception as err:
        print("Error in sigmoid: " + err)


def get_state(datan, t, n_days):
    """Returns an n-day state representation ending at time t
    """
    blocks = []
    for feature in datan.columns:
        data = list(datan[feature])
        if len(data) == 0:
            raise Exception("DATA IS ZERO!!! CHECK YFINANCE OUTPUT")
        d = t - n_days + 1
        block = data[d: t + 1] if d >= 0 else -d * [data[0]] + data[0: t + 1]  # pad with t0
        blocks.append(block)
    res = []
    for i in range(n_days - 1):
        columns = []
        for block in blocks:
            c1 = sigmoid(block[i + 1] - block[i])
            columns.append(c1)
        res.append(columns)
    resp = np.array(res).T
    return resp
