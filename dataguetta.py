import yfinance as yf
import pandas as pd
import numpy as np

STOCK = "GOOG"
data = yf.download("GOOG",period="max",interval="1d")

msk = np.random.rand(len(data)) < 0.9 # 90 10% split
train = data[msk]
tmp = data[~msk]
msk = np.random.rand(len(tmp)) < 0.5 # 50 50 test val split
test = tmp[msk]
val = tmp[~msk]

#i need
# Date,Open,High,Low,Close,Adj Close,Volume
# 2010-08-12,17.799999,17.900000,17.389999,17.600000,17.600000,691000

train.to_csv("data/%s_train.csv"%STOCK)
test.to_csv("data/%s_test.csv"%STOCK)
val.to_csv("data/%s_validation.csv"%STOCK)

print(train.head())
print(train.shape,data.shape)