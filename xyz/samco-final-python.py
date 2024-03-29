import math
# import pandas_datareader as web
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime as dt
# from datetime import timedelta as td
# from bs4 import BeautifulSoup
from snapi_py_client.snapi_bridge import StocknoteAPIPythonBridge
import requests
# from random_user_agent.user_agent import UserAgent
# from random_user_agent.params import SoftwareName, OperatingSystem
import time
import os
from threading import *

#---     FUNCTIONS  ---

hundred_rejection = 1.0014
hundred_target = 0.997
hundred_SL = 1.008
hundred_last_confirmation = 0.9991
hundred_last_confirmation_2 = 0.9973
hundred_last_confirmation_3 = 0.9985
zero_rejection = 0.9986
zero_target = 1.003
zero_SL = 0.992
zero_last_confirmation = 1.0009
zero_last_confirmation_2 = 1.0027
zero_last_confirmation_3 = 1.0015

conf = 0
exceed = 0
time_m_min = 4
time_m_sec = 25


def stochrsi_K(tickerr, period: int = 14, smoothK: int = 3, smoothD: int = 3):
    global conf
    time_m_sec = 10
    time_1 = dt.now()
    while True:
        df_5 = yf.download(tickers=tickerr, period='2d', interval='5m')
        a = dt.now().minute
        if a % 5 != 0:
            if float(str(df_5.index[-1])[14:16]) == a and float(str(df_5.index[-2])[14:16]) == a - a % 5 and float(str(df_5.index[-3])[14:16]) == a - a % 5 - 5:
                conf = 1
                break
        if a % 5 == 0:
            if float(str(df_5.index[-1])[14:16]) == a and float(str(df_5.index[-2])[14:16]) == a - 5 and float(str(df_5.index[-3])[14:16]) == a - 10:
                conf = 1
                break
        if time_exceed(time_1.hour, time_1.minute, time_1.second + time_m_sec, time_1.microsecond):
            printt_telegram('yfinance failed trade cancelled as twenty seconds are up')
            break
    if conf == 1:
        conf=0
        df_6 = df_5[:-1]
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
        # stochrsii_D = stochrsii_K.rolling(smoothD).mean()
        print('.              .')

        return stochrsii_K[-1]
    else:
        return 50


def ohlc_data(tickerr):
    global conf
    time_m_sec = 10
    time_1 = dt.now()
    while True:
        df_5 = yf.download(tickers=tickerr, period='2d', interval='5m')
        a = dt.now().minute
        if a%5 != 0:
            if float(str(df_5.index[-1])[14:16]) == a and float(str(df_5.index[-2])[14:16]) == a - a % 5 and float(str(df_5.index[-3])[14:16]) == a - a % 5 - 5:
                conf = 1
                break
        if a%5 == 0:
            if float(str(df_5.index[-1])[14:16]) == a and float(str(df_5.index[-2])[14:16]) == a - 5 and float(str(df_5.index[-3])[14:16]) == a - 10:
                conf = 1
                break
        if time_exceed(time_1.hour, time_1.minute, time_1.second + time_m_sec, time_1.microsecond):
            printt_telegram('yfinance failed trade cancelled as twenty seconds are up')
            break
    if conf ==1 :
        conf=0
        df_5 = df_5[:-1]
        df_6 = df_5[:-1]
        df = df_6['Close']
        print('.              .')

        return df[-1], df_5['Open'][-1], df_6['Low'][-1], df_6['High'][-1], df_5['Low'][-1], df_5['High'][-1]
    else:
        return None,None,None,None,None,None


