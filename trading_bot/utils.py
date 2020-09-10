import os
import math
import logging

import pandas as pd
import numpy as np

import keras.backend as K

import yfinance as yf

from sklearn.preprocessing import MinMaxScaler
from ta import add_all_ta_features
import joblib


# Formats Position
format_position = lambda price: ('-$' if price < 0 else '+$') + '{0:.2f}'.format(abs(price))


# Formats Currency
format_currency = lambda price: '${0:.2f}'.format(abs(price))


def show_train_result(result, val_position, initial_offset):
    """ Displays training results
    """
    if val_position == initial_offset or val_position == 0.0:
        logging.info('Episode {}/{} - Train Position: {}  Val Position: USELESS  Train Loss: {:.4f}'
                     .format(result[0], result[1], format_position(result[2]), result[3]))
    else:
        logging.info('Episode {}/{} - Train Position: {}  Val Position: {}  Train Loss: {:.4f})'
                     .format(result[0], result[1], format_position(result[2]), format_position(val_position), result[3],))


def show_eval_result(model_name, profit, initial_offset):
    """ Displays eval results
    """
    if profit == initial_offset or profit == 0.0:
        logging.info('{}: USELESS\n'.format(model_name))
    else:
        logging.info('{}: {}\n'.format(model_name, format_position(profit)))


def get_stock_data(stock_file):
    """Reads stock data from csv file
    """
    # Datetime = Date if non hourly
    try:
        df = pd.read_csv(stock_file,parse_dates=['Datetime'], index_col=['Datetime'])
    except ValueError: # bc yfinance day = Date, intraday datetime
        df = pd.read_csv(stock_file,parse_dates=['Date'], index_col=['Date'])
    # todo cut out weekend (non trading day)
    df = df[df.index.dayofweek < 5]
    df = df[df.columns[1:]] # drop date
    filename = 'scalers/%s.scaler.gz'%stock_file.split("data/")[1].lower()
    if "train" in stock_file:
        scaler = MinMaxScaler((0,100)) # bigger values = stronger training
        dfscaled = scaler.fit_transform(df)
        dfscaled = pd.DataFrame(dfscaled,columns=df.columns)
        # write scaler to file for later
        joblib.dump(scaler,filename)
    elif "test" in stock_file:
        newname = filename.replace("test","train")
        scaler = joblib.load(newname)
        dfscaled = scaler.transform(df)
        dfscaled = pd.DataFrame(dfscaled,columns=df.columns)

    # add ta features
    # dfscaled = add_all_ta_features(dfscaled,open="Open", high="High", low="Low", close="Close", volume="Volume")

    
    return dfscaled

def get_live_stock_data(stockname,interval):
    """Reads stock data from csv file
    """
    period = "20d"
    if "h" in interval:
        period = "20h"
    elif "5m" in interval:
        period = "100m"
    elif "1m" in interval:
        period = "50m"
    df = yf.download(stockname,period=period,interval=interval)
    df = df[df.columns[1:]] # drop date
    name = None
    if "EUR" in stockname:
        name = stockname.lower() + "_"+interval + "_train.csv.scaler.gz"
    else:
        name = stockname.lower() + "_"+interval + "_train.csv.scaler.gz"
    filename = 'scalers/%s' % name
    scaler = joblib.load(filename)
    dfscaled = scaler.transform(df)
    
    dfscaled = pd.DataFrame(dfscaled,columns=df.columns)
    dfscaled["realprice"] = df["Close"].values
    # add ta features
    # dfscaled = add_all_ta_features(dfscaled,open="Open", high="High", low="Low", close="Close", volume="Volume")

    print(dfscaled.shape)
    return dfscaled

def switch_k_backend_device():
    """ Switches `keras` backend from GPU to CPU if required.

    Faster computation on CPU (if using tensorflow-gpu).
    """
    # is really faster.
    if K.backend() == "tensorflow":
        logging.debug("switching to TensorFlow for CPU")
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
