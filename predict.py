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

from docopt import docopt
from etoro import etoroHandler

from trading_bot.agent import Agent
from trading_bot.methods import predict_next
from trading_bot.utils import (
    get_stock_data,
    get_live_stock_data,
    format_currency,
    format_position,
    show_eval_result,
    switch_k_backend_device
)


def main(eval_stock, model_name, period,money,waitTime):
    """ Evaluates the stock trading bot.
    Please see https://arxiv.org/abs/1312.5602 for more details.

    Args: [python eval.py --help]
    """    
    eh = etoroHandler()
    pos = eh.getPositionDict()
    print(pos)
    # todo get current portfolio
    run = True
    boughtAT = 0
    prof = 0
    while run:
        try:
            prof = 0
            yfname = eval_stock
            if "EUR" in eval_stock: # if forex
                yfname = eval_stock + "=X"
            data = get_live_stock_data(yfname,period)
            window_size = 10
            # Single Model Evaluation
            if model_name is not None:
                print("Modelname: ",model_name)
                agent = Agent(window_size, pretrained=True, model_name=model_name)
                act = predict_next(agent, data, window_size)
                # show_eval_result(model_name, profit, initial_offset)
            # Multiple Model Evaluation
            else:
                print("MODEL NAME MISSISNg")
            # act on decision
            crntPrice = data["realprice"].values[-1]
            resp = None
            eh.updateHandler()
            if act == 1: # buy
                if eval_stock.lower() not in pos:
                    resp = eh.buy(eval_stock.lower(),money,1,crntPrice*1.2,crntPrice*0.9)
                    print(resp)
                    boughtAT = crntPrice
                else:
                    resp= " buy, but have position, so stay"
            elif act == 2: # sell
                if eval_stock.lower() in pos:
                    prof = boughtAT - crntPrice
                    print("SELLINGGGG ",eval_stock," profit: ",prof)
                    boughtAT = 0
                    resp = eh.close(eval_stock.lower())
                else:
                    print("not selling bc position not thjere ",eval_stock)
                    resp = "not selling bc i have no positions in ",eval_stock

            else:
                print("HOLD")
            with open('logs/%s_log.txt'%eval_stock,'a') as f:
                txt = "stock:%s, action:%s, profit:%.2f , api-response:%s, time:%s\n"%(eval_stock,act,prof,resp, datetime.datetime.now())
                f.write(txt)
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