def live_price(tickerr):
    global samco, ltp
    try:
        time.sleep(0.4)
        a = samco.get_quote(symbol_name=tickerr, exchange=samco.EXCHANGE_NSE)
        a = eval(a)
        ltp = a["lastTradedPrice"]
        ltp = ltp.replace(',', '')
        ltp = float(ltp)
    except Exception as e:
        print(e)
        printt_telegram('live price ltp error')
    return ltp


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
    global qty, Stock_samco
    bodyy= {"symbolName": Stock_samco, "exchange": samco.EXCHANGE_NSE,"transactionType": samco.TRANSACTION_TYPE_BUY,
            "orderType": samco.ORDER_TYPE_MARKET,"price": "","quantity": qty,"disclosedQuantity": "",
            "orderValidity": samco.VALIDITY_DAY,"productType": samco.PRODUCT_MIS, "triggerPrice": "", "afterMarketOrderFlag": "NO"}
    if b != 'slm':
        del bodyy["triggerPrice"]
    if b =='market':
        del bodyy["price"]
    if a=='sell':
        bodyy["transactionType"]=samco.TRANSACTION_TYPE_SELL
    if b=='limit':
        bodyy["orderType"]=samco.ORDER_TYPE_LIMIT
        bodyy["price"]=c
    if b=='slm':
        del bodyy["price"]
        bodyy["orderType"] = samco.ORDER_TYPE_SLM
        bodyy["triggerPrice"]=c
    if d=='cnc':
        bodyy["productType"]=samco.PRODUCT_CNC
    return bodyy


def time_exceed(a,b,c,d):
    global startt_day, startt_month, startt_year
    now=dt.now()
    if d>999999:
        d=d-1000000
        c=c+1
    if c>59:
        c=c-60
        b=b+1
    if b>59:
        b=b-60
        a=a+1
    if now.year > startt_year or now.month > startt_year or now.day > startt_day:
        a = a - 24
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
        if h>=d:
            return True


def cond(a,b,c):
    while True:
        cond = dt.now()
        if cond.minute % 5 == a and cond.second >= b and cond.second <= c:
            break


def printt_telegram(a):
    print(a)
    telegram_trade_messeges(string_remove_char(a))


def order_status_dict(a):
    Order_status = samco.get_order_status(order_number=a["orderNumber"])
    dict_Order_status = eval(Order_status)
    return  dict_Order_status


def square_off(a):
    done = 0
    if a == zero_target:
        price = live_price(Stock_samco)
        if price >= a * avg:
            while True:
                price = live_price(Stock_samco)
                if price <= a * avg:
                    PO_1 = samco.place_order(body=PO_body('sell', 'market', 'na', order_type))
                    break
                if price >= (a + 0.0005) * avg:
                    while True:
                        price = live_price(Stock_samco)
                        if price <= a * avg:
                            PO_1 = samco.place_order(body=PO_body('sell', 'market', 'na', order_type))
                            break
                        if price >= (a + 0.001) * avg:
                            while True:
                                price = live_price(Stock_samco)
                                if price <= a * avg:
                                    PO_1 = samco.place_order(body=PO_body('sell', 'market', 'na', order_type))
                                    break
                                if price >= (a + 0.0015) * avg:
                                    while True:
                                        price = live_price(Stock_samco)
                                        if price <= (a + 0.0005) * avg:
                                            PO_1 = samco.place_order(body=PO_body('sell', 'market', 'na', order_type))
                                            break
                                        if price >= (a + 0.002) * avg:
                                            PO_1 = samco.place_order(body=PO_body('sell', 'market', 'na', order_type))
                                            break
                                    break
                            break
                    break
            dict_PO_1 = eval(PO_1)
            while True:
                if order_status_dict(dict_PO_1)["orderStatus"] == "EXECUTED":
                    printt_telegram('SELL EXECUTED   avgExecutionPrice is ' + order_status_dict(dict_PO_1)["orderDetails"]["avgExecutionPrice"])
                    PO_cancel = samco.cancel_order(order_number=dict_PO_2["orderNumber"])
                    dict_PO_cancel = eval(PO_cancel)
                    while True:
                        if dict_PO_cancel["statusMessage"] == "Order cancelled successfully":
                            printt_telegram('SL order cancelled as target hit')
                            done=1
                            break
                    break

    if a == hundred_target:
        price = live_price(Stock_samco)
        if price <= a * avg:
            while True:
                price = live_price(Stock_samco)
                if price >= a * avg:
                    PO_1 = samco.place_order(body=PO_body('buy', 'market', 'na', order_type))
                    break
                if price <= (a - 0.0005) * avg:
                    while True:
                        price = live_price(Stock_samco)
                        if price >= a * avg:
                            PO_1 = samco.place_order(body=PO_body('buy', 'market', 'na', order_type))
                            break
                        if price <= (a - 0.001) * avg:
                            while True:
                                price = live_price(Stock_samco)
                                if price >= a * avg:
                                    PO_1 = samco.place_order(body=PO_body('buy', 'market', 'na', order_type))
                                    break
                                if price <= (a - 0.0015) * avg:
                                    while True:
                                        price = live_price(Stock_samco)
                                        if price >= (a - 0.0005) * avg:
                                            PO_1 = samco.place_order(body=PO_body('buy', 'market', 'na', order_type))
                                            break
                                        if price <= (a - 0.002) * avg:
                                            PO_1 = samco.place_order(body=PO_body('buy', 'market', 'na', order_type))
                                            break
                                    break
                            break
                    break
            dict_PO_1 = eval(PO_1)
            while True:
                if order_status_dict(dict_PO_1)["orderStatus"] == "EXECUTED":
                    printt_telegram('BUY EXECUTED   avgExecutionPrice is ' + order_status_dict(dict_PO_1)["orderDetails"]["avgExecutionPrice"])
                    PO_cancel = samco.cancel_order(order_number=dict_PO_2["orderNumber"])
                    dict_PO_cancel = eval(PO_cancel)
                    while True:
                        if dict_PO_cancel["statusMessage"] == "Order cancelled successfully":
                            printt_telegram('SL order cancelled as target hit')
                            done=1
                            break
                    break
    return done


