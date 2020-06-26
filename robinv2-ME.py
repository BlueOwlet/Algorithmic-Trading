import os
import robin_stocks as rh
import urllib
import json
from tabulate import tabulate
import time
from statistics import mean

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
    account.append([userName,data['type'],data['buying_power'],data['cash_available_for_withdrawal'],data['unsettled_funds']])
    print(tabulate(account,headers,'fancy_grid'))
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
    counter=0
    for stock in stocks:
        try:
            currentPrices.append(rh.stocks.get_latest_price(stock)[0])
        except Exception as e:
            currentPrices.append(recentPrices[-1])

        recentPrices[counter].append(float(currentPrices[-1]))
        counter+=1
    if len(recentPrices[0])>27:
        for i in range(len(recentPrices)):
            recentPrices[i].pop(0)
    return currentPrices,recentPrices

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
    try:
        ownedStocks=rh.build_holdings()
        for stock in ownedStocks.items():
            stocksOwned.append(stock[0])
        for stock in range(int(len(stocks))):
            if stocks[stock] in stocksOwned:
                stockStatus.append('Owned')
            else:
                stockStatus.append('Not Owned')
        # print(tabulate([stockStatus],stocks))
    except Exception as e:
        print('something wrong with function CheckIfOwnedStock()')

    return stockStatus

macd=[]
previousma26=[]
previousma12=[]
previousma9=[]
previousmacd=[]
multipliers=[2/(26+1),2/(12+1),2/(9+1)]
firstRun=True
def EMA(recentPrices):
    signal=[]
    if len(recentPrices[0])<5:
        pass
    elif len(recentPrices[0])==5:
        for i in range(len(recentPrices)):
            ma26=mean(recentPrices[i])
            ma12=mean(recentPrices[i][-12:])
            macd[i].append(ma26-ma12)
            previousma26[i].append(ma26)
            previousma12[i].append(ma12)
            print('initial means: {},{},{}'.format(ma26,ma12,macd[-1]))
    elif len(recentPrices[0])>5:
        for i in range(len(recentPrices)):
            ma26=(recentPrices[i][-1]-previousma26[i][-1])*multipliers[0]+previousma26[i][-1]
            ma12=(recentPrices[i][-1]-previousma26[i][-1])*multipliers[1]+previousma26[i][-1]
            macd[i].append(ma26-ma12)
            if len(macd[i])==9:
                ma9=mean(macd[i])
                previousma9[i].append(ma9)
            elif len(macd[i])==10:
                ma9=(macd[i][-1]-previousma9[i][-1])*multipliers[2]+previousma9[i][-1]
                macd[i]=macd[i][-9:]
                signal.append(ma9-macd[i][-1])
            # print('previous26: {}'.format(previousma26[i]))
            # print('current26: {}'.format(ma26))
            # macd.append([ma26-ma12])
    # print('Previous26: {}'.format(previousma26))
    # print('Previous12: {}'.format(previousma12))
    # print('Previous9: {}'.format(previousma9))
    # # print('Previousmacd: {}'.format(previousmacd))
    # print('signal: {}'.format(signal))
    # print('MACD: {}'.format(macd))
    # print(signal)
    return signal

def BuyOrSell(watchlistStocks,highPrices,currentPrices,stockStatus,recentPrices):
    try:
        buyingPower=float(rh.profiles.load_account_profile()['buying_power'])
    except Exception as e:
        print('BP is None')
        buyingPower=float(50)
    # buyingPower=float(50)


    choice=[]
    signal=EMA(recentPrices)
    # finalMA=EMAS[0]
    # macd=EMAS[1]
    print('Buying Power: {}'.format(buyingPower))
    print(stockStatus)
    if len(signal)==len(currentPrices):
        for stock in range(len(watchlistStocks)):
            if stockStatus[stock] is 'Owned':
                if signal[stock]<0:
                    try:
                        rh.orders.order_sell_market(watchlistStocks[stock], 1, timeInForce='gtc', extendedHours='false')
                        choice.append('Sold')
                    except Exception as e:
                        choice.append('SellingFailed')
                else:
                    choice.append('Waiting to Sell')
            elif signal[stock]>0 and buyingPower>float(currentPrices[stock]):
                rh.orders.order_buy_market(watchlistStocks[stock], 1, timeInForce='gtc', extendedHours='false')
                choice.append('Bought')
                buyingPower-=float(currentPrices[stock])
            elif signal[stock]>0 and buyingPower<float(currentPrices[stock]):
                choice.append('NoMoney')
            else:
                choice.append('wait')

    return choice,signal


def AnalyzeStocks(watchlistStocks,highPrices,currentPrices,stockStatus,recentPrices):
    os.system('cls')
    print('\n<| Analyzing Stocks |>\n')

    bors=BuyOrSell(watchlistStocks,highPrices,currentPrices,stockStatus,recentPrices)
    choice=bors[0]
    signal=bors[1]
    # macd=bors[2]


    print(tabulate([stockStatus,highPrices,currentPrices,signal,choice],watchlistStocks))
    return


def main():

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
        highPrices=GetHighPrices(watchlistStocks)

        GCR=GetCurrentPrices(watchlistStocks,recentPrices)

        currentPrices=GCR[0]
        recentPrices=GCR[1]


        stockStatus=CheckIfOwnedStock(watchlistStocks)

        AS=AnalyzeStocks(watchlistStocks,highPrices,currentPrices,stockStatus,recentPrices)

        # time.sleep(10)
main()
