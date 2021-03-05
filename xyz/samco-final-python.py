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
# from threading import *

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

check = 0
exceed = 0
done = 0
placeo_100 = 0
placeo_0 = 0
time_m_min = 4
time_m_sec = 20


def stochrsi(tickerr, period: int = 14, smoothK: int = 3, smoothD: int = 3):
    df_5 = yf.download(tickers=tickerr, period='2d', interval='5m')
    df_6=df_5[:-1]
    df = df_6['Close']
    delta = df_6['Close'].diff(1)
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
    print('.              .')

    return stochrsii_K[-1], df[-6:], df_5['Open'][-1]


# def live_price(tickerr):
#     global samco
#     a = samco.get_quote(symbol_name=tickerr, exchange=samco.EXCHANGE_NSE)
#     a = eval(a)
#     ltp = a["lastTradedPrice"]
#     ltp = ltp.replace(',', '')
#     ltp = float(ltp)
#     return ltp


def live_price(s):
    global user_agent_rotator
    url = 'https://query2.finance.yahoo.com/v10/finance/quoteSummary/{}.ns?modules=price'.format(s)
    user_agent = user_agent_rotator.get_random_user_agent()
    headers = {'User-Agent': user_agent}
    r = requests.get(url, headers)
    data = r.json()
    return data['quoteSummary']['result'][0]['price']['regularMarketPrice']['raw']


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


def PO_body(a,b,c,d):
    global samco, qty , price_open, Stock_samco
    bodyy= {"symbolName": Stock_samco, "exchange": samco.EXCHANGE_NSE,"transactionType": samco.TRANSACTION_TYPE_BUY,
            "orderType": samco.ORDER_TYPE_MARKET,"price": "","quantity": qty,"disclosedQuantity": "",
            "orderValidity": samco.VALIDITY_DAY,"productType": samco.PRODUCT_MIS, "afterMarketOrderFlag": "NO"}
    if a=='sell':
        bodyy["transactionType"]=samco.TRANSACTION_TYPE_SELL
    if b=='limit':
        bodyy["orderType"]=samco.ORDER_TYPE_LIMIT
        bodyy["price"]=c
    if d=='cnc':
        bodyy["productType"]=samco.PRODUCT_CNC
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

print('Minimum Amount is Rs 30K')

amount = int(input('HOW MUCH AMOUNT TO TRADE TODAYYY = '))
order_type = input("Enter order type cnc or mis : ")

startt_time = [int(x) for x in input('Enter Start time in 24 hrs format ---hours <space> minutes = ').split()]
endd_time = [int(x) for x in input('Enter End time in 24 hrs format ---hours <space> minutes = ').split()]


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


