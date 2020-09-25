import os
import logging

import numpy as np

from tqdm import tqdm

from .utils import (
    format_currency,
    format_position
)
from .ops import (
    get_state
)


def train_model(agent, episode, data, ep_count=100, batch_size=32, window_size=10):
    total_profit = 0
    data_length = len(data) - 1

    agent.inventory = []
    avg_loss = []

    state = get_state(data, 0, window_size + 1)

    isShort = False
    hasPosition = False

    for t in tqdm(range(data_length), total=data_length, leave=True, desc='Episode {}/{}'.format(episode, ep_count)):        
        reward = 0
        COMMISSIONPCT = 0.00125 # the higher the more penalty for small trades
        next_state = get_state(data, t + 1, window_size + 1)

        # select an action
        action = agent.act(state)

       
        if not hasPosition:
            # BUY long position
            if action == 1:
                agent.inventory.append(data["Close"][t])
                isShort = False
                hasPosition = True
            # Buy short position
            elif action == 2:
                agent.inventory.append(data["Close"][t])
                isShort = True
                hasPosition = True
            # HOLD
            else:
                pass
        else: # if there is an open position
            # BUY - if it is a short close
            if action == 1 and isShort:
                bought_price = agent.inventory.pop(0)
                delta = -(data["Close"][t] - bought_price) 
                reward = delta - (COMMISSIONPCT * data["Close"][t])
                total_profit += reward
                hasPosition = False
            # buy sig and only long
            elif action == 1 and not isShort: 
                pass # dont buy new stocks
            # Sell signal if we have a long position
            elif action == 2 and not isShort:
                bought_price = agent.inventory.pop(0)
                delta = data["Close"][t] - bought_price
                reward = delta - (COMMISSIONPCT * data["Close"][t])
                total_profit += reward
                hasPosition = False
            # sell signal and have short
            elif action == 2 and isShort:
                pass # do not buy new ones yet
            # HOLD
            else:
                pass

        done = (t == data_length - 1)
        agent.remember(state, action, reward, next_state, done)

        if len(agent.memory) > batch_size:
            loss = agent.train_experience_replay(batch_size)
            avg_loss.append(loss)

        state = next_state

    if episode % 10 == 0:
        agent.save(episode)

    return (episode, ep_count, total_profit, np.mean(np.array(avg_loss)))


def predict_next(agent,data,window_size):
    state = get_state(data, len(data)-1, window_size + 1)
    # select an action
    action = agent.act(state)
    # if action == 1:
    #     print("BUY!")
    # elif action == 2: 
    #     print("SELL! (if you bought a stock")
    # else:
    #     print("HOLD")
    return action

def evaluate_model(agent, data, window_size, debug):
    total_profit = 0
    data_length = len(data) - 1

    history = []
    agent.inventory = []
    
    state = get_state(data, 0, window_size + 1)
    actionCollection = []
    print("Data lerngth",data_length)
    for t in range(data_length):        
        reward = 0
        print("eval dta size",data.shape)
        next_state = get_state(data, t + 1, window_size + 1)
        
        # select an action
        action = agent.act(state, is_eval=True)
        # BUY
        dec = None
        if action == 1:
            agent.inventory.append(data["Close"][t])

            history.append((data["Close"][t], "BUY"))
            dec = "BUY"
            if debug:
                logging.debug("Buy at: {}".format(format_currency(data["Close"][t])))
        
        # SELL
        elif action == 2 and len(agent.inventory) > 0:
            bought_price = agent.inventory.pop(0)
            delta = data["Close"][t] - bought_price
            reward = delta #max(delta, 0)
            total_profit += delta

            history.append((data["Close"][t], "SELL"))
            dec = "SELL"
            if debug:
                logging.debug("Sell at: {} | Position: {}".format(
                    format_currency(data["Close"][t]), format_position(data["Close"][t] - bought_price)))
        # HOLD
        else:
            history.append((data["Close"][t], "HOLD"))
            dec = "HOLD"

        done = (t == data_length - 1)
        agent.memory.append((state, action, reward, next_state, done))

        state = next_state
        actionCollection.append(action)
        if done:
            print("Final decision: ",dec, " at ",format_currency(data["Close"][t]))
            return total_profit, history, actionCollection
