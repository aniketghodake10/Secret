import math
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta as td
from snapi_py_client.snapi_bridge import StocknoteAPIPythonBridge
import requests
import time
import configparser as cfg
import yfinance as yf
from threading import *

#---     VARIABLES  ---
down_target = 0.9982
down_SL = 1.0061
up_target = 1.0018
up_SL = 0.9939
#---     VARIABLES  ---


#---     FUNCTIONS  ---
def cond(a,b,c):
    while True:
        condi = dt.now()
        if condi.minute % 5 == a and condi.second >= b and condi.second <= c:
            break


def live_price(tickerr):
    global samco
    while True:
        time.sleep(0.35)
        a = samco.get_quote(symbol_name=tickerr, exchange=samco.EXCHANGE_NSE)
        a = eval(a)
        if "lastTradedPrice" in a.keys():
            break
    ltp = a["lastTradedPrice"]
    ltp = ltp.replace(',', '')
    ltp = flsr(ltp)
    return ltp


def flsr(a):
    return float('{:.5f}'.format(float(a)))


def ohlc_5m():
    global stocklist
    a = stocklist

    conf = 0
    time_m_sec = 10
    time_1 = dt.now()
    while True:
        dff = yf.download(tickers=a[0], period='2d', interval='5m')
        ajj = dt.now().minute
        if ajj % 5 != 0:
            if float(str(dff.index[-2])[14:16]) == ajj - ajj % 5:
                if flsr((dff.index[-2] - dff.index[-3]).seconds / 60) == 5:
                    conf = 1
                    break
            # if float(str(dff.index[-1])[14:16]) == ajj - ajj % 5:
            #     if flsr((dff.index[-1] - dff.index[-2]).seconds / 60) == 5:
            #         conf = 2
            #         break
        if time_exceed(time_1.hour, time_1.minute, time_1.second + time_m_sec, time_1.microsecond):
            print(dff)
            break
    if conf == 1:
        dff = dff[:-2]
    # if conf == 2:
    #     dff = dff[:-1]
    dff.rename(columns={'Open': 'open' + a[0], 'High': 'high' + a[0], 'Low': 'low' + a[0],
                       'Close': 'close' + a[0], 'Volume': 'volume' + a[0]}, inplace=True)

    for i in a[1:]:
        if conf == 0:
            print('yf 5m candle glitch')
            break

        confs = 0
        time_m_sec = 2
        time_1 = dt.now()
        while True:
            df1 = yf.download(tickers=i, period='2d', interval='5m')
            ajj = dt.now().minute
            if ajj % 5 != 0:
                if float(str(df1.index[-2])[14:16]) == ajj - ajj % 5:
                    if flsr((df1.index[-2] - df1.index[-3]).seconds/60) == 5:
                        confs = 1
                        break
                # if float(str(df1.index[-1])[14:16]) == ajj - ajj % 5:
                #     if flsr((df1.index[-1] - df1.index[-2]).seconds / 60) == 5:
                #         confs = 2
                #         break
            if time_exceed(time_1.hour, time_1.minute, time_1.second + time_m_sec, time_1.microsecond):
                stocklist.remove(i)
                break

        if confs == 0:
            print('yf_1 5m candle glitch')
            continue

        if confs == 1:
            df1 = df1[:-2]
        # if confs == 2:
        #     df1 = df1[:-1]

        list1 = df1['Open'].tolist()
        list2 = df1['High'].tolist()
        list3 = df1['Low'].tolist()
        list4 = df1['Close'].tolist()
        list5 = df1['Volume'].tolist()

        try:
            dff = dff.assign(open2=list1)
            dff = dff.assign(high2=list2)
            dff = dff.assign(low2=list3)
            dff = dff.assign(close2=list4)
            dff = dff.assign(volume2=list5)

            dff.rename(columns={'open2': 'open' + i, 'high2': 'high' + i, 'low2': 'low' + i,
                                'close2': 'close' + i, 'volume2': 'volume' + i}, inplace=True)
        except Exception as e:
            print(e)
            stocklist.remove(i)
        finally:
            pass

    return dff,conf


