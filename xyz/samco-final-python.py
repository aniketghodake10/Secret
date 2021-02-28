import math
import pandas_datareader as web
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime as dt
from datetime import timedelta as td

from snapi_py_client.snapi_bridge import StocknoteAPIPythonBridge
samco=StocknoteAPIPythonBridge()

userId=input("Enter Samco userId : ")
password=input("Enter Samco Password : ")
yob=input("Enter Samco Year Of Birth : ")
login=samco.login(body={"userId":userId,'password':password,'yob':yob})
print(login)
login=eval(login)

samco.set_session_token(sessionToken=login['sessionToken'])


Stock = input('Enter Stock Name in .NS form : ')
qty=int(input('Enter quantity = '))
qty=str(qty)
Stock_samco=Stock[:-3]
Stock_samco_EQ=Stock[:-3]+'-EQ'


csv_1=pd.read_csv('ScripMaster.csv')
u=csv_1.loc[:, 'symbolCode':'symbolCode']
v=csv_1.loc[:, 'tradingSymbol':'tradingSymbol']
w=v.join(u)
x=dict(zip(w.tradingSymbol,w.symbolCode))
symbolCode=x[Stock_samco_EQ]


time_m=td(seconds=300)


a=6
while(a>5):
    if dt.now().strftime("%I:%M %p")=="09:59 AM":
        b=6
        while(b>5):
            def stochrsi(tickerr, period: int = 14, smoothK: int = 3, smoothD: int = 3):
                df_5 = yf.download(tickers=tickerr, period='2d', interval='5m')
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

                return stochrsii_K[-1], df[-1]


            stochRSI, df_ltp=stochrsi(Stock)
            stochRSI = float('{:.3f}'.format(100 * stochRSI))



            if stochRSI==100 or stochRSI==0:
                if stochRSI == 100:
                    value = [{"symbol": symbolCode}]
                    samco.set_streaming_data(value)
                    samco_stream = samco.start_streaming()
                    dict_samco_stream = eval(samco_stream)

                    c = 6
                    time_1 = dt.now()
                    while (c > 5):
                        if float(dict_samco_stream['ltp']) > 1.001 * df_ltp:
                            d = 6
                            time_2 = dt.now()
                            while (d > 5):
                                if float(dict_samco_stream['ltp']) == df_ltp:
                                    PO = samco.place_order(
                                        body={"symbolName": Stock_samco, "exchange": samco.EXCHANGE_NSE,
                                              "transactionType": samco.TRANSACTION_TYPE_SELL,
                                              "orderType": samco.ORDER_TYPE_MARKET, "price": "",
                                              "quantity": qty, "disclosedQuantity": "",
                                              "orderValidity": samco.VALIDITY_DAY,
                                              "productType": samco.PRODUCT_MIS,
                                              "afterMarketOrderFlag": "NO"})
                                    dict_PO = eval(PO)
                                    e = 6
                                    while (e > 5):
                                        Order_status = samco.get_order_status(order_number=dict_PO["orderNumber"])
                                        dict_Order_status = eval(Order_status)
                                        if dict_Order_status["orderStatus"] == "EXECUTED":
                                            PO_1 = samco.place_order(
                                                body={"symbolName": Stock_samco, "exchange": samco.EXCHANGE_NSE,
                                                      "transactionType": samco.TRANSACTION_TYPE_BUY,
                                                      "orderType": samco.ORDER_TYPE_LIMIT, "price": str(0.997 * df_ltp),
                                                      "quantity": qty,
                                                      "disclosedQuantity": "", "orderValidity": samco.VALIDITY_DAY,
                                                      "productType": samco.PRODUCT_MIS, "afterMarketOrderFlag": "NO"})
                                            dict_PO_1 = eval(PO_1)
                                            f = 6
                                            while (f > 5):
                                                Order_status_1 = samco.get_order_status(
                                                    order_number=dict_PO_1["orderNumber"])
                                                dict_Order_status_1 = eval(Order_status_1)
                                                if dict_Order_status_1["orderStatus"] == "EXECUTED":
                                                    break
                                                elif float(dict_samco_stream["ltp"]) > 1.0035 * df_ltp:
                                                    PO_2 = samco.modify_order(order_number=dict_PO_1["orderNumber"],
                                                                              body={
                                                                                  "orderType": samco.ORDER_TYPE_MARKET,
                                                                                  "price": ""})
                                                    g = 6
                                                    while (g > 5):
                                                        Order_status_2 = samco.get_order_status(
                                                            order_number=dict_PO_1["orderNumber"])
                                                        dict_Order_status_2 = eval(Order_status_2)
                                                        if dict_Order_status_2["orderStatus"] == "EXECUTED":
                                                            break
                                                    break
                                                elif dt.now().strftime("%I:%M %p") == "02:00 PM":
                                                    PO_3 = samco.modify_order(order_number=dict_PO_1["orderNumber"],
                                                                              body={
                                                                                  "orderType": samco.ORDER_TYPE_MARKET,
                                                                                  "price": ""})
                                                    h = 6
                                                    while (h > 5):
                                                        Order_status_3 = samco.get_order_status(
                                                            order_number=dict_PO_1["orderNumber"])
                                                        dict_Order_status_3 = eval(Order_status_3)
                                                        if dict_Order_status_3["orderStatus"] == "EXECUTED":
                                                            break
                                                    break
                                            break
                                    break
                                time_3 = dt.now()
                                time_diff_2 = time_3 - time_2
                                if (time_diff_2 > time_m) == True:
                                    break
                            break
                        time_4 = dt.now()
                        time_diff_1 = time_4 - time_1
                        if (time_diff_1 > time_m) == True:
                            break
                if stochRSI == 0:
                    value = [{"symbol": symbolCode}]
                    samco.set_streaming_data(value)
                    samco_stream = samco.start_streaming()
                    dict_samco_stream = eval(samco_stream)

                    c = 6
                    time_1 = dt.now()
                    while (c > 5):
                        if float(dict_samco_stream['ltp']) < 0.999 * df_ltp:
                            d = 6
                            time_2 = dt.now()
                            while (d > 5):
                                if float(dict_samco_stream['ltp']) == df_ltp:
                                    PO = samco.place_order(
                                        body={"symbolName": Stock_samco, "exchange": samco.EXCHANGE_NSE,
                                              "transactionType": samco.TRANSACTION_TYPE_BUY,
                                              "orderType": samco.ORDER_TYPE_MARKET, "price": "",
                                              "quantity": qty, "disclosedQuantity": "",
                                              "orderValidity": samco.VALIDITY_DAY,
                                              "productType": samco.PRODUCT_MIS,
                                              "afterMarketOrderFlag": "NO"})
                                    dict_PO = eval(PO)
                                    e = 6
                                    while (e > 5):
                                        Order_status = samco.get_order_status(order_number=dict_PO["orderNumber"])
                                        dict_Order_status = eval(Order_status)
                                        if dict_Order_status["orderStatus"] == "EXECUTED":
                                            PO_1 = samco.place_order(
                                                body={"symbolName": Stock_samco, "exchange": samco.EXCHANGE_NSE,
                                                      "transactionType": samco.TRANSACTION_TYPE_SELL,
                                                      "orderType": samco.ORDER_TYPE_LIMIT, "price": str(1.003 * df_ltp),
                                                      "quantity": qty,
                                                      "disclosedQuantity": "", "orderValidity": samco.VALIDITY_DAY,
                                                      "productType": samco.PRODUCT_MIS, "afterMarketOrderFlag": "NO"})
                                            dict_PO_1 = eval(PO_1)
                                            f = 6
                                            while (f > 5):
                                                Order_status_1 = samco.get_order_status(
                                                    order_number=dict_PO_1["orderNumber"])
                                                dict_Order_status_1 = eval(Order_status_1)
                                                if dict_Order_status_1["orderStatus"] == "EXECUTED":
                                                    break
                                                elif float(dict_samco_stream["ltp"]) < 0.9965 * df_ltp:
                                                    PO_2 = samco.modify_order(order_number=dict_PO_1["orderNumber"],
                                                                              body={
                                                                                  "orderType": samco.ORDER_TYPE_MARKET,
                                                                                  "price": ""})
                                                    g = 6
                                                    while (g > 5):
                                                        Order_status_2 = samco.get_order_status(
                                                            order_number=dict_PO_1["orderNumber"])
                                                        dict_Order_status_2 = eval(Order_status_2)
                                                        if dict_Order_status_2["orderStatus"] == "EXECUTED":
                                                            break
                                                    break
                                                elif dt.now().strftime("%I:%M %p") == "02:00 PM":
                                                    PO_3 = samco.modify_order(order_number=dict_PO_1["orderNumber"],
                                                                              body={
                                                                                  "orderType": samco.ORDER_TYPE_MARKET,
                                                                                  "price": ""})
                                                    h = 6
                                                    while (h > 5):
                                                        Order_status_3 = samco.get_order_status(
                                                            order_number=dict_PO_1["orderNumber"])
                                                        dict_Order_status_3 = eval(Order_status_3)
                                                        if dict_Order_status_3["orderStatus"] == "EXECUTED":
                                                            break
                                                    break
                                            break
                                    break
                                time_3 = dt.now()
                                time_diff_2 = time_3 - time_2
                                if (time_diff_2 > time_m) == True:
                                    break
                            break
                        time_4 = dt.now()
                        time_diff_1 = time_4 - time_1
                        if (time_diff_1 > time_m) == True:
                            break
                if dt.now().strftime("%I:%M %p") == "02:00 PM":
                    break
    if dt.now().strftime("%I:%M %p")=="02:00 PM":
        break


print('program ended')
samco.logout()





