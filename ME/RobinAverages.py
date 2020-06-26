import os
import robin_stocks as rh
import urllib
import json
from tabulate import tabulate
import time
from statistics import mean, pstdev
import openpyxl as xl

file = xl.load_workbook('Investing-Stocks.xlsx')

print('Workbook loaded')
sheets = file.worksheets
sheet = sheets[0]
rows = sheet.rows
rows1=rows
rows = list(rows)
row=[row.value for row in rows[0]]
print(row)

userName='kamiowlet@gmail.com'
password='BlueOwl1227'
stocks=[]
ownedStocks=None
quantityOwned=None

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
    # global stocks
    watchlist = rh.account.get_watchlist_by_name(name='Default', info='instrument')
    symbolInfo=[]
    for url in range(len(watchlist)):
        stockName = json.loads(urllib.request.urlopen(watchlist[url]).read()).get('symbol')
        stock=Stock(stockName)
        # stock.name=stockName
        stocks.append(stock)
        print(stock.name)
    print('Stocks initiated nicely')
    return stocks

class Stock:
    def __init__(self, stockName):
        self.name = stockName
        self.data=[]

    def owned(self):

        try:
            if self.name in ownedStocks:
                position = ownedStocks.index(self.name)
                return True,quantityOwned[position]
            else:
                return False,0
        except Exception as e:
            print('owned() Error')
            return None,None


    def price(self):
        try:
            price = rh.stocks.get_latest_price(self.name)[0]
            return float(price)
        except Exception as e:
            print('Current price not available')
            return 0


    def stats(self):
        try:
            span='day'#could be 'day', 'week', 'year', or '5year'. Default is 'week'.
            historical_info = rh.stocks.get_historicals(self.name,span=span,bounds='regular')
            # print(historical_info)

            closing_prices = [float(closing_price['close_price']) for closing_price in historical_info]
            max_price = max(closing_prices)
            min_price = min(closing_prices)
            average = mean(closing_prices)
            stdev = pstdev(closing_prices,mu=average)
            self.average = average
            self.stdev = stdev
            return float(average),float(stdev)
        except Exception as e:
            print('average() Error')
            return 0



    def buy(self):
        try:
            rh.orders.order_buy_market(self.name, 1, timeInForce='gtc', extendedHours='false')
        except Exception as e:
            print('Error Buying')
            print(e)


    def sell(self):
        try:
            rh.orders.order_sell_market(self.name, 1, timeInForce='gtc', extendedHours='false')
        except Exception as e:
            print('Error Selling')


    def cancel_order(self):
        try:
            orders=rh.orders.find_orders(symbol=self.name)
            rh.cancel_order(orders[0]['id'])

        except Exception as e:
            print('Error Cancelling Orders for: {}'.format(self.name))
    def set_buy_point(self, buy_point=0):
        self.buy_point = buy_point
        return self.buy_point

    def profit_loss(self):
        profit_loss = self.buy_point-self.price()
        return profit_loss

    def register_data(self,data_point=0):
        self.data.append(data_point)
        return self.data
    # def check_order(self):
    #     try:
    #         orders=rh.orders.find_orders(symbol=self.name)
    #
    #         if len(orders)==0:
    #             continue
    #         else:
    #
    #
    #     except Exception as e:
    #         raise

def BuyOrSell():


    global ownedStocks
    global quantityOwned
    holdings=rh.build_holdings()
    holdings=list(holdings.items())
    ownedStocks=[stock[0] for stock in holdings]
    quantityOwned=[float(stock[1]['quantity']) for stock in holdings]

    for stock in stocks:


        name = stock.name
        owned = stock.owned()
        if owned[0]==False:
            stock.set_buy_point()
            stock.buy_point=0
            # profit_loss=0
            # stock.buy_point=0
        else:
            pass


        stock.register_data()

        price = stock.price()
        stats = stock.stats()
        stock.register_data(price)
        average = stock.average
        stdev = stock.stdev
        lower_limit = average-stdev*1
        stop_loss=average-stdev*1.5
        upper_limit= average+stdev*1

        print('')
        print('Stock: '+name)
        print('Average: {}'.format(average))
        print('STDEV: {}'.format(stdev))
        print('Owned: {}'.format(owned[0]))
        print('Quantity: {}'.format(owned[1]))

        # print('Profit/Loss: {}'.format(profit_loss))

        print('Sell point: {}'.format(upper_limit))
        print('Price point: {}'.format(price))
        print('Buy point: {}'.format(lower_limit))
        print('Stop Loss: {}'.format(stop_loss))

        if price < lower_limit and owned[0]==False and price > stop_loss:
            try:
                stock.cancel_order()
                time.sleep(5)
            except Exception as e:
                print('No Orders to Cancel')
                # print(e)
            print('Buy')
            try:
                stock.buy()
                stock.set_buy_point(stock.price())
                time.sleep(5)
            except Exception as e:
                print('Could not buy')
        elif price < stop_loss and owned[0]==True:
            try:
                stock.cancel_orders()
                time.sleep(5)
            except Exception as e:
                print('No Orders to Cancel')
            print('Sell')

            try:
                stock.sell()
                time.sleep(5)
            except Exception as e:
                print('Could not Sell')

        elif price > upper_limit and owned[0]==True:
            try:
                stock.cancel_orders()
                time.sleep(5)
            except Exception as e:
                print('No Orders to Cancel')
            print('Sell')

            try:
                stock.sell()
                time.sleep(5)
            except Exception as e:
                print('Could not Sell')
        else:
            print('No Action')
            pass





firstrun = True
def testing():
    global firstrun

    averageList=[]
    i = 0
    for row in rows:

        print(row[1].value)

        if firstrun is True:
            print('firstRun')
            firstrun=False
        else:

            averageList.append(float(row[1].value))





            price = row[1].value
            average=289.33
            stdev = pstdev(averageList)
            upper_limit = average+stdev*1
            lower_limit = average-stdev*1

            row[2].value = lower_limit
            row[3].value = average
            row[4].value = upper_limit

            print('Price {}'.format(price))
            print('Lower {}'.format(lower_limit))
            print('Upper {}'.format(upper_limit))
            print('Average {}'.format(average))


            if price < lower_limit:
                row[5].value = 'Buy'
                print('Buy')
            elif price > upper_limit:
                row[5].value = 'sell'
                print('Sell')
            else:
                row[5].value = 'Nothing'
                print('Nothing')


        i+=1


    file.save('Investing-Stocks.xlsx')


def main():



    header = """

    Owl Trading bot V.4 | BuyOrSell() initialized

    """
    i=0

    testings = 'no'

    if testings is 'yes':
        print('-'*10+'Testing'+10*'-')
        testing()
    else:
        LogIn()
        GetWatchlistStocks()

        for stock in stocks:
            stock.stats()

        while True:
            os.system('cls')
            print(header)

            BuyOrSell()
            print(i)
            i+=1
            time.sleep(4)
            # time.sleep(5)

            # input()



main()