def confirm_100(stk, close):
    global aniket
    time_1 = dt.now()
    while aniket == 'none':
        if time_exceed(time_1.hour, time_1.minute + 4, time_1.second, time_1.microsecond):
            break
        if live_price(stk) >= flsr(1.002 * close):
            while aniket == 'none':
                if time_exceed(time_1.hour, time_1.minute + 4, time_1.second, time_1.microsecond):
                    break
                if live_price(stk) <= flsr(0.9993 * close):
                    aniket = stk + 'do'
            break


def confirm_0(stk, close):
    global aniket
    time_1 = dt.now()
    while aniket == 'none':
        if time_exceed(time_1.hour, time_1.minute + 4, time_1.second, time_1.microsecond):
            break
        if live_price(stk) <= flsr(0.998 * close):
            while aniket == 'none':
                if time_exceed(time_1.hour, time_1.minute + 4, time_1.second, time_1.microsecond):
                    break
                if live_price(stk) >= flsr(1.0007 * close):
                    aniket = stk + 'up'
            break


def bolling_macd():
    global stocklist,aniket

    aniket = 'none'

    period_rsi = 14
    period_bollinger = 20
    multiplier1 = 2
    multiplier2 = 2

    cond(0,20,30)
    time_1 = dt.now()

    df,conff = ohlc_5m()

    dict_cond1_100 = {}
    dict_cond1_0 = {}
    for stk in stocklist:
        if conff == 0:
            print('yf 5m candle glitch')
            break

        # baddy = 1

        df_close = df['close' + stk]
        df_open = df['open' + stk]
        df_high = df['high' + stk]
        df_low = df['low' + stk]

        delta = df_close.diff(1)
        delta.dropna(inplace=True)
        gain, loss = delta.copy(), delta.copy()
        gain[gain < 0] = 0
        loss[loss > 0] = 0

        _gain = gain.ewm(com=(period_rsi - 1), min_periods=period_rsi).mean()
        _loss = loss.abs().ewm(com=(period_rsi - 1), min_periods=period_rsi).mean()

        RS = _gain / _loss
        rsii = 100 - (100 / (1 + RS))

        stochrsii = (rsii - rsii.rolling(period_rsi).min()) / (rsii.rolling(period_rsi).max() - rsii.rolling(period_rsi).min())
        stochrsii_K = stochrsii.rolling(3).mean()

        MiddleBand = df_close.rolling(period_bollinger).mean()
        UpperBand = MiddleBand + df_close.rolling(period_bollinger).std() * multiplier1
        LowerBand = MiddleBand - df_close.rolling(period_bollinger).std() * multiplier2

        if flsr(100 * stochrsii_K[-1]) == 100 and df_close.iloc[-1] > flsr(1.0025 * UpperBand.iloc[-1]) and df_low.iloc[
            -1] >= flsr(0.999 * df_open.iloc[-1]):
            dict_cond1_100[stk] = flsr(df_close.iloc[-1])
        if flsr(100 * stochrsii_K[-1]) == 0 and df_close.iloc[-1] < flsr(0.9975 * LowerBand.iloc[-1]) and df_high.iloc[
            -1] <= flsr(1.001 * df_open.iloc[-1]):
            dict_cond1_0[stk] = flsr(df_close.iloc[-1])

    if dict_cond1_100 or dict_cond1_0:
        thread_dict = {}

        for xc in list(dict_cond1_100.keys()):
            thread_dict[xc] = Thread(target=confirm_100, args=(xc,dict_cond1_100[xc]))
            thread_dict[xc].start()
        for xc in list(dict_cond1_0.keys()):
            thread_dict[xc] = Thread(target=confirm_0, args=(xc,dict_cond1_0[xc]))
            thread_dict[xc].start()

        while True:
            if aniket != 'none':
                break
            if time_exceed(time_1.hour, time_1.minute + 4, time_1.second, time_1.microsecond):
                break

    return aniket


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
    global samco, qty, Stock_samco
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


def printt_telegram(a):
    print(a)
    telegram_trade_messeges(string_remove_char(a))


def order_status_dict(a):
    global samco
    Order_status = samco.get_order_status(order_number=a["orderNumber"])
    dict_Order_status = eval(Order_status)
    print(dict_Order_status)
    return  dict_Order_status


