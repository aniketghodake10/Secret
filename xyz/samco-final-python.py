import math
import pandas_datareader as web
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime as dt
from datetime import timedelta as td
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

a_thread=1
check = 0
exceed = 0
done = 0
placeo = 0
aa = 1
time_m = td(seconds=200)


def time_exceed(time_in_hours_24hour_format):
    time2 = dt.now()
    if time2.hour >= time_in_hours_24hour_format:
        global exceed
        exceed = time_in_hours_24hour_format


def stochrsi(tickerr, period: int = 14, smoothK: int = 3, smoothD: int = 3):
    df_5 = yf.download(tickers=tickerr, period='2h', interval='5m')
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

    stochrsii = (rsii - rsii.rolling(period).min()) / (
            rsii.rolling(period).max() - rsii.rolling(period).min())
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
Stock_samco_EQ = []
for i in Stock_samco1:
    j = i + '.NS'
    k = i + '-EQ'
    Stock1.append(j)
    Stock_samco_EQ.append(k)
dict_Stock1 = dict(zip(Stock1, Stock_samco_EQ))
dict_Stock2 = dict(zip(Stock1, Stock_samco1))

qty = int(input('HOW MUCH QUANTITY TO TRADE TODAYYY = '))
qty = str(qty)

startt_time = int(input('Enter Start time in hrs in 24hr format = '))
endd_time = int(input('Enter End time in hrs in 24hr format = '))

csv_1 = pd.read_csv('ScripMaster.csv')
u = csv_1.loc[:, 'symbolCode':'symbolCode']
v = csv_1.loc[:, 'tradingSymbol':'tradingSymbol']
w = v.join(u)
dict_symbolCode = dict(zip(w.tradingSymbol, w.symbolCode))


