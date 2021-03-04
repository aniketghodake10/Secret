import math
# import pandas_datareader as web
# import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime as dt
# from datetime import timedelta as td
from bs4 import BeautifulSoup
from snapi_py_client.snapi_bridge import StocknoteAPIPythonBridge
import requests
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from threading import *

###     FUNCTIONS  ###

software_names = [SoftwareName.CHROME.value, SoftwareName.FIREFOX.value, SoftwareName.SAFARI.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

hundred_rejection=1.001
hundred_target=0.997/0.05
hundred_SL=1.0035
zero_rejection=0.999
zero_target=1.003/0.05
zero_SL=0.9965

a_thread=1
check = 0
exceed = 0
done = 0
placeo = 0
aa = 1
time_m = 200



def stochrsi(tickerr, period: int = 14, smoothK: int = 3, smoothD: int = 3):
    df_5 = yf.download(tickers=tickerr, period='2h', interval='5m')
    df_5=df_5[:-1]
    df = df_5['Close']
    delta = df_5['Close'].diff(1)
    delta.dropna(inplace=True)
    gain, loss = delta.copy(), delta.copy()
    gain[gain < 0] = 0
    loss[loss > 0] = 0

    _gain = gain.ewm(com=(period - 1), min_periods=period).mean()
    _loss = loss.abs().ewm(com=(period - 1), min_periods=period).mean()

    RS = _gain / _loss
    rsii = 100 - (100 / (1 + RS))

    stochrsii = (rsii - rsii.rolling(period).min()) / (rsii.rolling(period).max() - rsii.rolling(period).min())
    # stochrsii_K = stochrsii.ewm(span=smoothK).mean()
    # stochrsii_D = stochrsii_K.ewm(span=smoothD).mean()
    stochrsii_K = stochrsii.rolling(smoothK).mean()
    stochrsii_D = stochrsii_K.rolling(smoothD).mean()

    return stochrsii_K[-1], df[-1], df[-6:]


def live_price(Stock):
    stockcode = Stock.lower()
    global user_agent_rotator
    stock_url = 'https://in.finance.yahoo.com/quote/' + stockcode
    user_agent = user_agent_rotator.get_random_user_agent()
    headers = {'User-Agent': user_agent}
    response = requests.get(stock_url, headers)
    soup = BeautifulSoup(response.text, 'lxml')
    price = soup.find_all('div', {'class': 'My(6px) Pos(r) smartphone_Mt(6px)'})[0].find('span').text
    price = price.split(',')
    price = ''.join(price)
    price = float(price)
    return price


def telegram_trade_messeges(bot_messege):
    bot_token = '1645791181:AAHbzBLFj_1PwVCxFXByChYaIkafHNGxVSk'
    bot_charID = '473753128'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_charID + '&parse_mode=MarkdownV2&text=' + bot_messege
    response = requests.get(send_text)
    return response.json()


def string_remove_char(a):
    for i in ['.', '\'', '\"', '{', '}', '[', ']', ':', ',', '*', '-', '_', '=', '(', ')', '@', '+']:
        a = a.replace(i, ' ')
    return a


def PO_body(a,b,c):
    global samco, qty , price_1, Stock_samco
    bodyy= {"symbolName": Stock_samco, "exchange": samco.EXCHANGE_NSE,"transactionType": samco.TRANSACTION_TYPE_BUY,
            "orderType": samco.ORDER_TYPE_MARKET,"price": "","quantity": qty,"disclosedQuantity": "",
            "orderValidity": samco.VALIDITY_DAY,"productType": samco.PRODUCT_MIS, "afterMarketOrderFlag": "NO"}
    if a=='sell':
        bodyy["transactionType"]=samco.TRANSACTION_TYPE_SELL
    if b=='limit':
        bodyy["orderType"]=samco.ORDER_TYPE_LIMIT
        bodyy["price"]=c
    return bodyy


def time_exceed(a,b,c,d):
    if d>999999:
        d=d-1000000
        c=c+1
    if c>59:
        c=c-60
        b=b+1
    if b>59:
        b=b-60
        a=a+1
    if a>23:
        a=a-24
    now=dt.now()
    e,f,g,h=now.hour, now.minute, now.second, now.microsecond
    if e>a:
        return True
    if e==a:
        if f>b:
            return True
    if e==a and f==b:
        if g>c:
            return True
    if e==a and f==b and g==c:
        if h>d:
            return True


###     FUNCTIONS  ###


samco = StocknoteAPIPythonBridge()

userId = input("Enter Samco userId : ")
password = input("Enter Samco Password : ")
yob = input("Enter Samco Year Of Birth : ")
login = samco.login(body={"userId": userId, 'password': password, 'yob': yob})
print('Login Details\n', login)
login = eval(login)

samco.set_session_token(sessionToken=login['sessionToken'])

csv_2 = pd.read_csv('ind_nifty50list.csv')
Stock_samco1 = csv_2.loc[:, 'Symbol':'Symbol']
Stock_samco1 = Stock_samco1.Symbol
Stock_samco1 = Stock_samco1.tolist()

Stock1 = []
for i in Stock_samco1:
    j = i + '.NS'
    Stock1.append(j)
dict_Stock2 = dict(zip(Stock1, Stock_samco1))

qty = int(input('HOW MUCH QUANTITY TO TRADE TODAYYY = '))
qty = str(qty)

startt_time = [int(x) for x in input('Enter Start time in 24 hrs format ---hours <space> minutes = ').split()]
endd_time = [int(x) for x in input('Enter End time in 24 hrs format ---hours <space> minutes = ').split()]


class Scrip(Thread):
    def __init__(self, Stock):
        global a_thread, check, exceed, done, placeo, aa, time_m, software_names, operating_systems, \
            user_agent_rotator, samco, Stock_samco1, Stock1, dict_Stock2, qty, startt_time, endd_time, \
            hundred_rejection, hundred_target, hundred_SL, zero_rejection, zero_target, zero_SL
        Thread.__init__(self)
        self.Stock = Stock

    def run(self):
        global a_thread, check, exceed, done, placeo, aa, time_m, software_names, operating_systems, \
            user_agent_rotator, samco, Stock_samco1, Stock1, dict_Stock2, qty, startt_time, endd_time, \
            hundred_rejection, hundred_target, hundred_SL, zero_rejection, zero_target, zero_SL
        while True:
            if time_exceed(endd_time[0],endd_time[1],0,0):
                break
            if time_exceed(startt_time[0],startt_time[1],0,0):
                while True:
                    if time_exceed(endd_time[0],endd_time[1],0,0):
                        break
                    while True:
                        if a_thread==1:
                            break
                    while True:
                        cond = dt.now()
                        if cond.minute % 5 == 0 and cond.second == 3:
                            break
                    telegram_trade_messeges('checking stochRSI NEW Iteration')
                    print('checking stochRSI NEW Iteration')
                    stochRSI, df_ltp, df_last_5_values = stochrsi(self.Stock)
                    stochRSI = float('{:.3f}'.format(100 * stochRSI))
                    Stock_samco = dict_Stock2[self.Stock]

                    if stochRSI == 100:
                        time_1 = dt.now()
                        while True:
                            price = live_price(self.Stock)
                            if aa == 1:
                                price_1 = price
                                print(df_last_5_values)
                                print('\nWEoooooo WE got the Stock ---', self.Stock, '----', 'stochRSI===', stochRSI)
                                print('\nprice_1===', price_1)
                                telegram_trade_messeges(string_remove_char('WEoooooo WE got the Stock ---' +self.Stock+ '----'+ 'stochRSI is   '+ stochRSI+ 'price 1 is    '+price_1))
                                aa = 2
                            if a_thread != 1:
                                break
                            if price > hundred_rejection * price_1:
                                time_2 = dt.now()
                                while True:
                                    if a_thread != 1:
                                        break
                                    price = live_price(self.Stock)
                                    if price <= price_1:
                                        a_thread = 0
                                        placeo = 1
                                        break

                                    if time_exceed(time_2.hour,time_2.minute,time_2.second+time_m,time_2.microsecond):
                                        print('2 min done so no trade')
                                        telegram_trade_messeges('trade cancelled as two minutes are up')
                                        break
                                break

                            if time_exceed(time_1.hour,time_1.minute,time_1.second+time_m,time_1.microsecond):
                                print('2 min done so no trade')
                                telegram_trade_messeges('trade cancelled as two minutes are up')
                                break

                        if placeo == 1:
                            placeo = 0
                            PO = samco.place_order(body=PO_body('sell','m','na'))
                            dict_PO = eval(PO)
                            while True:
                                Order_status = samco.get_order_status(order_number=dict_PO["orderNumber"])
                                dict_Order_status = eval(Order_status)
                                dict_dict_Order_status=eval(dict_Order_status["orderDetails"])
                                if dict_Order_status["orderStatus"] == "EXECUTED":
                                    print('SELL EXECUTED   avgExecutionPrice is ' + dict_dict_Order_status["avgExecutionPrice"])
                                    telegram_trade_messeges(string_remove_char('SELL EXECUTED   avgExecutionPrice is ' + dict_dict_Order_status["avgExecutionPrice"]))
                                    PO_1 = samco.place_order(body=PO_body('b','limit',str(0.05 * math.ceil(hundred_target * price_1))))
                                    dict_PO_1 = eval(PO_1)
                                    while True:
                                        Order_status_1 = samco.get_order_status(order_number=dict_PO_1["orderNumber"])
                                        dict_Order_status_1 = eval(Order_status_1)
                                        dict_dict_Order_status_1=eval(dict_Order_status_1["orderDetails"])
                                        if dict_Order_status_1["orderStatus"] == "EXECUTED":
                                            print('BUY EXECUTED   avgExecutionPrice is ' + dict_dict_Order_status_1["avgExecutionPrice"])
                                            telegram_trade_messeges(string_remove_char('BUY EXECUTED   avgExecutionPrice is ' + dict_dict_Order_status_1["avgExecutionPrice"]))
                                            done = 1
                                            break
                                        price = live_price(self.Stock)
                                        if price > hundred_SL * price_1:
                                            done = 2
                                            break
                                        if time_exceed(endd_time[0],endd_time[1],0,0):
                                            done = 3
                                            break
                                    if done == 1:
                                        done = 0
                                        break
                                    if done == 2:
                                        done = 0
                                        PO_2 = samco.modify_order(order_number=dict_PO_1["orderNumber"], body={"orderType": samco.ORDER_TYPE_MARKET,"price": ""})
                                        while True:
                                            Order_status_2 = samco.get_order_status(order_number=dict_PO_1["orderNumber"])
                                            dict_Order_status_2 = eval(Order_status_2)
                                            dict_dict_Order_status_2 = eval(dict_Order_status_2["orderDetails"])
                                            if dict_Order_status_2["orderStatus"] == "EXECUTED":
                                                print('BUY EXECUTED   avgExecutionPrice is ' + dict_dict_Order_status_2["avgExecutionPrice"])
                                                telegram_trade_messeges(string_remove_char('BUY EXECUTED   avgExecutionPrice is ' + dict_dict_Order_status_2["avgExecutionPrice"]))
                                                break
                                        break
                                    if done == 3:
                                        done = 0
                                        PO_3 = samco.modify_order(order_number=dict_PO_1["orderNumber"],body={"orderType": samco.ORDER_TYPE_MARKET,"price": ""})
                                        while True:
                                            Order_status_3 = samco.get_order_status(order_number=dict_PO_1["orderNumber"])
                                            dict_Order_status_3 = eval(Order_status_3)
                                            dict_dict_Order_status_3 = eval(dict_Order_status_3["orderDetails"])
                                            if dict_Order_status_3["orderStatus"] == "EXECUTED":
                                                print('BUY EXECUTED   avgExecutionPrice is ' + dict_dict_Order_status_3["avgExecutionPrice"])
                                                telegram_trade_messeges(string_remove_char('BUY EXECUTED   avgExecutionPrice is ' + dict_dict_Order_status_3["avgExecutionPrice"]))
                                                break
                                    break
                        aa = 1
                        a_thread = 1

                    if stochRSI == 0:
                        time_1 = dt.now()
                        while True:
                            price = live_price(self.Stock)
                            if aa == 1:
                                price_1 = price
                                print(df_last_5_values)
                                print('\nWEoooooo WE got the Stock ---', self.Stock, '----', 'stochRSI===', stochRSI)
                                print('\nprice_1===', price_1)
                                telegram_trade_messeges(string_remove_char('WEoooooo WE got the Stock ---' + self.Stock + '----' + 'stochRSI is   ' + stochRSI + 'price 1 is    ' + price_1))
                                aa = 2
                            if a_thread != 1:
                                break
                            if price < zero_rejection * price_1:
                                time_2 = dt.now()
                                while True:
                                    if a_thread != 1:
                                        break
                                    price = live_price(self.Stock)
                                    if price >= price_1:
                                        a_thread = 0
                                        placeo = 1
                                        break

                                    if time_exceed(time_2.hour,time_2.minute,time_2.second+time_m,time_2.microsecond):
                                        print('2 min done so no trade')
                                        telegram_trade_messeges('trade cancelled as two minutes are up')
                                        break
                                break
                            if time_exceed(time_1.hour,time_1.minute,time_1.second+time_m,time_1.microsecond):
                                print('2 min done so no trade')
                                telegram_trade_messeges('trade cancelled as two minutes are up')
                                break

                        if placeo == 1:
                            placeo = 0
                            PO = samco.place_order(body=PO_body('buy', 'm', 'na'))
                            dict_PO = eval(PO)
                            while True:
                                Order_status = samco.get_order_status(order_number=dict_PO["orderNumber"])
                                dict_Order_status = eval(Order_status)
                                dict_dict_Order_status = eval(dict_Order_status["orderDetails"])
                                if dict_Order_status["orderStatus"] == "EXECUTED":
                                    print('BUY EXECUTED   avgExecutionPrice is ' + dict_dict_Order_status["avgExecutionPrice"])
                                    telegram_trade_messeges(string_remove_char('BUY EXECUTED   avgExecutionPrice is ' + dict_dict_Order_status["avgExecutionPrice"]))
                                    PO_1 = samco.place_order(body=PO_body('s', 'limit', str(0.05 * math.ceil(zero_target * price_1))))
                                    dict_PO_1 = eval(PO_1)
                                    while True:
                                        Order_status_1 = samco.get_order_status(order_number=dict_PO_1["orderNumber"])
                                        dict_Order_status_1 = eval(Order_status_1)
                                        dict_dict_Order_status_1 = eval(dict_Order_status_1["orderDetails"])
                                        if dict_Order_status_1["orderStatus"] == "EXECUTED":
                                            print('SELL EXECUTED   avgExecutionPrice is ' + dict_dict_Order_status_1["avgExecutionPrice"])
                                            telegram_trade_messeges(string_remove_char('SELL EXECUTED   avgExecutionPrice is ' + dict_dict_Order_status_1["avgExecutionPrice"]))
                                            done = 1
                                            break
                                        price = live_price(self.Stock)
                                        if price < zero_SL * price_1:
                                            done = 2
                                            break
                                        if time_exceed(endd_time[0],endd_time[1],0,0):
                                            done = 3
                                            break
                                    if done == 1:
                                        done = 0
                                        break
                                    if done == 2:
                                        done = 0
                                        PO_2 = samco.modify_order(order_number=dict_PO_1["orderNumber"],body={"orderType": samco.ORDER_TYPE_MARKET,"price": ""})
                                        while True:
                                            Order_status_2 = samco.get_order_status(order_number=dict_PO_1["orderNumber"])
                                            dict_Order_status_2 = eval(Order_status_2)
                                            dict_dict_Order_status_2 = eval(dict_Order_status_2["orderDetails"])
                                            if dict_Order_status_2["orderStatus"] == "EXECUTED":
                                                print('SELL EXECUTED   avgExecutionPrice is ' + dict_dict_Order_status_2["avgExecutionPrice"])
                                                telegram_trade_messeges(string_remove_char('SELL EXECUTED   avgExecutionPrice is ' + dict_dict_Order_status_2["avgExecutionPrice"]))
                                                break
                                        break
                                    if done == 3:
                                        done = 0
                                        PO_3 = samco.modify_order(order_number=dict_PO_1["orderNumber"],body={"orderType": samco.ORDER_TYPE_MARKET,"price": ""})
                                        while True:
                                            Order_status_3 = samco.get_order_status(order_number=dict_PO_1["orderNumber"])
                                            dict_Order_status_3 = eval(Order_status_3)
                                            dict_dict_Order_status_3 = eval(dict_Order_status_3["orderDetails"])
                                            if dict_Order_status_3["orderStatus"] == "EXECUTED":
                                                print('SELL EXECUTED   avgExecutionPrice is ' + dict_dict_Order_status_3["avgExecutionPrice"])
                                                telegram_trade_messeges(string_remove_char('SELL EXECUTED   avgExecutionPrice is ' + dict_dict_Order_status_3["avgExecutionPrice"]))
                                                break
                                    break
                        aa = 1
                        a_thread = 1


obj = []
for i in Stock1:
    i = Scrip(Stock=i)
    obj.append(i)

while True:
    if time_exceed(startt_time[0],startt_time[1],0,0):
        print('Trade m-c is Started---')
        telegram_trade_messeges('IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII')
        telegram_trade_messeges('THE START')
        for i in obj:
            i.start()
        break

while True:
    if time_exceed(endd_time[0],endd_time[1],0,0):
        samco_holdings = samco.get_holding()
        if samco_holdings.find('tradingSymbol') != -1:
            telegram_trade_messeges('holdings are there CHECK app')
        telegram_trade_messeges('THE END')
        telegram_trade_messeges('IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII')
        break


print('program ended')
samco.logout()