def square_off(a):
    global samco, Stock_samco, up_target, avg, order_type, dict_PO_2, down_target
    done = 0
    rti = 'notok'
    if a == up_target:
        if live_price(Stock_samco) >= flsr(a * avg):
            while True:
                if live_price(Stock_samco) >= flsr(a * avg):
                    rti = 'ok'
                    a = flsr(a + 0.0005)
                if (a == flsr(up_target + 0.0005) or a == up_target) and rti == 'ok':
                    if live_price(Stock_samco) <= flsr(1.0015 * avg):
                        PO_1 = samco.place_order(body=PO_body('sell', 'market', 'na', order_type))
                        dict_PO_1 = eval(PO_1)
                        print(dict_PO_1)
                        break
                if a != flsr(up_target + 0.0005) and a != up_target and rti == 'ok':
                    if live_price(Stock_samco) <= flsr(flsr((a - 2 * 0.0005)) * avg):
                        PO_1 = samco.place_order(body=PO_body('sell', 'market', 'na', order_type))
                        dict_PO_1 = eval(PO_1)
                        print(dict_PO_1)
                        break

            while True:
                if order_status_dict(dict_PO_1)["orderStatus"] == "EXECUTED":
                    printt_telegram('SELL EXECUTED   avgExecutionPrice is ' + order_status_dict(dict_PO_1)["orderDetails"]["avgExecutionPrice"])
                    PO_cancel = samco.cancel_order(order_number=dict_PO_2["orderNumber"])
                    dict_PO_cancel = eval(PO_cancel)
                    print(dict_PO_cancel)
                    while True:
                        if dict_PO_cancel["statusMessage"] == "Order cancelled successfully":
                            printt_telegram('SL order cancelled as target hit')
                            done=1
                            break
                    break

    if a == down_target:
        if live_price(Stock_samco) <= flsr(a * avg):
            while True:
                if live_price(Stock_samco) <= flsr(a * avg):
                    rti = 'ok'
                    a = flsr(a - 0.0005)
                if (a == flsr(down_target - 0.0005) or a == down_target) and rti == 'ok':
                    if live_price(Stock_samco) >= flsr(0.9985 * avg):
                        PO_1 = samco.place_order(body=PO_body('buy', 'market', 'na', order_type))
                        dict_PO_1 = eval(PO_1)
                        print(dict_PO_1)
                        break
                if a != flsr(up_target - 0.0005) and a != down_target and rti == 'ok':
                    if live_price(Stock_samco) >= flsr(flsr((a + 2 * 0.0005)) * avg):
                        PO_1 = samco.place_order(body=PO_body('buy', 'market', 'na', order_type))
                        dict_PO_1 = eval(PO_1)
                        print(dict_PO_1)
                        break

            while True:
                if order_status_dict(dict_PO_1)["orderStatus"] == "EXECUTED":
                    printt_telegram('BUY EXECUTED   avgExecutionPrice is ' + order_status_dict(dict_PO_1)["orderDetails"]["avgExecutionPrice"])
                    PO_cancel = samco.cancel_order(order_number=dict_PO_2["orderNumber"])
                    dict_PO_cancel = eval(PO_cancel)
                    print(dict_PO_cancel)
                    while True:
                        if dict_PO_cancel["statusMessage"] == "Order cancelled successfully":
                            printt_telegram('SL order cancelled as target hit')
                            done = 1
                            break
                    break
    return done


def read_token_from_config_file(config, key):
    parser = cfg.ConfigParser()
    parser.read(config)
    return parser.get('creds', key)
#---     FUNCTIONS  ---


#---     INPUTS  ---
csv_2=pd.read_csv('ind_nifty500list.csv')
Stock_samco1=csv_2.loc[:, 'Symbol':'Symbol']
Stock_samco1=Stock_samco1.Symbol
Stock_samco1=Stock_samco1.tolist()
Stock_samco1.remove('BAJFINANCE')
Stock_samco1.insert(0,'BAJFINANCE')


# amount = 100000
order_type = 'mis'
startt_time = [9,30]
endd_time = [14,40]

samco = StocknoteAPIPythonBridge()
userId, password, yob = read_token_from_config_file("login_data.cfg", "userId"), read_token_from_config_file(
        "login_data.cfg", "password"), read_token_from_config_file("login_data.cfg", "yob")