def confirmation(Stock,stochRSI):
    Stock_samco = Stock[:-3]
    conf_list = []
    placeo=0
    global amount,hundred_rejection,hundred_last_confirmation,hundred_last_confirmation_2,hundred_last_confirmation_3,\
        time_1,time_m_min,time_m_sec,zero_rejection,zero_last_confirmation,zero_last_confirmation_2,\
        zero_last_confirmation_3
    while stochRSI > 99:
        cond(1,15,23)
        df_ltp, price_open, df_low, df_high, check_low, check_high = ohlc_data(Stock)
        if df_ltp == None:
            break
        qty = math.ceil(amount / (1.01 * price_open))
        qty = str(qty)
        printt_telegram('price_open is ' + str(price_open))
        while True:
            price = live_price(Stock_samco)
            if check_high >= hundred_rejection * price_open or price >= hundred_rejection * price_open:
                placeo = 1
                printt_telegram('first condition satisfied')
                break
            if df_high >= hundred_rejection * df_ltp:
                placeo = 1
                printt_telegram('first_1 condition satisfied')
                break
            if time_exceed(time_1.hour, time_1.minute + time_m_min, time_1.second + time_m_sec, time_1.microsecond):
                printt_telegram('trade cancelled as four minutes are up')
                break
        cond(4, 30, 55)
        _, _, _, _, check_low2, _ = ohlc_data(Stock)
        if check_low2 == None:
            break
        print('check low after four minutes is ', check_low2)
        cond(4, 57, 58)
        price = live_price(Stock_samco)
        if price > hundred_last_confirmation * price_open or price < hundred_last_confirmation_2 * price_open or price * hundred_last_confirmation_3 > check_low2:
            printt_telegram('Second condition failed')
            placeo = 0
        if placeo == 1 and not conf_list:
            conf_list.append(Stock_samco)
            conf_list.append(price_open)
            conf_list.append(qty)
            conf_list.append(stochRSI)
            if os.stat('confirmation.txt').st_size == 0:
                with open('confirmation.txt', 'w') as f:
                    f.write(str(conf_list))
        stochRSI=50

    while stochRSI < 1:
        cond(1, 15, 23)
        df_ltp, price_open, df_low, df_high, check_low, check_high = ohlc_data(Stock)
        if df_ltp == None:
            break
        qty = math.ceil(amount / (1.01 * price_open))
        qty = str(qty)
        printt_telegram('price_open is ' + str(price_open))
        while True:
            price = live_price(Stock_samco)
            if check_low <= zero_rejection * price_open or price <= zero_rejection * price_open:
                placeo = 1
                printt_telegram('first condition satisfied')
                break
            if df_low <= zero_rejection * df_ltp:
                placeo = 1
                printt_telegram('first_1 condition satisfied')
                break
            if time_exceed(time_1.hour, time_1.minute + time_m_min, time_1.second + time_m_sec, time_1.microsecond):
                printt_telegram('trade cancelled as four minutes are up')
                break
        cond(4, 30, 55)
        _, _, _, _, _, check_high2 = ohlc_data(Stock)
        if check_high2 == None:
            break
        print('check high after four minutes is ', check_high2)
        cond(4, 57, 58)
        price = live_price(Stock_samco)
        if price < zero_last_confirmation * price_open or price > zero_last_confirmation_2 * price_open or price * zero_last_confirmation_3 < check_high2:
            printt_telegram('Second condition failed')
            placeo = 0
        if placeo == 1 and not conf_list:
            conf_list.append(Stock_samco)
            conf_list.append(price_open)
            conf_list.append(qty)
            conf_list.append(stochRSI)
            if os.stat('confirmation.txt').st_size == 0:
                with open('confirmation.txt', 'w') as f:
                    f.write(str(conf_list))
        stochRSI = 50

