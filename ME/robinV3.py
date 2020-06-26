import os
import robin_stocks as rh
import urllib
import json
from tabulate import tabulate
import time
from statistics import mean

# userName='ivan.ortiz51@outlook.com'
# password='Levithian1'

userName='kamiowlet@gmail.com'
password='BlueOwl1227'

def LogIn():
    os.system('cls')
    print('<| Attempting Login |>')
    rh.authentication.login(userName,password,expiresIn=86400,scope='internal',by_sms=False,store_session=True)
    print('<| Login Successful |>')

def AccountInfo():
    print('<| Account Info |>')
    data = rh.profiles.load_account_profile()
    headers = ['User','Acc. Type','Buying Power','Withdrawal Money','Unsettled Funds']
    account = []
    try:
        account.append([userName,data['type'],data['buying_power'],data['cash_available_for_withdrawal'],data['unsettled_funds']])
        print(tabulate(account,headers,'fancy_grid'))
    except Exception as e:
        print(e)
        print('Infor not Available')
        raise

    print()

def DeleteWatchlist(watchlistStocks):
    delete=input('Delete Watchlist?: ')
    if delete=='y':
        rh.account.delete_symbols_from_watchlist(watchlistStocks,name='Default')
        exit()

def PrintOwnedStocks():
    currentStocks=rh.build_holdings()
    print('<| Current Stocks |>')
    headers=['Ticker']
    for stock in currentStocks.items():
        for key in stock[1].keys():
            headers.append(key)
        break
    stocks=[]
    for stock in currentStocks.items():
        items=[]
        for item in stock[1]:
            items.append(stock[1].get(item))
        items.insert(0,stock[0])
        stocks.append(items)
    print(tabulate(stocks,headers))
    print()

def PrintWatchlist():
    print('<| Printing Watchlist | Latest Prices |>')
    watchlist = rh.account.get_watchlist_by_name(name='Default', info=None)
    headers = ['Stock','Price']
    stocks=[]
    symbolInfo=[]
    for symbol in range(len(watchlist)):
        url = (watchlist[symbol].get('instrument'))
        jsonData = json.loads(urllib.request.urlopen(url).read())
        symbolInfo.append(jsonData)
        stockName=symbolInfo[symbol].get('symbol')
        stockPrice= rh.stocks.get_latest_price(stockName)
        stocks.append([stockName,stockPrice[0]])
    print(tabulate(stocks))
    print()

def GetWatchlistStocks():
    watchlist = rh.account.get_watchlist_by_name(name='Default', info='instrument')
    stocks=[]
    symbolInfo=[]
    for url in range(len(watchlist)):
        stockName =json.loads(urllib.request.urlopen(watchlist[url]).read()).get('symbol')
        stocks.append(stockName)
    print(stocks)
    return stocks

def GetCurrentPrices(stocks,recentPrices):
    currentPrices=[]
    laggingPrices=[]
    counter=0
    for stock in stocks:
        try:
            currentPrices.append(rh.stocks.get_latest_price(stock)[0])
        except Exception as e:
            currentPrices.append(recentPrices[stock][-1])
        recentPrices[counter].append(float(currentPrices[-1]))
        counter+=1
    if len(recentPrices[0])>27:
        for i in range(len(recentPrices)):
            recentPrices[i].pop(0)
            laggingPrices.append(float(recentPrices[i][20]))
    # print(recentPrices)
    # input('check recentPrices')
    return currentPrices,recentPrices,laggingPrices

def GetHighPrices(stocks):
    highPrices=[]
    for stock in stocks:
        stockDict = rh.stocks.get_historicals(stock,span='day',bounds='extended')
        #use these two for high price
        # highPricesList=[float(historicInfo['high_price']) for historicInfo in stockDict]
        # highPrices.append(max(highPricesList))

        #use these two for market open price
        try:
            highPricesList=[float(historicInfo['open_price']) for historicInfo in stockDict]
            highPrices.append(highPricesList[0])
        except Exception as e:
            print('nopricelistdatayet')
    return highPrices

