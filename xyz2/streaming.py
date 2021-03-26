import json
import math
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta as td
from snapi_py_client.snapi_bridge import StocknoteAPIPythonBridge
import requests
import time
import configparser as cfg
import yfinance as yf
from matplotlib import pyplot as plt
import websocket
from threading import *


def read_token_from_config_file(config, key):
    parser = cfg.ConfigParser()
    parser.read(config)
    return parser.get('creds', key)


def flsr(a):
    return float('{:.5f}'.format(float(a)))


samco = StocknoteAPIPythonBridge()
userId, password, yob = read_token_from_config_file("login_data.cfg", "userId"), read_token_from_config_file(
    "login_data.cfg", "password"), read_token_from_config_file("login_data.cfg", "yob")


login = samco.login(body={"userId": userId, 'password': password, 'yob': yob})
print('Login Details\n', login)
login = eval(login)
samco.set_session_token(sessionToken=login['sessionToken'])

def on_message(ws, msg):
    global ohlc_dict,candle_high_low,Symbol_list
    a  = eval(msg)
    qwerty = flsr(a['response']['data']['ltp'])
    if candle_high_low == 0:
        ohlc_dict['open_close'][a['response']['data']['sym']] = qwerty
        if not ohlc_dict['low']:
            ohlc_dict['low'][a['response']['data']['sym']] = qwerty
        if not ohlc_dict['high']:
            ohlc_dict['high'][a['response']['data']['sym']] = qwerty
        if qwerty < ohlc_dict['low'][a['response']['data']['sym']] and ohlc_dict['low']:
            ohlc_dict['low'][a['response']['data']['sym']] = qwerty
        if qwerty > ohlc_dict['high'][a['response']['data']['sym']] and ohlc_dict['high']:
            ohlc_dict['high'][a['response']['data']['sym']] = qwerty
    else:
        ohlc_dict['open_close'][a['response']['data']['sym']] = qwerty
        ohlc_dict['low'][a['response']['data']['sym']] = qwerty
        ohlc_dict['high'][a['response']['data']['sym']] = qwerty
        if not ohlc_dict['low']:
            ohlc_dict['low'][a['response']['data']['sym']] = qwerty
        if not ohlc_dict['high']:
            ohlc_dict['high'][a['response']['data']['sym']] = qwerty
        if qwerty < ohlc_dict['low'][a['response']['data']['sym']] and ohlc_dict['low']:
            ohlc_dict['low'][a['response']['data']['sym']] = qwerty
        if qwerty > ohlc_dict['high'][a['response']['data']['sym']] and ohlc_dict['high']:
            ohlc_dict['high'][a['response']['data']['sym']] = qwerty
        loll = 0
        if all(ohlc_dict['open_close'][a['response']['data'][i]] == ohlc_dict['low'][a['response']['data'][i]] ==
        ohlc_dict['high'][a['response']['data'][i]] for i in Symbol_list):
            loll = 1
        if loll == 1:
            candle_high_low = 0







def on_error(ws, error):
    print(error)


def on_close(ws):
    print("Connection Closed")


def on_open(ws):
    print("Sending json")
    data = '{"request":{"streaming_type":"quote", "data":{"symbols":[{"symbol":"3045_NSE"}]}, "request_type":"subscribe", "response_format":"json"}}'
    ws.send(data)
    ws.send("\n")




def baddy_zinda():
    global login
    headers = {'x-session-token': login['sessionToken']}

    websocket.enableTrace(True)

    ws = websocket.WebSocketApp("wss://stream.stocknote.com", on_open=on_open, on_message=on_message, on_error=on_error,
                                on_close=on_close, header=headers)

    ws.run_forever()

ltp = 1000
t1 = Thread(target=baddy_zinda)
t1.start()

while True:
    print(ltp)
    if ltp < 358:
        print('baddy')
        break

csv_1=pd.read_csv('ScripMaster.csv')
u=csv_1.loc[:, 'symbolCode':'symbolCode']
v=csv_1.loc[:, 'tradingSymbol':'tradingSymbol']
w=v.join(u)
x=dict(zip(w.tradingSymbol,w.symbolCode))

Symbol_list = []
candle_high_low = 0
ohlc_dict ={'open_close':{},'low':{},'high':{}}