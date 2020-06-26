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
            laggingPrices.append(float(recentPrices[i][15]))
    # print(recentPrices)
    # input('check recentPrices')
    return currentPrices,recentPrices,laggingPrices
