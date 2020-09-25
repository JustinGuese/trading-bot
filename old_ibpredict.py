"""
Script for evaluating Stock Trading Bot.

Usage:
  eval.py <eval-stock> [--model-name=<model-name>] [--period=<model-name>] [--money=<money>] [--wait=<wait]

Options:
  --model-name=<model-name>     Name of the pretrained model to use (will eval all models in `models/` if unspecified).
  --period=<period>             timeframe according to model minute, hour, day, ...
  --money=<money>               How much to invest
  --wait=<wait>                 Seconds to wait between invests 86400 (daily)
"""

import os
import coloredlogs
import sys
import time
import datetime
import pandas as pd
import pickle


from docopt import docopt

from trading_bot.agent import Agent
from trading_bot.methods import predict_next
from trading_bot.utils import (
    get_stock_data,
    format_currency,
    format_position,
    show_eval_result,
    switch_k_backend_device
)

## get ib data
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order

import threading
import time

class IBapi(EWrapper, EClient):
	def __init__(self):
		EClient.__init__(self, self)
		self.data = [] #Initialize variable to store candle

	def historicalData(self, reqId, bar):
		#print(f'Time: {bar.date} Close: {bar.close}')
		self.data.append([bar.date, bar.open,bar.high,bar.low,bar.close])
		
def run_loop():
	app.run()

app = IBapi()
app.connect('127.0.0.1', 4002, 123)

def saveOrderIds(orderIds):
    with open('orderids.pickle', 'wb') as handle:
        pickle.dump(orderIds,handle)
def loadOrderIds():
    with open('orderids.pickle', 'rb') as handle:
        ord = pickle.load(handle)
    return ord

try:
    orderIds = loadOrderIds()
except FileNotFoundError:
    orderIds = dict()
    saveOrderIds(orderIds)

#Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=False)
api_thread.start()

time.sleep(1) #Sleep interval to allow time for connection to server

#Create contract object
eurusd_contract = Contract()
eurusd_contract.symbol = 'EUR'
eurusd_contract.secType = 'CASH'
eurusd_contract.exchange = 'IDEALPRO'
eurusd_contract.currency = 'USD'
name = eurusd_contract.symbol + eurusd_contract.currency
#Request historical candles
# maximum 1 min -> 6d
#app.reqHistoricalData(1, eurusd_contract, '', '1 M', '1 min', 'BID', 0, 2, False, [])

#time.sleep(5) #sleep to allow enough time for data to be returned

def getPositions():
    '''
    NOT good method, keep current positions in csv
    '''
    try:
        pos = pd.read_csv("interactiveBrokers_Positions.csv")
    except FileNotFoundError:
        pos = pd.DataFrame()
        pos.to_csv("interactiveBrokers_Positions.csv")
    return pos

def writePositions(pos):
    pos.to_csv("interactiveBrokers_Positions.csv")

def main(eval_stock, model_name, period,money,waitTime):
    """ Evaluates the stock trading bot.
    Please see https://arxiv.org/abs/1312.5602 for more details.

    Args: [python eval.py --help]
    """    
    LEVERAGE = 20
    pos = getPositions()
    print("crnt positions", pos)
    # todo get current portfolio
    run = True
    boughtAT = 0
    prof = 0

    isShort = False



    while run:
        try:
            resp = None
            pos = getPositions()
            print("current positions: ",pos)
            prof = 0
            app.reqHistoricalData(1, eurusd_contract, '', '60 S', '1 min', 'BID', 0, 2, False, [])
            time.sleep(5)
            data = pd.DataFrame(app.data, columns=['Datetime', 'Open',"High","Low","Close"])
            data['Datetime'] = pd.to_datetime(data['Datetime'],unit='s') 
            if len(data) == 0:
                print(data)
                raise Exception("NO DATAAAA")
            # need to change data for input
            print(data)
            data = data[data.columns[1:]] # leave out datetime
            window_size = 10
            # Single Model Evaluation
            print("Modelname: ",model_name)
            agent = Agent(window_size, pretrained=True, model_name=model_name)
            act = predict_next(agent, data, window_size)
            # act on decision
            print(type(data["Close"]))
            crntPrice = data["Close"][len(data["Close"])-1] # wtf not -1?
            print("current price is: ",crntPrice)

            def createOrder(money,crntPrice):
                order = Order()
                order.action = None
                order.orderType = "MKT"
                order.totalQuantity = int(money/crntPrice)
                return order
                
            allowShort = False
            if act == 1: # buy
                if eval_stock.lower() not in pos.columns:
                    order = createOrder(money,crntPrice)
                    order.action = "SELL"
                    print("Long Buy bc no position: ",pos,eval_stock.lower())
                    print("TYPE OF DAMN ORDERID",type(orderIds))
                    if orderIds.get(eval_stock.lower()) == None:
                        # should be case in first episode
                        orderIds[eval_stock.lower()] = 1
                    else:
                        orderIds[eval_stock.lower()] = orderIds[eval_stock.lower()] +1 # add one
                    saveOrderIds(orderIds)
                    resp = app.placeOrder(orderIds[eval_stock.lower()], eurusd_contract,
                             order)
                    print(resp)
                    pos[name] = order.totalQuantity
                    print(order.totalQuantity,money,crntPrice)
                    writePositions(pos)
                    boughtAT = crntPrice
                    isShort = False
                elif eval_stock.lower() in pos.columns and isShort and allowShort:
                    prof = -(boughtAT - crntPrice)
                    print("Short SELLINGGGG ",eval_stock," profit: ",prof)
                    boughtAT = 0
                    #resp = eh.close(eval_stock.lower())
                else:
                    resp= " buy, but have position, so stay"
            elif act == 2: # sell
                if eval_stock.lower() in pos and not isShort:

                    prof = boughtAT - crntPrice
                    print("Long SELLINGGGG ",eval_stock," profit: ",prof)
                    boughtAT = 0
                    order = createOrder(money,crntPrice)
                    order.action = "BUY"
                    print("Long sell",pos,eval_stock.lower())
                    id = orderIds[eval_stock.lower()]
                    resp = app.placeOrder(id, eurusd_contract,
                             order)
                    print(resp)
                    pos[name] = 0
                    writePositions(pos)
                elif eval_stock.lower() not in pos.columns and allowShort:
                    print("Short Buy bc no position: ",pos,eval_stock.lower())
                    #resp = eh.sell(eval_stock.lower(),money,LEVERAGE,crntPrice*.8,crntPrice*1.1)
                    print(resp)
                    boughtAT = crntPrice
                    isShort = True
                else: # we have a short position
                    print("not selling bc position not thjere ",eval_stock)
                    resp = "not selling bc i have no positions in ",eval_stock

            else:
                print("HOLD")
            with open('logs/%s_log.txt'%eval_stock,'a') as f:
                txt = "stock:%s, action:%s, profit:%.2f , api-response:%s, time:%s\n"%(eval_stock,act,prof,resp, datetime.datetime.now())
                f.write(txt)
            print(waitTime,"s waiting... ")
            time.sleep(waitTime-3)

        except KeyboardInterrupt:
            print('Interrupted')
            run = False
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)


if __name__ == "__main__":
    args = docopt(__doc__)

    eval_stock = args["<eval-stock>"]
    model_name = args["--model-name"]
    period = args["--period"]
    money = int(args["--money"])
    waitTime = int(args["--wait"])

    coloredlogs.install()
    switch_k_backend_device()

    try:
        main(eval_stock, model_name, period,money,waitTime)
    except KeyboardInterrupt:
        print("Aborted")
