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
# print('Login Details\n', login)
login = eval(login)
samco.set_session_token(sessionToken=login['sessionToken'])

csv_2=pd.read_csv('ind_nifty500list.csv')
Stock_samco1=csv_2.loc[:, 'Symbol':'Symbol']
Stock_samco1=Stock_samco1.Symbol
Stock_samco1=Stock_samco1.tolist()
Stock_samco1.remove('BAJFINANCE')
Stock_samco1.insert(0,'BAJFINANCE')
Stock_samco1.remove('DIXON')
Stock_samco1.remove('ASTRAL')

for stk in Stock_samco1:
    df_1m_samco = samco.get_intraday_candle_data(symbol_name=stk, exchange=samco.EXCHANGE_NSE,
                                                 from_date='2021-03-22 08:00:00')
    df_1m_samco = eval(df_1m_samco)
    data = df_1m_samco["intradayCandleData"]
    df_1m_samco = pd.DataFrame(data)

    df_1m_samco['open'] = pd.to_numeric(df_1m_samco['open'], downcast='float')
    df_1m_samco['low'] = pd.to_numeric(df_1m_samco['low'], downcast='float')
    df_1m_samco['high'] = pd.to_numeric(df_1m_samco['high'], downcast='float')
    df_1m_samco['close'] = pd.to_numeric(df_1m_samco['close'], downcast='float')
    df_1m_samco['volume'] = pd.to_numeric(df_1m_samco['volume'], downcast='float')

    df_1m_samco.to_csv(stk + "_1m_samco.csv")
    print(stk)