def CheckIfOwnedStock(stocks):
    stocksOwned=[]
    stockStatus=[]
    quantityOwned=[]
    try:
        ownedStocks=rh.build_holdings()
        for stock in ownedStocks.items():
            stocksOwned.append(stock[0])
            # print('ok1')
            quantityOwned.append(stock[1]['quantity'])
            # print('ok2')
        for stock in range(int(len(stocks))):
            if stocks[stock] in stocksOwned:
                # print('ok3')
                stockStatus.append(['Owned',float(quantityOwned[stocksOwned.index(stocks[stock])])])
            else:
                # print('ok4')
                stockStatus.append(['Not Owned',0])
    except Exception as e:
        for stock in ownedStocks.items():
            stocksOwned.append(stock[0])
            # print('ok1')
            quantityOwned.append(stock[1]['quantity'])
            # print('ok2')
        for stock in range(int(len(stocks))):
            if stocks[stock] in stocksOwned:
                # print('ok3')
                stockStatus.append(['Owned',float(quantityOwned[stocksOwned.index(stocks[stock])])])
            else:
                # print('ok4')
                stockStatus.append(['Error',0])
        print('something wrong with function CheckIfOwnedStock()')
        # input('check oks')
    return stockStatus

macd=[]
previousma26=[]
previousma12=[]
previousma9=[]
previousmacd=[]
multipliers=[2/(26+1),2/(12+1),2/(9+1)]
def EMA(recentPrices):
    global macd
    global previousma12
    global previousma26
    global previousma9
    global previousmacd
    signal=[]
    ticks=20
    if len(recentPrices[0])<ticks:
        pass
    elif len(recentPrices[0])==ticks:
        for i in range(len(recentPrices)):
            ma26=mean(recentPrices[i])
            ma12=mean(recentPrices[i][-12:])
            macd[i].append(ma12-ma26)
            previousma26[i].append(ma26)
            previousma12[i].append(ma12)
            print('initial means: {},{},{}'.format(ma26,ma12,macd[i][-1]))
    elif len(recentPrices[0])>ticks:
        for i in range(len(recentPrices)):
            ma26=(recentPrices[i][-1]-previousma26[i][-1])*multipliers[0]+previousma26[i][-1]
            ma12=(recentPrices[i][-1]-previousma12[i][-1])*multipliers[1]+previousma12[i][-1]
            previousma26[i].append(ma26)
            previousma12[i].append(ma12)
            macd[i].append(ma12-ma26)
            if len(macd[i])==9:
                ma9=mean(macd[i])
                previousma9[i].append(ma9)
            elif len(macd[i])>9:
                ma9=(macd[i][-1]-previousma9[i][-1])*multipliers[2]+previousma9[i][-1]
                signal.append(macd[i][-1]-ma9)
                macd[i]=macd[i][-9:]
    return signal

