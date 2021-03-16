import math
# import pandas_datareader as web
# import numpy as np
import pandas as pd
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

def bollinger_macd(stocklist, period: int = 14):
    conf = 0
    period_bollinger = 20
    multiplier = 2

    st = str(stocklist)
    st = st[1:]
    st = st[:-1]
    st = st.replace('\'', '')
    st = st.replace(',', '')

    # time_m_sec = 10
    # time_1 = dt.now()
    # while True:
    #     df_5 = yf.download(tickers=st, period='2d', interval='5m')
    #     a = dt.now().minute
    #     if a % 5 != 0:
    #         if float(str(df_5.index[-1])[14:16]) == a and float(str(df_5.index[-2])[14:16]) == a - a % 5 and float(
    #                 str(df_5.index[-3])[14:16]) == a - a % 5 - 5:
    #             conf = 1
    #             break
    #     if a % 5 == 0:
    #         if float(str(df_5.index[-1])[14:16]) == a and float(str(df_5.index[-2])[14:16]) == a - 5 and float(
    #                 str(df_5.index[-3])[14:16]) == a - 10:
    #             conf = 1
    #             break
    #     if time_exceed(time_1.hour, time_1.minute, time_1.second + time_m_sec, time_1.microsecond):
    #         break
    df_5 = yf.download(tickers=st, period='2d', interval='5m')
    conf=1
    if conf == 1:
        conf = 0
        baddy = 0
        stock = 'none'
        for i in stocklist:
            # df_6 = df_5[:-1]
            df_6 = df_5
            df_close = df_6['Close'][i]
            df_open = df_6['Open'][i]
            df_high = df_6['High'][i]
            df_low = df_6['Low'][i]
            delta = df_close.diff(1)
            delta.dropna(inplace=True)
            gain, loss = delta.copy(), delta.copy()
            gain[gain < 0] = 0
            loss[loss > 0] = 0

            _gain = gain.ewm(com=(period - 1), min_periods=period).mean()
            _loss = loss.abs().ewm(com=(period - 1), min_periods=period).mean()

            RS = _gain / _loss
            rsii = 100 - (100 / (1 + RS))

            MiddleBand = df_close.rolling(period_bollinger).mean()
            UpperBand = MiddleBand + df_close.rolling(period).std() * multiplier
            LowerBand = MiddleBand - df_close.rolling(period).std() * multiplier

            macd = df_close.ewm(span=26, adjust=False).mean() - df_close.ewm(span=12, adjust=False).mean()
            signal = macd.ewm(span=9, adjust=False).mean()

            print('.              .')

            if df_close[-1] >= 1.001 * UpperBand[-1]:
                if df_open[-1] <= UpperBand[-1] and df_open[-1] >= MiddleBand[-1] and macd[-1] > 0 and macd[-1] > \
                        signal[-1] and rsii[-1] > 56.5 and rsii[-1] < 65:
                    baddy = 1
                    for i in range(2, 9):
                        if df_low[-1 * i] < LowerBand[-1 * i] or df_high[-1 * i] > UpperBand[-1 * i]:
                            baddy = 0
                            break
                    for i in range(2, 6):
                        if df_close[-1 * i] >= MiddleBand[-1 * i]:
                            baddy = 0
                            break
            if df_close[-1] <= 0.999 * LowerBand[-1]:
                if df_open[-1] >= LowerBand[-1] and df_open[-1] <= MiddleBand[-1] and macd[-1] < 0 and macd[-1] < \
                        signal[-1] and rsii[-1] > 35 and rsii[-1] < 43:
                    baddy = 1
                    for i in range(2, 9):
                        if df_low[-1 * i] < LowerBand[-1 * i] or df_high[-1 * i] > UpperBand[-1 * i]:
                            baddy = 0
                            break
                    for i in range(2, 6):
                        if df_close[-1 * i] <= MiddleBand[-1 * i]:
                            baddy = 0
                            break
            if baddy == 1:
                stock = i
                break

        return stock
    else:
        print('yfinance failed')
        return None

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
print(bollinger_macd(Stock1))