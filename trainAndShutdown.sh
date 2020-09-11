#!/bin/bash
python train.py data/EURUSD=X_1m_train.csv data/EURUSD=X_1m_test.csv --model-name eurusd1mTA

# shutdown in the end
/sbin/shutdown -h now