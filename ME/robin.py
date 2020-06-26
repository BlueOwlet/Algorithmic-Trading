import os
import robin_stocks as rh
import urllib
import json
from tabulate import tabulate

def LogIn():
    print('-'*30+'<| Attempting Login |>'+'-'*30)
    userName='kamiowlet@gmail.com'
    password='BlueOwl1227'
    rh.authentication.login(userName,password,expiresIn=86400,scope='internal',by_sms=False,store_session=True)
    print('-'*30+'<| Login Successful |>'+'-'*30)

def AccountInfo():
    print('-'*30+'<| Account Info |>'+'-'*30)
    data = rh.profiles.load_account_profile()
    headers = ['Acc. Type','Buying Power','Withdrawal Money']
    account = []
    account.append([data['type'],data['buying_power'],data['cash_available_for_withdrawal']])
    print(tabulate(account,headers,'fancy_grid'))
    print()
    return data['buying_power']


def StockInfo():
    currentStocks=rh.build_holdings()
    print('-'*30+'<| Current Stocks |>'+'-'*30)
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
    print('-'*30+'<| Printing Watchlist | Latest Prices |>'+'-'*30)
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
    return [stock[0] for stock in stocks]

def GetHighPrices(stocks):
    highPrices=[]
    for stock in stocks:
        try:
            stockDict = rh.stocks.get_historicals(stock,span='day',bounds='regular')
            # print(stockDict)
        except Exception as e:
            print('No values for today yet')
        else:
            stockDict = rh.stocks.get_historicals(stock,span='day',bounds='regular')

        highPricesList=[float(historicInfo['high_price']) for historicInfo in stockDict]
        highPrices.append(max(highPricesList))
    return highPrices

def GetCurrentPrice(stocks):
    currentPrices=[]
    for stock in stocks:
        currentPrices.append(rh.stocks.get_latest_price(stock)[0])
    return currentPrices

def StockDifference(stocks,highPrices,currentPrices):
    priceDifference=[]
    choice=[]
    buyingPower=float(rh.profiles.load_account_profile()['buying_power'])
    print('Buying Power: {}'.format(buyingPower))
    for price in range(len(highPrices)):
        priceDifference.append(float(highPrices[price])-float(currentPrices[price]))
        if priceDifference[-1]<0:
            if buyingPower > float(currentPrices[price]):
                buyingPower-=float(currentPrices[price])
                # rh.orders.order_buy_market(stocks[price], 1, timeInForce='gtc', extendedHours='false')
                choice.append('bought')
            else:

                choice.append('nomoney')
        else:
            choice.append('')
    return priceDifference,choice

def BuyStocks(stocks):
    while True:
        print('-'*30+'<| Checking Which Stocks to buy |>'+'-'*30)
        highPrices = GetHighPrices(stocks)
        currentPrices = GetCurrentPrice(stocks)
        sD=StockDifference(stocks,highPrices,currentPrices)
        priceDifference=sD[0]
        choice = sD[1]
        print(tabulate([highPrices,currentPrices,priceDifference,choice],stocks))


def main():
    os.system('cls')
    LogIn()
    AccountInfo()
    StockInfo()
    stocks = PrintWatchlist()
    BuyStocks(stocks)



main()
