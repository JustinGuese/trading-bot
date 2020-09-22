from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

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
app.reqHistoricalData(1, eurusd_contract, '', '6 D', '1 min', 'BID', 0, 2, False, [])

time.sleep(5) #sleep to allow enough time for data to be returned

#Working with Pandas DataFrames
import pandas

df = pandas.DataFrame(app.data, columns=['DateTime', 'Open',"High","Low","Close"])
df['DateTime'] = pandas.to_datetime(df['DateTime'],unit='s') 
if len(df) > 0:
    df.to_csv('data/%s=X_1m_all.csv'%name,index=False)  
    split = 0.9
    df[:int(len(df)*split)].to_csv('data/%s=X_1m_train.csv'%name,index=False)  
    df[int(len(df)*split):].to_csv('data/%s=X_1m_test.csv'%name,index=False)  
    print(df.head())
    print("It will crash now, fucking ibapi... Just ignore")
else:
    print("OHOH!!!! no dataa ")

app.done = True
app.disconnect()