#---     FUNCTIONS  ---



try:
    samco = StocknoteAPIPythonBridge()

    print('Minimum Amount is Rs 30K')

    amount = int(input('HOW MUCH AMOUNT TO TRADE TODAYYY = '))
    order_type = input("Enter order type cnc or mis : ")

    startt_time = [int(x) for x in input('Enter Start time in 24 hrs format ---hours <space> minutes = ').split()]
    print('If WORK at NIGHT after time 12:00 AM then put endd time as 25,26,27 not 0,1,2')
    endd_time = [int(x) for x in input('Enter End time in 24 hrs format ---hours <space> minutes = ').split()]

    userId = input("Enter Samco userId : ")
    password = input("Enter Samco Password : ")
    yob = input("Enter Samco Year Of Birth : ")
    login = samco.login(body={"userId": userId, 'password': password, 'yob': yob})
    print('Login Details\n', login)
    login = eval(login)

    samco.set_session_token(sessionToken=login['sessionToken'])

    Stock_samco1 = ['BAJFINANCE', 'SBIN', 'RELIANCE', 'HDFCBANK', 'HDFC', 'ICICIBANK', 'AXISBANK', 'DIVISLAB',
                    'JSWSTEEL', 'BAJAJFINSV', 'BAJAJ-AUTO', 'POWERGRID', 'TITAN', 'ADANIPORTS', 'ASIANPAINT',
                    'BPCL', 'BHARTIARTL', 'BRITANNIA', 'CIPLA', 'DRREDDY', 'EICHERMOT', 'GRASIM', 'HCLTECH',
                    'HDFCLIFE', 'HEROMOTOCO', 'HINDALCO', 'HINDUNILVR', 'ITC', 'INDUSINDBK', 'INFY', 'KOTAKBANK',
                    'LT', 'M&M', 'MARUTI', 'NESTLEIND', 'SBILIFE', 'SHREECEM', 'SUNPHARMA', 'TCS', 'TATAMOTORS',
                    'TATASTEEL', 'TECHM', 'UPL', 'ULTRACEMCO', 'WIPRO']

    Stock1 = []
    for i in Stock_samco1:
        j = i + '.NS'
        Stock1.append(j)

    startt_year = dt.now().year
    startt_month = dt.now().month
    startt_day = dt.now().day
    telegram_trade_messeges('Plz Restart the Bot')
    while True:
        if time_exceed(endd_time[0], endd_time[1], 0, 0):
            samco_holdings = samco.get_holding()
            dict_samco_holdings = eval(samco_holdings)
            if dict_samco_holdings["statusMessage"] == "User Holding details retrieved successfully":
                printt_telegram('holdings are there CHECK app')
            printt_telegram('THE END')
            printt_telegram('IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII')
            break
        if time_exceed(startt_time[0], startt_time[1], 0, 0):
            printt_telegram('IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII')
            printt_telegram('THE START')
            while True:
                if time_exceed(endd_time[0], endd_time[1], 0, 0):
                    break
                cond(0, 15, 23)
                time_1 = dt.now()
                printt_telegram('checking stochRSI NEW Iteration')
                Stock_list = []
                for Stock2 in Stock1:
                    stochRSII = stochrsi_K(Stock2)
                    stochRSII = float('{:.2f}'.format(100 * stochRSII))
                    if stochRSII > 99 or stochRSII < 1:
                        list1 = []
                        list1.append(Stock2)
                        list1.append(stochRSII)
                        Stock_list.append(list1)

                if Stock_list:
                    for i,j in Stock_list:
                        printt_telegram('WEoooooo WE got the Stock ---' + i[:-3] + '----' + 'stochRSI is   ' + str(j))
                        t1=Thread(target=confirmation, args=(i,j))
                        t1.start()
                    cond(4, 58, 59)
                    if os.stat('confirmation.txt').st_size != 0:
                        with open('confirmation.txt', 'w') as f:
                            readd = a = eval(f.read())
                        Stock_samco, price_open, qty, stochRSI = readd[0], readd[1], readd[2], readd[3]
                        printt_telegram('All conditions satisfied')

                    while os.stat('confirmation.txt').st_size != 0 and stochRSI > 99 and order_type != 'cnc':
                        with open('confirmation.txt', 'w') as f:
                            pass
                        PO = samco.place_order(body=PO_body('sell', 'market', 'na', order_type))
                        dict_PO = eval(PO)
                        avg = float('{:.2f}'.format(float(order_status_dict(dict_PO)["orderDetails"]["avgExecutionPrice"])))
                        while True:
                            if order_status_dict(dict_PO)["orderStatus"] == "EXECUTED":
                                printt_telegram('SELL EXECUTED   avgExecutionPrice is ' +order_status_dict(dict_PO)["orderDetails"]["avgExecutionPrice"])
                                PO_2 = samco.place_order(body=PO_body('buy', 'slm', str(0.05 * math.ceil((hundred_SL * avg) / 0.05)),order_type))
                                dict_PO_2 = eval(PO_2)
                                while True:
                                    price = live_price(Stock_samco)
                                    if price > 0.05 * math.ceil((hundred_SL * avg) / 0.05):
                                        if order_status_dict(dict_PO_2)["orderStatus"] == "EXECUTED":
                                            printt_telegram(' SL hit BUY EXECUTED   avgExecutionPrice is ' +order_status_dict(dict_PO_2)["orderDetails"]["avgExecutionPrice"])
                                            break
                                    if time_exceed(14, 50, 0, 0):
                                        PO_1 = samco.place_order(body=PO_body('buy', 'limit', str(0.05 * math.ceil((hundred_target * avg) / 0.05)), order_type))
                                        print(PO_1)
                                        printt_telegram('BUY order may be Auto square off as time is two fifty ')
                                        break
                                    if square_off(hundred_target) == 1:
                                        break
                                break
                    stochRSI = 50

                    while os.stat('confirmation.txt').st_size != 0 and stochRSI < 1:
                        with open('confirmation.txt', 'w') as f:
                            pass
                        PO = samco.place_order(body=PO_body('buy', 'market', 'na', order_type))
                        dict_PO = eval(PO)
                        avg = float('{:.2f}'.format(float(order_status_dict(dict_PO)["orderDetails"]["avgExecutionPrice"])))
                        while True:
                            if order_status_dict(dict_PO)["orderStatus"] == "EXECUTED":
                                printt_telegram('BUY EXECUTED   avgExecutionPrice is ' + str(avg))
                                PO_2 = samco.place_order(body=PO_body('sell', 'slm', str(0.05 * math.ceil((zero_SL * avg) / 0.05)),order_type))
                                dict_PO_2 = eval(PO_2)
                                while True:
                                    price = live_price(Stock_samco)
                                    if price < 0.05 * math.ceil((zero_SL * avg) / 0.05):
                                        if order_status_dict(dict_PO_2)["orderStatus"] == "EXECUTED":
                                            printt_telegram('SL hit SELL EXECUTED   avgExecutionPrice is ' +order_status_dict(dict_PO_2)["orderDetails"]["avgExecutionPrice"])
                                            break
                                    if time_exceed(14, 50, 0, 0):
                                        PO_1 = samco.place_order(body=PO_body('sell', 'limit', str(0.05 * math.ceil((zero_target * avg) / 0.05)), order_type))
                                        print(PO_1)
                                        printt_telegram('SELL order may be Auto square off as time is two fifty ')
                                        break
                                    if square_off(zero_target) == 1:
                                        break
                                break
                    stochRSI = 50
except Exception as e:
    print(e)
    printt_telegram('ERROR ERROR')

print('program ended')
samco.logout()
