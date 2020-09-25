import backtrader as bt
import argparse
from trading_bot.agent import Agent
from trading_bot.methods import predict_next
import pandas as pd
import numpy as np
import time

parser = argparse.ArgumentParser(description='LiveTrading using Backtrader.')
parser.add_argument('--model-name',dest="modelname" ,
                   help='the name of the model as in models/', required=True)

args = parser.parse_args()
print("using model: ",args.modelname)
window_size = 10





agent = Agent(window_size, pretrained=True, model_name=args.modelname)
#act = predict_next(agent, data, window_size)

class rebot(bt.Strategy):

    params = (
        ('allowshorts',0),
        ('printLog',False)
    )

    def __init__(self):
        self.pos = 0
        self.data_live = False
        self.isShort = False
        

    def next(self):
        #for d in self.datas:
        d = self.datas[1]
        if self.data_live:
            # print(dn,self.crosses[d._name][0])

            pos = self.getposition(d).size
            # start 99.511 eur, 450 usd
            print("need to fix fucking IB becasue they are retarded fucktards",pos)
            pos += 944


            tmp = []
            # if len(d.open) < window_size:
            #     lookback = len(d.open)
            # else:
            #     lookback = window_size
            for i in range(1):
                tmp.append([d.open[-i],d.high[-i],d.low[-i],d.close[-i]])
            print(d.datetime.datetime(ago=0)," current numbers ",tmp[0])
            print("current positions: ",pos)
                
            crntData = pd.DataFrame(tmp, columns=['Open',"High","Low","Close"])
            #crntData['Datetime'] = pd.to_datetime(crntData['Datetime']) #,unit='s'

            action = predict_next(agent, crntData, window_size)
            #print(action)

            #time.sleep(10)
           
           
            
            if pos < 0:
                self.isShort = True
            elif pos > 0:
                self.isShort = False

            if not pos:  # no market / no orders
                if action == 1: # buy
                    self.buy(data=d)
                    print("buy bc no positions")
                    #self.isShort = False
                elif action == 2 and self.p.allowshorts == 1:
                    self.sell(data=d)
                    print("short bc no positions")
                    #self.isShort = True
                elif action == 2 and self.p.allowshorts == 0:
                    print("short, but skip bc short deactivated")
                
            else:
                if action == 1 and self.isShort and self.p.allowshorts == 1:
                    print("closing short")
                    self.close(data=d)
                    #self.buy(data=d)
                    #self.isShort = False
                elif action == 2 and not self.isShort:
                    print("long sell")
                    self.close(data=d)
                    #self.sell(data=d)
                    #self.isShort = True
                elif action == 1 and self.p.allowshorts == 0:
                    print("would be closing short, but cancel bc short deactivated")
        else: # d not live
            print("no live data, will wait ... ",d.datetime.datetime(ago=0))

    def notify_trade(self, trade):
        dt = self.data.datetime.date()
        if trade.isclosed and self.p.printLog:
            print('{} {} Closed: PnL Gross {}, Net {}'.format(
                                                dt,
                                                trade.data._name,
                                                round(trade.pnl,2),
                                                round(trade.pnlcomm,2)))
            
    def notify_data(self, data, status, *args, **kwargs):
        if status == data.LIVE:
            self.data_live = True
            print("yay Live data!")


# live part
cerebro = bt.Cerebro()
ibstore = bt.stores.IBStore(host='127.0.0.1', port=4003, clientId=35)
data = ibstore.getdata(dataname='EUR.USD-CASH-IDEALPRO',timeframe=bt.TimeFrame.Minutes,compression=1)
cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=1)

cerebro.broker = ibstore.getbroker()
cerebro.adddata(data)

# strategy
# cerebro.addstrategy(SmaCross, pfast=2,pslow=6) # not used bc opt strategy

cerebro.addstrategy(rebot) # https://backtest-rookies.com/2017/06/26/optimize-strategies-backtrader/


# cerebro.optstrategy(SmaCross, pfast=pfast,pslow=pslow) # https://backtest-rookies.com/2017/06/26/optimize-strategies-backtrader/

# add analyzer
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio') #  timeframe=bt.TimeFrame.Months
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DrawDown') #  timeframe=bt.TimeFrame.Months
cerebro.addanalyzer(bt.analyzers.Returns, _name='Returns') #  timeframe=bt.TimeFrame.Months
cerebro.addanalyzer(bt.analyzers.SQN, _name='SQN') #  timeframe=bt.TimeFrame.Months


# sizer
cerebro.addsizer(bt.sizers.PercentSizer, percents=50)

results = cerebro.run()
end = cerebro.broker.get_value() - 100000
print(end)