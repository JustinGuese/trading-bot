"""
Script for evaluating Stock Trading Bot.

Usage:
  eval.py <eval-stock> [--model-name=<model-name>] [--period=<model-name>]

Options:
  --model-name=<model-name>     Name of the pretrained model to use (will eval all models in `models/` if unspecified).
  --period=<period>             Fuck.
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


def main(eval_stock, model_name, period):
    """ Evaluates the stock trading bot.
    Please see https://arxiv.org/abs/1312.5602 for more details.

    Args: [python eval.py --help]
    """    
    eh = etoroHandler()
    pos = eh.getPositionDict()
    print(pos)
    # todo get current portfolio
    run = True
    while True:
        try:
            data = get_live_stock_data(eval_stock,period)
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
            crntPrice = data["Close"][-1]
            resp = None
            eh.updateHandler()
            print(eh.getWatchlist())
            debug = True
            if act == 1 or debug: # buy
                resp = eh.buy(eval_stock.lower(),10000,1,crntPrice*1.2,crntPrice*0.9)
                print(resp)
            elif act == 2: # sell
                if eval_stock in pos:
                    print("SELLINGGGG")
                else:
                    print("FUGGGGGG",pos)
            else:
                print("HOLD")
            with open('%s_log.txt'%eval_stock,'a') as f:
                txt = "%s %s %s %s"%(eval_stock,act,resp, datetime.datetime.now())
                f.write(txt)
            time.sleep(57)

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

    coloredlogs.install()
    switch_k_backend_device()

    try:
        main(eval_stock, model_name, period)
    except KeyboardInterrupt:
        print("Aborted")