while True:
    if time_exceed(endd_time[0],endd_time[1],0,0):
        samco_holdings = samco.get_holding()
        dict_samco_holdings = eval(samco_holdings)
        if dict_samco_holdings["holdingDetails"]:
            telegram_trade_messeges('holdings are there CHECK app')
        telegram_trade_messeges('THE END')
        telegram_trade_messeges('IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII')
        break
    if time_exceed(startt_time[0],startt_time[1],0,0):
        print('Trade m-c is Started---')
        telegram_trade_messeges('IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII')
        telegram_trade_messeges('THE START')
        while True:
            if time_exceed(endd_time[0], endd_time[1], 0, 0):
                break
            while True:
                cond = dt.now()
                if cond.minute % 5 == 0 and cond.second >= 7 and cond.second <= 20:
                    break
            print('checking stochRSI NEW Iteration')
            telegram_trade_messeges('checking stochRSI NEW Iteration')
            Stock100,Stock0,Stock100_price_open100,Stock0_price_open0=[],[],[],[]
            for Stock2 in Stock1:
                stochRSI, df_last_5_values, price_open = stochrsi(Stock2)
                stochRSI = float('{:.3f}'.format(100 * stochRSI))
                if stochRSI==100:
                    Stock100.append(dict_Stock2[Stock2])
                    Stock100.append(price_open)
                    Stock100_price_open100.append(Stock100)
                    Stock100=[]
                if stochRSI==0:
                    Stock0.append(dict_Stock2[Stock2])
                    Stock0.append(price_open)
                    Stock0_price_open0.append(Stock0)
                    Stock0 = []

            if Stock100_price_open100 or Stock0_price_open0:
                time_1 = dt.now()
                Stock7100, Stock80, Stock7100_price_open5100, Stock80_price_open60 = [], [], [], []
                while True:
                    for Stock5 , price_open in Stock100_price_open100:
                        price = live_price(Stock5)
                        if price > hundred_rejection * price_open:
                            Stock7100.append(Stock5)
                            Stock7100.append(price_open)
                            Stock7100_price_open5100.append(Stock7100)
                            Stock7100=[]

                    for Stock6 , price_open in Stock0_price_open0:
                        price = live_price(Stock6)
                        if price < zero_rejection * price_open:
                            Stock80.append(Stock6)
                            Stock80.append(price_open)
                            Stock80_price_open60.append(Stock80)
                            Stock80 = []

                    if Stock7100_price_open5100:
                        for Stock9 , price_open34 in Stock7100_price_open5100:
                            price = live_price(Stock9)
                            if price <= price_open34:
                                Stock_samco = Stock9
                                price_open=price_open34
                                placeo_100 = 1

                    if Stock80_price_open60 and placeo_100==0:
                        for Stock10 , price_open34 in Stock80 , price_open60:
                            price = live_price(Stock10)
                            if price >= price_open34:
                                Stock_samco = Stock10
                                price_open = price_open34
                                placeo_0 = 1

                    if placeo_100 == 1 or placeo_0 == 1:
                        break
                    if time_exceed(time_1.hour, time_1.minute + time_m_min, time_1.second + time_m_sec,time_1.microsecond):
                        print('4 min done so no trade')
                        telegram_trade_messeges('trade cancelled as four minutes are up')
                        break


                if placeo_100==1 and order_type != 'cnc':
                    placeo_100=0
                    qty = math.ceil(amount / (1.01 * price_open))
                    qty = str(qty)

                    print(df_last_5_values)
                    print('\nWEoooooo WE got the Stock ---', Stock_samco, '----', 'stochRSI===100')
                    print('\nprice_open===', price_open)
                    telegram_trade_messeges(string_remove_char('WEoooooo WE got the Stock ---' + Stock_samco + '----' + 'stochRSI is 100 ' + '   price 1 is    ' + str(price_open)))

                    PO = samco.place_order(body=PO_body('sell', 'm', 'na', order_type))
                    dict_PO = eval(PO)
                    while True:
                        Order_status = samco.get_order_status(order_number=dict_PO["orderNumber"])
                        dict_Order_status = eval(Order_status)
                        if dict_Order_status["orderStatus"] == "EXECUTED":
                            print('SELL EXECUTED   avgExecutionPrice is ' + dict_Order_status["orderDetails"]["avgExecutionPrice"])
                            telegram_trade_messeges(string_remove_char('SELL EXECUTED   avgExecutionPrice is ' + dict_Order_status["orderDetails"]["avgExecutionPrice"]))
                            PO_1 = samco.place_order(
                                body=PO_body('b', 'limit', str(0.05 * math.ceil(hundred_target * price_open)),order_type))
                            dict_PO_1 = eval(PO_1)
                            while True:
                                Order_status_1 = samco.get_order_status(order_number=dict_PO_1["orderNumber"])
                                dict_Order_status_1 = eval(Order_status_1)
                                if dict_Order_status_1["orderStatus"] == "EXECUTED":
                                    print('BUY EXECUTED   avgExecutionPrice is ' + dict_Order_status_1["orderDetails"]["avgExecutionPrice"])
                                    telegram_trade_messeges(string_remove_char('BUY EXECUTED   avgExecutionPrice is ' + dict_Order_status_1["orderDetails"]["avgExecutionPrice"]))
                                    done = 1
                                    break
                                price = live_price(Stock_samco)
                                if price > hundred_SL * price_open:
                                    done = 2
                                    break
                                if time_exceed(endd_time[0], endd_time[1], 0, 0):
                                    done = 3
                                    break
                            if done == 1:
                                done = 0
                                break
                            if done == 2:
                                done = 0
                                PO_2 = samco.modify_order(order_number=dict_PO_1["orderNumber"],body={"orderType": samco.ORDER_TYPE_MARKET, "price": ""})
                                while True:
                                    Order_status_2 = samco.get_order_status(order_number=dict_PO_1["orderNumber"])
                                    dict_Order_status_2 = eval(Order_status_2)
                                    if dict_Order_status_2["orderStatus"] == "EXECUTED":
                                        print('BUY EXECUTED   avgExecutionPrice is ' +dict_Order_status_2["orderDetails"]["avgExecutionPrice"])
                                        telegram_trade_messeges(string_remove_char('BUY EXECUTED   avgExecutionPrice is ' +dict_Order_status_2["orderDetails"]["avgExecutionPrice"]))
                                        break
                                break
                            if done == 3:
                                done = 0
                                PO_3 = samco.modify_order(order_number=dict_PO_1["orderNumber"],body={"orderType": samco.ORDER_TYPE_MARKET, "price": ""})
                                while True:
                                    Order_status_3 = samco.get_order_status(order_number=dict_PO_1["orderNumber"])
                                    dict_Order_status_3 = eval(Order_status_3)
                                    if dict_Order_status_3["orderStatus"] == "EXECUTED":
                                        print('BUY EXECUTED   avgExecutionPrice is ' +dict_Order_status_3["orderDetails"]["avgExecutionPrice"])
                                        telegram_trade_messeges(string_remove_char('BUY EXECUTED   avgExecutionPrice is ' +dict_Order_status_3["orderDetails"]["avgExecutionPrice"]))
                                        break
                            break


                if placeo_0==1:
                    placeo_0=0
                    qty = math.ceil(amount / (1.01 * price_open))
                    qty = str(qty)

                    print(df_last_5_values)
                    print('\nWEoooooo WE got the Stock ---', Stock_samco, '----', 'stochRSI===0')
                    print('\nprice_open===', price_open)
                    telegram_trade_messeges(string_remove_char('WEoooooo WE got the Stock ---' + Stock_samco + '----' + 'stochRSI is 0 ' + '   price 1 is    ' + str(price_open)))

                    PO = samco.place_order(body=PO_body('buy', 'm', 'na', order_type))
                    dict_PO = eval(PO)
                    while True:
                        Order_status = samco.get_order_status(order_number=dict_PO["orderNumber"])
                        dict_Order_status = eval(Order_status)
                        if dict_Order_status["orderStatus"] == "EXECUTED":
                            print('BUY EXECUTED   avgExecutionPrice is ' + dict_Order_status["orderDetails"]["avgExecutionPrice"])
                            telegram_trade_messeges(string_remove_char('BUY EXECUTED   avgExecutionPrice is ' + dict_Order_status["orderDetails"]["avgExecutionPrice"]))
                            PO_1 = samco.place_order(body=PO_body('sell', 'limit', str(0.05 * math.ceil(zero_target * price_open)),order_type))
                            dict_PO_1 = eval(PO_1)
                            while True:
                                Order_status_1 = samco.get_order_status(order_number=dict_PO_1["orderNumber"])
                                dict_Order_status_1 = eval(Order_status_1)
                                if dict_Order_status_1["orderStatus"] == "EXECUTED":
                                    print('SELL EXECUTED   avgExecutionPrice is ' + dict_Order_status_1["orderDetails"]["avgExecutionPrice"])
                                    telegram_trade_messeges(string_remove_char('SELL EXECUTED   avgExecutionPrice is ' + dict_Order_status_1["orderDetails"]["avgExecutionPrice"]))
                                    done = 1
                                    break
                                price = live_price(Stock_samco)
                                if price < zero_SL * price_open:
                                    done = 2
                                    break
                                if time_exceed(endd_time[0], endd_time[1], 0, 0):
                                    done = 3
                                    break
                            if done == 1:
                                done = 0
                                break
                            if done == 2:
                                done = 0
                                PO_2 = samco.modify_order(order_number=dict_PO_1["orderNumber"],body={"orderType": samco.ORDER_TYPE_MARKET, "price": ""})
                                while True:
                                    Order_status_2 = samco.get_order_status(order_number=dict_PO_1["orderNumber"])
                                    dict_Order_status_2 = eval(Order_status_2)
                                    if dict_Order_status_2["orderStatus"] == "EXECUTED":
                                        print('SELL EXECUTED   avgExecutionPrice is ' +dict_Order_status_2["orderDetails"]["avgExecutionPrice"])
                                        telegram_trade_messeges(string_remove_char('SELL EXECUTED   avgExecutionPrice is ' +dict_Order_status_2["orderDetails"]["avgExecutionPrice"]))
                                        break
                                break
                            if done == 3:
                                done = 0
                                PO_3 = samco.modify_order(order_number=dict_PO_1["orderNumber"],body={"orderType": samco.ORDER_TYPE_MARKET, "price": ""})
                                while True:
                                    Order_status_3 = samco.get_order_status(order_number=dict_PO_1["orderNumber"])
                                    dict_Order_status_3 = eval(Order_status_3)
                                    if dict_Order_status_3["orderStatus"] == "EXECUTED":
                                        print('SELL EXECUTED   avgExecutionPrice is ' +dict_Order_status_3["orderDetails"]["avgExecutionPrice"])
                                        telegram_trade_messeges(string_remove_char('SELL EXECUTED   avgExecutionPrice is ' +dict_Order_status_3["orderDetails"]["avgExecutionPrice"]))
                                        break
                            break

print('program ended')
samco.logout()