login = samco.login(body={"userId": userId, 'password': password, 'yob': yob})
print('Login Details\n', login)
login = eval(login)
samco.set_session_token(sessionToken=login['sessionToken'])

startt_year = dt.now().year
startt_month = dt.now().month
startt_day = dt.now().day
printt_telegram('Plz Restart the telegram Bot')
#---     INPUTS  ---

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

            stocklist = []
            for i in Stock_samco1:
                j = i + '.NS'
                stocklist.append(j)

            goooo = 0
            printt_telegram('NEW ITERATION')
            aniket = 'none'
            bollz = bolling_macd()
            print(bollz)

            if bollz != "none":
                printt_telegram('Got the Stock ' + bollz)
                Stock_samco = bollz[:-2]
                # price = live_price(Stock_samco)
                # qty = math.ceil(amount / (1.01 * price))
                # qty = str(qty)
                qty = '1'
                if bollz[-2:]=='up':
                    goooo = 1
                if bollz[-2:]=='do':
                    goooo = 2

            if goooo == 1:
                PO = samco.place_order(body=PO_body('buy', 'market', 'na', order_type))
                dict_PO = eval(PO)
                print(dict_PO)
                avg = float('{:.2f}'.format(float(order_status_dict(dict_PO)["orderDetails"]["avgExecutionPrice"])))
                while True:
                    if order_status_dict(dict_PO)["orderStatus"] == "EXECUTED":
                        printt_telegram('BUY EXECUTED   avgExecutionPrice is ' + str(avg))
                        PO_2 = samco.place_order(body=PO_body('sell', 'slm', str(flsr(0.05 * math.ceil((up_SL * avg) / 0.05))),order_type))
                        dict_PO_2 = eval(PO_2)
                        print(dict_PO_2)
                        while True:
                            price = live_price(Stock_samco)
                            if price < flsr(0.05 * math.ceil((up_SL * avg) / 0.05)):
                                if order_status_dict(dict_PO_2)["orderStatus"] == "EXECUTED":
                                    printt_telegram('SL hit SELL EXECUTED   avgExecutionPrice is ' +order_status_dict(dict_PO_2)["orderDetails"]["avgExecutionPrice"])
                                    break
                            if time_exceed(14, 50, 0, 0):
                                PO_1 = samco.place_order(body=PO_body('sell', 'limit', str(flsr(0.05 * math.ceil((up_target * avg) / 0.05))), order_type))
                                print(PO_1)
                                printt_telegram('SELL order may be Auto square off as time is two fifty ')
                                break
                            if square_off(up_target) == 1:
                                break
                        break

            if goooo == 2:
                PO = samco.place_order(body=PO_body('sell', 'market', 'na', order_type))
                dict_PO = eval(PO)
                print(dict_PO)
                avg = float('{:.2f}'.format(float(order_status_dict(dict_PO)["orderDetails"]["avgExecutionPrice"])))
                while True:
                    if order_status_dict(dict_PO)["orderStatus"] == "EXECUTED":
                        printt_telegram('SELL EXECUTED   avgExecutionPrice is ' +order_status_dict(dict_PO)["orderDetails"]["avgExecutionPrice"])
                        PO_2 = samco.place_order(body=PO_body('buy', 'slm', str(flsr(0.05 * math.ceil((down_SL * avg) / 0.05))),order_type))
                        dict_PO_2 = eval(PO_2)
                        print(dict_PO_2)
                        while True:
                            price = live_price(Stock_samco)
                            if price > flsr(0.05 * math.ceil((down_SL * avg) / 0.05)):
                                if order_status_dict(dict_PO_2)["orderStatus"] == "EXECUTED":
                                    printt_telegram(' SL hit BUY EXECUTED   avgExecutionPrice is ' +order_status_dict(dict_PO_2)["orderDetails"]["avgExecutionPrice"])
                                    break
                            if time_exceed(14, 50, 0, 0):
                                PO_1 = samco.place_order(body=PO_body('buy', 'limit', str(flsr(0.05 * math.ceil((down_target * avg) / 0.05))), order_type))
                                print(PO_1)
                                printt_telegram('BUY order may be Auto square off as time is two fifty ')
                                break
                            if square_off(down_target) == 1:
                                break
                        break
print('program ended')
samco.logout()