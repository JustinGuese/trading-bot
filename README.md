#install (new)

conda env create -f environment.yml
OR: update an existing environment: > conda env update --file environment.yml

## train
python train.py data/TRAINDATA data/TESTDATA --model-name STOCKPERIOD(QQQ1h)

# 96.037,94 USD

## live trading with etoro

1. run etoro server: https://github.com/JustinGuese/etoro-api
2. > python predict.py GOOG --model-name GOOG1d_50 --period 1d --money 1000 --wait 86400
match period in model with timeframe

python predict.py GOOG --model-name GOOG1d_50 --period 1d --money 1000 --wait 86400
example for minute data
python predict.py EURUSD=X --model-name eurusd1m_50 --period 1m --money 1000 --wait 60
-> todo: scaler is weirdly named, needs to be manually changed now

wait seconds to wait between trades

if it says "asset not found" add with addAssets2Etoro script
--------------
OLD:

# Overview

This project implements a Stock Trading Bot, trained using Deep Reinforcement Learning, specifically Deep Q-learning. Implementation is kept simple and as close as possible to the algorithm discussed in the paper, for learning purposes.

## Introduction

Generally, Reinforcement Learning is a family of machine learning techniques that allow us to create intelligent agents that learn from the environment by interacting with it, as they learn an optimal policy by trial and error. This is especially useful in many real world tasks where supervised learning might not be the best approach due to various reasons like nature of task itself, lack of appropriate labelled data, etc.

The important idea here is that this technique can be applied to any real world task that can be described loosely as a Markovian process.

## Approach

This work uses a Model-free Reinforcement Learning technique called Deep Q-Learning (neural variant of Q-Learning).
At any given time (episode), an agent abserves it's current state (n-day window stock price representation), selects and performs an action (buy/sell/hold), observes a subsequent state, receives some reward signal (difference in portfolio position) and lastly adjusts it's parameters based on the gradient of the loss computed.

There have been several improvements to the Q-learning algorithm over the years, and a few have been implemented in this project:

- [x] Vanilla DQN
- [x] DQN with fixed target distribution
- [x] Double DQN
- [ ] Prioritized Experience Replay
- [ ] Dueling Network Architectures

## Results

Trained on `GOOG` 2010-17 stock data, tested on 2019 with a profit of $1141.45 (validated on 2018 with profit of $863.41):

![Google Stock Trading episode](./extra/visualization.png)

You can obtain similar visualizations of your model evaluations using the [notebook](./visualize.ipynb) provided.

## Some Caveats

- At any given state, the agent can only decide to buy/sell one stock at a time. This is done to keep things as simple as possible as the problem of deciding how much stock to buy/sell is one of portfolio redistribution.
- The n-day window feature representation is a vector of subsequent differences in Adjusted Closing price of the stock we're trading followed by a sigmoid operation, done in order to normalize the values to the range [0, 1].
- Training is prefferably done on CPU due to it's sequential manner, after each episode of trading we replay the experience (1 epoch over a small minibatch) and update model parameters.

## Data

You can download Historical Financial data from [Yahoo! Finance](https://ca.finance.yahoo.com/) for training, or even use some sample datasets already present under `data/`.

## Getting Started

In order to use this project, you'll need to install the required python packages:

```bash
pip install -r requirements.txt
```

Now you can open up a terminal and start training the agent:

```bash
python train.py data/DAX_1h_train.csv data/DAX_1h_train.csv --strategy t-dqn --model-name="DAX1h"
```
REMEMBER changing the name according to the data used! otherwise it will overwrite

Once you're done training, run the evaluation script and let the agent make trading decisions:

```bash
python eval.py data/GOOG_2019.csv --model-name model_GOOG_50 --debug
```

predict:
python eval.py data/GOOG_1d_validation.csv --model-name model_GOOG_50

Now you are all set up!

## Acknowledgements

- [@keon](https://github.com/keon) for [deep-q-learning](https://github.com/keon/deep-q-learning)
- [@edwardhdlu](https://github.com/edwardhdlu) for [q-trader](https://github.com/edwardhdlu/q-trader)

## References

- [Playing Atari with Deep Reinforcement Learning](https://arxiv.org/abs/1312.5602)
- [Human Level Control Through Deep Reinforcement Learning](https://deepmind.com/research/publications/human-level-control-through-deep-reinforcement-learning/)
- [Deep Reinforcement Learning with Double Q-Learning](https://arxiv.org/abs/1509.06461)
- [Prioritized Experience Replay](https://arxiv.org/abs/1511.05952)
- [Dueling Network Architectures for Deep Reinforcement Learning](https://arxiv.org/abs/1511.06581)
