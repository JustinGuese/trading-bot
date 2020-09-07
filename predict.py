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

from docopt import docopt

from trading_bot.agent import Agent
from trading_bot.methods import evaluate_model
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
    data = get_live_stock_data(eval_stock,period)
    window_size = 10
    # Single Model Evaluation
    if model_name is not None:
        print("Modelname: ",model_name)
        agent = Agent(window_size, pretrained=True, model_name=model_name)
        profit, _ = evaluate_model(agent, data, window_size, True)
        # show_eval_result(model_name, profit, initial_offset)
        
    # Multiple Model Evaluation
    else:
        print("MODEL NAME MISSISNg")


if __name__ == "__main__":
    args = docopt(__doc__)

    eval_stock = args["<eval-stock>"]
    model_name = args["--model-name"]
    period = args["--period"]

    coloredlogs.install(level="DEBUG")
    switch_k_backend_device()

    try:
        main(eval_stock, model_name, period)
    except KeyboardInterrupt:
        print("Aborted")