class Scrip(Thread):
    def __init__(self, Stock):
        global a_thread, check, exceed, done, placeo, aa, time_m, software_names, operating_systems, user_agent_rotator, samco, Stock_samco_1, Stock1, Stock_samco_EQ, dict_Stock1, dict_Stock2, qty, startt_time, endd_time, dict_symbolCode
        Thread.__init__(self)
        self.Stock = Stock
        while True:
            time_exceed(endd_time)
            if exceed == endd_time:
                samco_positions = samco.get_positions_data(position_type=samco.POSITION_TYPE_DAY)
                if samco_positions.find('companyName') != -1:
                    telegram_trade_messeges('positions are there CHECK app')
                samco_holdings = samco.get_holding()
                if samco_holdings.find('tradingSymbol') != -1:
                    telegram_trade_messeges('holdings are there CHECK app')
                telegram_trade_messeges('THE END')
                telegram_trade_messeges('IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII')
                break
            time_exceed(startt_time)
            if exceed == startt_time:
                print('Trade m-c is Started---')
                telegram_trade_messeges('IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII')
                telegram_trade_messeges('THE START')
                while True:
                    time_exceed(endd_time)
                    if exceed == endd_time:
                        break
                    telegram_trade_messeges('searching for stocks NEW Ireration')
                    while True:
                        if a_thread==1:
                            break
                    while True:
                        cond = dt.now()
                        if cond.minute % 5 == 0 and cond.second == 0 and cond.microsecond < 999999:
                            break
                    print('searching for stocks NEW Ireration')
                    stochRSI, df_ltp, df_last_5_values = stochrsi(Stock)
                    stochRSI = float('{:.3f}'.format(100 * stochRSI))
                    symbolCode = dict_symbolCode[dict_Stock1[Stock]]
                    Stock_samco = dict_Stock2[Stock]

                    if stochRSI == 100:
                        time_1 = dt.now()
                        while True:
                            price = live_price(Stock)
                            if aa == 1:
                                price_1 = price
                                print(df_last_5_values)
                                print('\nWEoooooo WE got the Stock ---', Stock, '----', 'stochRSI===', stochRSI)
                                print('\nprice_1===', price_1)
                                telegram_trade_messeges(
                                    Stock.replace('.NS', ' ') + 'price 1  is  ' + str(price_1).replace('.', ' '))
                                aa = 2
                            if price > 1.001 * price_1:
                                time_2 = dt.now()
                                while True:
                                    price = live_price(Stock)
                                    if price <= price_1:
                                        a_thread = 0
                                        placeo = 1
                                        break
                                    time_3 = dt.now()
                                    time_diff_2 = time_3 - time_2
                                    if (time_diff_2 >= time_m) == True:
                                        print('2 min done so no trade')
                                        telegram_trade_messeges('trade cancelled as two minutes are up')
                                        break
                                break
                            time_4 = dt.now()
                            time_diff_1 = time_4 - time_1
                            if (time_diff_1 >= time_m) == True:
                                print('2 min done so no trade')
                                telegram_trade_messeges('trade cancelled as two minutes are up')
                                break

                        if placeo == 1:
                            placeo = 0
                            PO = samco.place_order(
                                body={"symbolName": Stock_samco, "exchange": samco.EXCHANGE_NSE,
                                      "transactionType": samco.TRANSACTION_TYPE_SELL,
                                      "orderType": samco.ORDER_TYPE_MARKET, "price": "",
                                      "quantity": qty, "disclosedQuantity": "",
                                      "orderValidity": samco.VALIDITY_DAY,
                                      "productType": samco.PRODUCT_MIS,
                                      "afterMarketOrderFlag": "NO"})
                            dict_PO = eval(PO)
                            while True:
                                Order_status = samco.get_order_status(order_number=dict_PO["orderNumber"])
                                dict_Order_status = eval(Order_status)
                                if dict_Order_status["orderStatus"] == "EXECUTED":
                                    telegram_trade_messeges('SELL EXECUTED')
                                    print('SELL EXECUTED')
                                    samco_positions_1 = samco.get_positions_data(
                                        position_type=samco.POSITION_TYPE_DAY)
                                    samco_positions_find_1 = samco_positions_1.find('averageBuyPrice')
                                    samco_positions_find_2 = samco_positions_1.find('averageSellPrice')
                                    print('avgBUYprice===', samco_positions_1[
                                                            samco_positions_find_1 + 17:samco_positions_find_1 + 27],
                                          'avgSELLprice===', samco_positions_1[
                                                             samco_positions_find_2 + 17:samco_positions_find_2 + 27])
                                    PO_1 = samco.place_order(
                                        body={"symbolName": Stock_samco, "exchange": samco.EXCHANGE_NSE,
                                              "transactionType": samco.TRANSACTION_TYPE_BUY,
                                              "orderType": samco.ORDER_TYPE_LIMIT,
                                              "price": str(0.05 * math.ceil(19.94 * price_1)),
                                              "quantity": qty,
                                              "disclosedQuantity": "", "orderValidity": samco.VALIDITY_DAY,
                                              "productType": samco.PRODUCT_MIS, "afterMarketOrderFlag": "NO"})
                                    dict_PO_1 = eval(PO_1)
                                    while True:
                                        Order_status_1 = samco.get_order_status(
                                            order_number=dict_PO_1["orderNumber"])
                                        dict_Order_status_1 = eval(Order_status_1)
                                        if dict_Order_status_1["orderStatus"] == "EXECUTED":
                                            telegram_trade_messeges('BUY EXECUTED trade done')
                                            print('BUY EXECUTED')
                                            samco_positions_1 = samco.get_positions_data(
                                                position_type=samco.POSITION_TYPE_DAY)
                                            samco_positions_find_1 = samco_positions_1.find('averageBuyPrice')
                                            samco_positions_find_2 = samco_positions_1.find('averageSellPrice')
                                            print('avgBUYprice===', samco_positions_1[
                                                                    samco_positions_find_1 + 17:samco_positions_find_1 + 27],
                                                  'avgSELLprice===', samco_positions_1[
                                                                     samco_positions_find_2 + 17:samco_positions_find_2 + 27])
                                            done = 1
                                            break
                                        price = live_price(Stock)
                                        if price > 1.0035 * price_1:
                                            done = 2
                                            break
                                        time_exceed(endd_time)
                                        if exceed == endd_time:
                                            done = 3
                                            break
                                    if done == 1:
                                        done = 0
                                        break
                                    if done == 2:
                                        done = 0
                                        PO_2 = samco.modify_order(order_number=dict_PO_1["orderNumber"], body={
                                            "orderType": samco.ORDER_TYPE_MARKET,
                                            "price": ""})
                                        while True:
                                            Order_status_2 = samco.get_order_status(
                                                order_number=dict_PO_1["orderNumber"])
                                            dict_Order_status_2 = eval(Order_status_2)
                                            if dict_Order_status_2["orderStatus"] == "EXECUTED":
                                                telegram_trade_messeges('BUY EXECUTED trade done')
                                                print('BUY EXECUTED')
                                                samco_positions_1 = samco.get_positions_data(
                                                    position_type=samco.POSITION_TYPE_DAY)
                                                samco_positions_find_1 = samco_positions_1.find('averageBuyPrice')
                                                samco_positions_find_2 = samco_positions_1.find('averageSellPrice')
                                                print('avgBUYprice===', samco_positions_1[
                                                                        samco_positions_find_1 + 17:samco_positions_find_1 + 27],
                                                      'avgSELLprice===', samco_positions_1[
                                                                         samco_positions_find_2 + 17:samco_positions_find_2 + 27])
                                                break
                                        break
                                    if done == 3:
                                        done = 0
                                        PO_3 = samco.modify_order(order_number=dict_PO_1["orderNumber"],
                                                                  body={
                                                                      "orderType": samco.ORDER_TYPE_MARKET,
                                                                      "price": ""})
                                        while True:
                                            Order_status_3 = samco.get_order_status(
                                                order_number=dict_PO_1["orderNumber"])
                                            dict_Order_status_3 = eval(Order_status_3)
                                            if dict_Order_status_3["orderStatus"] == "EXECUTED":
                                                telegram_trade_messeges('BUY EXECUTED trade done')
                                                print('BUY EXECUTED')
                                                samco_positions_1 = samco.get_positions_data(
                                                    position_type=samco.POSITION_TYPE_DAY)
                                                samco_positions_find_1 = samco_positions_1.find('averageBuyPrice')
                                                samco_positions_find_2 = samco_positions_1.find('averageSellPrice')
                                                print('avgBUYprice===', samco_positions_1[
                                                                        samco_positions_find_1 + 17:samco_positions_find_1 + 27],
                                                      'avgSELLprice===', samco_positions_1[
                                                                         samco_positions_find_2 + 17:samco_positions_find_2 + 27])
                                                break
                                    break
                        aa = 1
                        a_thread = 1

                    if stochRSI == 0:
                        time_1 = dt.now()
                        while True:
                            price = live_price(Stock)
                            if aa == 1:
                                price_1 = price
                                print('price_1===', price_1)
                                telegram_trade_messeges(
                                    Stock.replace('.NS', ' ') + 'price 1  is  ' + str(price_1).replace('.', ' '))
                                aa = 2
                            if price < 0.999 * price_1:
                                time_2 = dt.now()
                                while True:
                                    price = live_price(Stock)
                                    if price >= price_1:
                                        a_thread = 0
                                        placeo = 1
                                        break
                                    time_3 = dt.now()
                                    time_diff_2 = time_3 - time_2
                                    if (time_diff_2 >= time_m) == True:
                                        print('2 min done so no trade')
                                        telegram_trade_messeges('trade cancelled as two minutes are up')
                                        break
                                break
                            time_4 = dt.now()
                            time_diff_1 = time_4 - time_1
                            if (time_diff_1 >= time_m) == True:
                                print('2 min done so no trade')
                                telegram_trade_messeges('trade cancelled as two minutes are up')
                                break

                        if placeo == 1:
                            placeo = 0
                            PO = samco.place_order(
                                body={"symbolName": Stock_samco, "exchange": samco.EXCHANGE_NSE,
                                      "transactionType": samco.TRANSACTION_TYPE_BUY,
                                      "orderType": samco.ORDER_TYPE_MARKET, "price": "",
                                      "quantity": qty, "disclosedQuantity": "",
                                      "orderValidity": samco.VALIDITY_DAY,
                                      "productType": samco.PRODUCT_MIS,
                                      "afterMarketOrderFlag": "NO"})
                            dict_PO = eval(PO)
                            while True:
                                Order_status = samco.get_order_status(order_number=dict_PO["orderNumber"])
                                dict_Order_status = eval(Order_status)
                                if dict_Order_status["orderStatus"] == "EXECUTED":
                                    telegram_trade_messeges('BUY EXECUTED')
                                    print('BUY EXECUTED')
                                    samco_positions_1 = samco.get_positions_data(
                                        position_type=samco.POSITION_TYPE_DAY)
                                    samco_positions_find_1 = samco_positions_1.find('averageBuyPrice')
                                    samco_positions_find_2 = samco_positions_1.find('averageSellPrice')
                                    print('avgBUYprice===', samco_positions_1[
                                                            samco_positions_find_1 + 17:samco_positions_find_1 + 27],
                                          'avgSELLprice===', samco_positions_1[
                                                             samco_positions_find_2 + 17:samco_positions_find_2 + 27])
                                    PO_1 = samco.place_order(
                                        body={"symbolName": Stock_samco, "exchange": samco.EXCHANGE_NSE,
                                              "transactionType": samco.TRANSACTION_TYPE_SELL,
                                              "orderType": samco.ORDER_TYPE_LIMIT,
                                              "price": str(0.05 * math.ceil(20.06 * price_1)),
                                              "quantity": qty,
                                              "disclosedQuantity": "", "orderValidity": samco.VALIDITY_DAY,
                                              "productType": samco.PRODUCT_MIS, "afterMarketOrderFlag": "NO"})
                                    dict_PO_1 = eval(PO_1)
                                    while True:
                                        Order_status_1 = samco.get_order_status(
                                            order_number=dict_PO_1["orderNumber"])
                                        dict_Order_status_1 = eval(Order_status_1)
                                        if dict_Order_status_1["orderStatus"] == "EXECUTED":
                                            telegram_trade_messeges('SELL EXECUTED trade done')
                                            print('SELL EXECUTED')
                                            samco_positions_1 = samco.get_positions_data(
                                                position_type=samco.POSITION_TYPE_DAY)
                                            samco_positions_find_1 = samco_positions_1.find('averageBuyPrice')
                                            samco_positions_find_2 = samco_positions_1.find('averageSellPrice')
                                            print('avgBUYprice===', samco_positions_1[
                                                                    samco_positions_find_1 + 17:samco_positions_find_1 + 27],
                                                  'avgSELLprice===', samco_positions_1[
                                                                     samco_positions_find_2 + 17:samco_positions_find_2 + 27])
                                            done = 1
                                            break
                                        price = live_price(Stock)
                                        if price < 0.9965 * price_1:
                                            done = 2
                                            break
                                        time_exceed(endd_time)
                                        if exceed == endd_time:
                                            done = 3
                                            break
                                    if done == 1:
                                        done = 0
                                        break
                                    if done == 2:
                                        done = 0
                                        PO_2 = samco.modify_order(order_number=dict_PO_1["orderNumber"], body={
                                            "orderType": samco.ORDER_TYPE_MARKET,
                                            "price": ""})
                                        while True:
                                            Order_status_2 = samco.get_order_status(
                                                order_number=dict_PO_1["orderNumber"])
                                            dict_Order_status_2 = eval(Order_status_2)
                                            if dict_Order_status_2["orderStatus"] == "EXECUTED":
                                                telegram_trade_messeges('SELL EXECUTED trade done')
                                                print('SELL EXECUTED')
                                                samco_positions_1 = samco.get_positions_data(
                                                    position_type=samco.POSITION_TYPE_DAY)
                                                samco_positions_find_1 = samco_positions_1.find('averageBuyPrice')
                                                samco_positions_find_2 = samco_positions_1.find('averageSellPrice')
                                                print('avgBUYprice===', samco_positions_1[
                                                                        samco_positions_find_1 + 17:samco_positions_find_1 + 27],
                                                      'avgSELLprice===', samco_positions_1[
                                                                         samco_positions_find_2 + 17:samco_positions_find_2 + 27])
                                                break
                                        break
                                    if done == 3:
                                        done = 0
                                        PO_3 = samco.modify_order(order_number=dict_PO_1["orderNumber"],
                                                                  body={
                                                                      "orderType": samco.ORDER_TYPE_MARKET,
                                                                      "price": ""})
                                        while True:
                                            Order_status_3 = samco.get_order_status(
                                                order_number=dict_PO_1["orderNumber"])
                                            dict_Order_status_3 = eval(Order_status_3)
                                            if dict_Order_status_3["orderStatus"] == "EXECUTED":
                                                telegram_trade_messeges('SELL EXECUTED trade done')
                                                print('SELL EXECUTED')
                                                samco_positions_1 = samco.get_positions_data(
                                                    position_type=samco.POSITION_TYPE_DAY)
                                                samco_positions_find_1 = samco_positions_1.find('averageBuyPrice')
                                                samco_positions_find_2 = samco_positions_1.find('averageSellPrice')
                                                print('avgBUYprice===', samco_positions_1[
                                                                        samco_positions_find_1 + 17:samco_positions_find_1 + 27],
                                                      'avgSELLprice===', samco_positions_1[
                                                                         samco_positions_find_2 + 17:samco_positions_find_2 + 27])
                                                break
                                    break
                        aa = 1
                        a_thread = 1


obj = []
for i in Stock1:
    object = Scrip(Stock=i)
    obj.append(object)

while True:
    time_exceed(startt_time)
    if exceed == startt_time:
        for i in obj:
            i.start()
        break



print('program ended')
samco.logout()
