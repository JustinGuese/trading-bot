#!/bin/bash
python train.py data/BTCUSD\=X_1d_all.csv data/BTCUSD\=X_1d_test.csv --model-name btcusd1d_30 --pretrained --episode-count 1
git add -A
git commit -m "training done"
git push origin master

