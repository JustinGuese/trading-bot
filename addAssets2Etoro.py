from etoro import etoroHandler

# if asset now found you will have to add it first
eh = etoroHandler()
ADD = ["GOOG","SPY","QQQ","btc","eurusd"]
for asset in ADD:
    resp = eh.putOnWatchlist(asset)
    print(resp)