def BuyOrSell(watchlistStocks,highPrices,currentPrices,stockStatus,recentPrices,laggingPrices):
    try:
        buyingPower=float(rh.profiles.load_account_profile()['buying_power'])
    except Exception as e:
        print('BP is None')
        buyingPower=float(50)
    choice=[]
    signal=EMA(recentPrices)
    # finalMA=EMAS[0]
    # macd=EMAS[1]
    print('Buying Power: {}'.format(buyingPower))
    if len(signal)==len(currentPrices):
        for stock in range(len(watchlistStocks)):
            try:

                if stockStatus[stock][0] is 'Owned' and stockStatus[stock][1]==0:
                    counter=0
                    while counter<1:
                        try:
                            orders=rh.orders.find_orders(symbol=watchlistStocks[stock])
                            rh.cancel_order(orders[0]['id'])

                        except Exception as e:
                            print(e)
                        try:
                            rh.orders.order_buy_market(watchlistStocks[stock], 1, timeInForce='gtc', extendedHours='false')
                            choice.append('Rebought')
                            print('Trying to re-buy {}'.format(watchlistStocks[stock]))
                            time.sleep(4)
                            stockStatus=CheckIfOwnedStock(watchlistStocks)
                            counter+=1
                        except Exception as e:
                            print('Rebought Failed?: '.format(e))

                elif stockStatus[stock][0] is 'Owned' and stockStatus[stock][1]>0 and signal[stock]<0.0002:
                    counter=0
                    while counter<1:
                        try:
                            rh.orders.order_sell_market(watchlistStocks[stock], 1, timeInForce='gtc', extendedHours='false')
                            choice.append('Sold')
                            print('Trying to sell {}'.format(watchlistStocks[stock]))
                            time.sleep(4)
                            stockStatus=CheckIfOwnedStock(watchlistStocks)
                            counter+=1
                        except Exception as e:
                            choice.append('SellingFailed')
                elif stockStatus[stock][0] is 'Owned' and stockStatus[stock][1]>0 and recentPrices[stock][-1]<laggingPrices[stock]*0.998:
                    counter=0
                    while counter<1:
                        try:
                            rh.orders.order_sell_market(watchlistStocks[stock], 1, timeInForce='gtc', extendedHours='false')
                            choice.append('Sold')
                            print('Trying to sell {}'.format(watchlistStocks[stock]))
                            time.sleep(4)
                            stockStatus=CheckIfOwnedStock(watchlistStocks)
                            counter+=1
                        except Exception as e:
                            choice.append('SellingFailed')
                elif signal[stock]>0.001 and stockStatus[stock][0] is 'Owned' and stockStatus[stock][1]>0 and recentPrices[stock][-1]>laggingPrices[stock]*0.998:
                    choice.append('Waiting to Sell')
                elif signal[stock]>0.001 and buyingPower>float(currentPrices[stock]) and recentPrices[stock][-1]>laggingPrices[stock]*0.998:
                    try:
                        rh.orders.order_buy_market(watchlistStocks[stock], 1, timeInForce='gtc', extendedHours='false')
                        choice.append('Bought')
                        print('Trying to buy {}'.format(watchlistStocks[stock]))
                        time.sleep(4)
                        stockStatus=CheckIfOwnedStock(watchlistStocks)
                    except Exception as e:
                        print(e)
                        choice.append('Bought Failed')
                    if stockStatus[stock][1]==0:
                        counter=0
                        while counter<1:
                            try:
                                orders=rh.orders.find_orders(symbol=watchlistStocks[stock])
                                rh.cancel_order(orders[0]['id'])

                            except Exception as e:
                                print(e)
                            try:
                                rh.orders.order_buy_market(watchlistStocks[stock], 1, timeInForce='gtc', extendedHours='false')
                                choice.append('Bought')
                                print('Trying to buy {}'.format(watchlistStocks[stock]))
                                time.sleep(4)
                                stockStatus=CheckIfOwnedStock(watchlistStocks)
                                counter+=1
                            except Exception as e:
                                print(e)
                                choice.append('Bought Failed')

                elif signal[stock]>0.001 and buyingPower<float(currentPrices[stock]):
                    choice.append('NoMoney')
                else:
                    choice.append('Too Low')
            except Exception as e:
                print(e)
    return choice,signal


def AnalyzeStocks(watchlistStocks,highPrices,currentPrices,stockStatus,recentPrices,laggingPrices):
    os.system('cls')
    print('\n<| Analyzing Stocks |>\n')

    bors=BuyOrSell(watchlistStocks,highPrices,currentPrices,stockStatus,recentPrices,laggingPrices)
    choice=bors[0]
    signal=bors[1]
    print(tabulate([stockStatus,laggingPrices,currentPrices,signal,choice],watchlistStocks))
    return


def main():
    global macd
    global previousma12
    global previousma26
    global previousma9
    global previousmacd
    LogIn()
    AccountInfo()
    PrintOwnedStocks()
    try:
        PrintWatchlist()
    except Exception as e:
        print('No Stocks in Watclist')
        exit()
    watchlistStocks=GetWatchlistStocks()

    # DeleteWatchlist(watchlistStocks)
    recentPrices=[]
    counter=0
    for i in range(len(watchlistStocks)):
        recentPrices.append([])
        macd.append([])
        previousma26.append([])
        previousma12.append([])
        previousma9.append([])
        previousmacd.append([])
    while True:
        counter+=1
        print(counter)
        if counter<26:
            None
        else:
            time.sleep(0)

        stockStatus=CheckIfOwnedStock(watchlistStocks)

        highPrices=GetHighPrices(watchlistStocks)
        GCR=GetCurrentPrices(watchlistStocks,recentPrices)
        currentPrices=GCR[0]
        recentPrices=GCR[1]
        laggingPrices=GCR[2]
        AS=AnalyzeStocks(watchlistStocks,highPrices,currentPrices,stockStatus,recentPrices,laggingPrices)

main()
