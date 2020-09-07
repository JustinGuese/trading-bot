import requests
import json

class etoroHandler():
    def __init__(self):
        self.headers = {
            'Content-Type': 'application/json',
            'cache-control': 'no-cache',
            'mode':'Demo'
        }
        self.positions = {}
        self.watchlist = {}
        self.id2name = {}
        self.posid2name = {}
        self.updateHandler()

    def updateHandler(self):
        self.positions = self.getPositions()
        self.watchlist = self.getWatchlist()
        for entry in self.watchlist:
            self.id2name.update({entry["id"]:entry["name"]})
        self.name2id = {v: k for k, v in self.id2name.items()}
        for entry in self.positions:
            self.posid2name.update({entry["positionID"]:self.id2name[entry["instrumentID"]]})
        self.name2posid = {v: k for k, v in self.posid2name.items()}

    def putOnWatchlist(self,name):
        data = '{ "param": "%s" }'%name
        response = requests.put('http://localhost:8088/etoro-api/watchlist/byName', headers=self.headers, data=data)
        return json.loads(response.text)

    def getWatchlist(self):
        response = requests.get('http://localhost:8088/etoro-api/watchlist', headers=self.headers)
        return json.loads(response.text)

    def buy(self,stock,eurval,leverage,takeprofit,stoploss):
        data = '{ "name": "%s", "type": "BUY", "amount": %d, "leverage": %d, "takeProfitRate": %f, "stopLossRate": %f }'%(stock,eurval,leverage,takeprofit,stoploss)
        response = requests.post('http://localhost:8088/etoro-api/positions/open', headers=self.headers, data=data)
        return json.loads(response.text)

    def sell(self,stock,eurval,leverage,takeprofit,stoploss):
        data = '{ "name": "%s", "type": "SELL", "amount": %d, "leverage": %d, "takeProfitRate": %f, "stopLossRate": %f }'%(stock,eurval,leverage,takeprofit,stoploss)
        response = requests.post('http://localhost:8088/etoro-api/positions/open', headers=self.headers, data=data)
        return json.loads(response.text)

    def getPositions(self):
        response = requests.get('http://localhost:8088/etoro-api/positions', headers=self.headers)
        return json.loads(response.text)

    def getPositionDict(self):
        pos = self.getPositions()
        if len(pos) == 0:
            return {}
        else:
            port = {}
            for entry in pos:
                name = self.id2name[entry["instrumentID"]]
                amount = entry["amount"]
                isBuy = entry["isBuy"]
                if not isBuy:
                    amount = -amount
                port.update({name:amount})
            return port



    def closeByID(self,id):
        params = ( ('id', '%s'%id),)
        print(params)
        response = requests.delete('http://localhost:8088/etoro-api/positions/close', headers=self.headers, params=params)
        return response

    def close(self,name):
        return self.closeByID(self.name2posid[name])