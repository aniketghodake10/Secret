import math
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta as td
from snapi_py_client.snapi_bridge import StocknoteAPIPythonBridge
import requests
import time
import configparser as cfg

#---     VARIABLES  ---
down_target = 0.9975
down_SL = 1.005
up_target = 1.0025
up_SL = 0.995
#---     VARIABLES  ---


#---     FUNCTIONS  ---
def samco_5m_candle_data(tickerr):
    global login
    today = dt.now()
    yesterday = str(today - td(days = 2))[:19]
    headers = {'Accept': 'application/json','x-session-token': login['sessionToken']}

    r = requests.get('https://api.stocknote.com/intraday/candleData', params={'symbolName': tickerr,  'fromDate': yesterday, 'interval': '5'}, headers = headers)

    r = eval(str(r.json()))
    candle = r['intradayCandleData']
    dff = pd.DataFrame(candle)
    dff['open'] = pd.to_numeric(dff['open'], downcast='float')
    dff['low'] = pd.to_numeric(dff['low'], downcast='float')
    dff['high'] = pd.to_numeric(dff['high'], downcast='float')
    dff['close'] = pd.to_numeric(dff['close'], downcast='float')
    dff['volume'] = pd.to_numeric(dff['volume'], downcast='float')
    return dff


def ohlc_5m():
    global Stock_samco1
    a= Stock_samco1

    dff = samco_5m_candle_data(a[0])
    dff.rename(columns={'open': 'open' + a[0], 'high': 'high' + a[0], 'low': 'low' + a[0],
                       'close': 'close' + a[0], 'volume': 'volume' + a[0]}, inplace=True)

    for i in a[1:]:
        df1 = samco_5m_candle_data(i)

        list1 = df1['open'].tolist()
        list2 = df1['high'].tolist()
        list3 = df1['low'].tolist()
        list4 = df1['close'].tolist()
        list5 = df1['volume'].tolist()

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
            Stock_samco1.remove(i)
        finally:
            pass

    return dff


def samco_5m_latest(tickerr,periodd):
    global login
    headers = {'Accept': 'application/json','x-session-token': login['sessionToken']}

    r = requests.get('https://api.stocknote.com/intraday/candleData', params={'symbolName': tickerr,  'fromDate': periodd, 'interval': '5'}, headers = headers)

    r = eval(str(r.json()))
    print(r)
    candle = r['intradayCandleData']
    dff = pd.DataFrame(candle)
    dff['open']=pd.to_numeric(dff['open'],downcast='float')
    dff['low'] = pd.to_numeric(dff['low'], downcast='float')
    dff['high'] = pd.to_numeric(dff['high'], downcast='float')
    dff['close'] = pd.to_numeric(dff['close'], downcast='float')
    dff['volume'] = pd.to_numeric(dff['volume'], downcast='float')
    return dff


def ohlc_5m_latest():
    global df, Stock_samco1
    period_minutes = str(dt.strptime(df['dateTime'].iloc[-1][:19], '%Y-%m-%d %H:%M:%S') + td(minutes=1))[:19]

    dff = samco_5m_latest(Stock_samco1[0], period_minutes)
    dff.rename(columns={'open': 'open' + Stock_samco1[0], 'high': 'high' + Stock_samco1[0], 'low': 'low' + Stock_samco1[0],
                       'close': 'close' + Stock_samco1[0], 'volume': 'volume' + Stock_samco1[0]}, inplace=True)

    for i in Stock_samco1[1:]:
        df1 = samco_5m_latest(i, period_minutes)

        list1 = df1['open'].tolist()
        list2 = df1['high'].tolist()
        list3 = df1['low'].tolist()
        list4 = df1['close'].tolist()
        list5 = df1['volume'].tolist()

        dff = dff.assign(open2=list1)
        dff = dff.assign(high2=list2)
        dff = dff.assign(low2=list3)
        dff = dff.assign(close2=list4)
        dff = dff.assign(volume2=list5)

        dff.rename(columns={'open2': 'open' + i, 'high2': 'high' + i, 'low2': 'low' + i,
                           'close2': 'close' + i, 'volume2': 'volume' + i}, inplace=True)
    return dff

def cond(a,b,c):
    while True:
        condi = dt.now()
        if condi.minute % 5 == a and condi.second >= b and condi.second <= c:
            break


def samco_1m_open(tickerr):
    global df,login
    yesterday = str(dt.strptime(df['dateTime'].iloc[-1][:19], '%Y-%m-%d %H:%M:%S') - td(seconds=30))[:19]
    headers = {'Accept': 'application/json', 'x-session-token': login['sessionToken']}
    r = requests.get('https://api.stocknote.com/intraday/candleData', params={'symbolName': tickerr,  'fromDate': yesterday, 'interval': '1'}, headers = headers)
    r = eval(str(r.json()))
    candle = r['intradayCandleData']
    dff = pd.DataFrame(candle)
    return flsr(dff['open'][0])


def live_price(tickerr):
    global samco
    while True:
        time.sleep(0.4)
        a = samco.get_quote(symbol_name=tickerr, exchange=samco.EXCHANGE_NSE)
        a = eval(a)
        if "lastTradedPrice" in a.keys():
            break
    ltp = a["lastTradedPrice"]
    ltp = ltp.replace(',', '')
    ltp = float('{:.2f}'.format(float(ltp)))
    return ltp


def flsr(a):
    return float('{:.2f}'.format(float(a)))


def bolling_macd():
    global df, Stock_samco1

    aniket = 'none'

    period_rsi = 14
    period_bollinger = 20
    multiplier1 = 2
    multiplier2 = 2

    cond(2,10,15)
    df8 = ohlc_5m_latest()
    df = pd.concat([df,df8],ignore_index=True)
    print(df.iloc[-5:])

    list_cond1 = []
    for stk in Stock_samco1:
        now = dt.now().minute
        if int(float(df['dateTime'].iloc[-1][14:16])) != now - now%5:
            print('samco 5m candle glitch')
            break

        baddy = 1

        df_close = df['close'+ stk]
        df_open = df['open'+ stk]
        df_high = df['high'+ stk]
        df_low = df['low'+ stk]

        print(df_close.iloc[-10:],'\n',df_low.iloc[-10:],'\n',df_high.iloc[-10:],'\n',df_open.iloc[-10:])

        MiddleBand = df_close.rolling(period_bollinger).mean()
        UpperBand = MiddleBand + df_close.rolling(period_bollinger).std() * multiplier1
        LowerBand = MiddleBand - df_close.rolling(period_bollinger).std() * multiplier2
        BandDiffer = (UpperBand - LowerBand) / MiddleBand

        print(MiddleBand.iloc[-10:],'\n',UpperBand.iloc[-10:],'\n',LowerBand.iloc[-10:],'\n',BandDiffer.iloc[-10:])

        for i in range(1, 6):
            if df_low.iloc[-1 * i] < LowerBand.iloc[-1 * i] or df_high.iloc[-1 * i] > UpperBand.iloc[-1 * i] or BandDiffer.iloc[-1 * i] > 0.008:
                baddy = 0
        for i in range(6, 8):
            if BandDiffer.iloc[-1 * i] > 0.008 or df_open.iloc[-1 * i] < LowerBand.iloc[-1 * i] or df_close.iloc[-1 * i] > UpperBand.iloc[-1 * i]:
                baddy = 0

        if baddy == 1:
            list_cond1.append(stk)

    if list_cond1:
        printt_telegram('Wee We Got the 1st list '+str(list_cond1))
        cond(4, 50, 59)

        df_openn = df['open' + list_cond1[0]]
        df_closee = df['close' + list_cond1[0]]

        df_openn_data = [[samco_1m_open(list_cond1[0])]]
        df_openn_columns = ['open'+list_cond1[0]]

        df_closee_data = [[live_price(list_cond1[0])]]
        df_closee_columns = ['close' + list_cond1[0]]

        for stk in list_cond1[1:]:
            df_openn = pd.concat([df_openn,df['open' + stk]],axis=1)
            df_closee = pd.concat([df_closee, df['close' + stk]], axis=1)

            df_openn_data[0].append(samco_1m_open(stk))
            df_openn_columns.append('open'+stk)

            df_closee_data[0].append(live_price(stk))
            df_closee_columns.append('close' + stk)

        df_openn1 = pd.DataFrame(df_openn_data,columns=df_openn_columns)
        df_closee1 = pd.DataFrame(df_closee_data,columns=df_closee_columns)

        df_openn = pd.concat([df_openn,df_openn1],ignore_index=True)
        df_closee = pd.concat([df_closee, df_closee1], ignore_index=True)

        for stk in list_cond1:

            aniket = 'none'

            df_close = df_closee['close' + stk]
            df_open = df_openn['open' + stk]

            delta = df_close.diff(1)
            delta.dropna(inplace=True)
            gain, loss = delta.copy(), delta.copy()
            gain[gain < 0] = 0
            loss[loss > 0] = 0

            _gain = gain.ewm(com=(period_rsi - 1), min_periods=period_rsi).mean()
            _loss = loss.abs().ewm(com=(period_rsi - 1), min_periods=period_rsi).mean()

            RS = _gain / _loss
            rsii = 100 - (100 / (1 + RS))

            MiddleBand = df_close.rolling(period_bollinger).mean()
            UpperBand = MiddleBand + df_close.rolling(period_bollinger).std() * multiplier1
            LowerBand = MiddleBand - df_close.rolling(period_bollinger).std() * multiplier2

            print(MiddleBand.iloc[-10:], '\n', UpperBand.iloc[-10:], '\n', LowerBand.iloc[-10:])

            macd = df_close.ewm(span=12, adjust=False).mean() - df_close.ewm(span=26, adjust=False).mean()
            # signal = macd.ewm(span=9, adjust=False).mean()

            if df_close.iloc[-1] >= 1.0005 * UpperBand.iloc[-1]:
                if df_open.iloc[-1] <= UpperBand.iloc[-1] and df_open.iloc[-1] >= MiddleBand.iloc[-1] and macd.iloc[-1] > \
                        macd.iloc[-2] and macd.iloc[-2] > macd.iloc[-3] and rsii.iloc[-1] < 75:
                    aniket = stk+'up'
                    break

            if df_close.iloc[-1] <= 0.9995 * LowerBand.iloc[-1]:
                if df_open.iloc[-1] >= LowerBand.iloc[-1] and df_open.iloc[-1] <= MiddleBand.iloc[-1] and macd.iloc[-1] < \
                        macd.iloc[-2] and macd.iloc[-2] < macd.iloc[-3] and rsii.iloc[-1] > 25:
                    aniket =stk+'do'
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
    return  dict_Order_status


def square_off(a):
    global samco, Stock_samco, up_target, avg, order_type, dict_PO_2, down_target
    done = 0
    if a == up_target:
        price = live_price(Stock_samco)
        if price >= a * avg:
            while True:
                price = live_price(Stock_samco)
                if price <= (a-0.0005) * avg:
                    PO_1 = samco.place_order(body=PO_body('sell', 'market', 'na', order_type))
                    break
                if price >= (a + 0.001) * avg:
                    while True:
                        price = live_price(Stock_samco)
                        if price <= (a+0.0005) * avg:
                            PO_1 = samco.place_order(body=PO_body('sell', 'market', 'na', order_type))
                            break
                        if price >= (a + 0.0025) * avg:
                            while True:
                                price = live_price(Stock_samco)
                                if price <= (a+0.002) * avg:
                                    PO_1 = samco.place_order(body=PO_body('sell', 'market', 'na', order_type))
                                    break
                                if price >= (a + 0.0045) * avg:
                                    while True:
                                        price = live_price(Stock_samco)
                                        if price <= (a + 0.0035) * avg:
                                            PO_1 = samco.place_order(body=PO_body('sell', 'market', 'na', order_type))
                                            break
                                        if price >= (a + 0.0075) * avg:
                                            while True:
                                                price = live_price(Stock_samco)
                                                if price <= (a+0.0065) * avg:
                                                    PO_1 = samco.place_order(body=PO_body('sell', 'market', 'na', order_type))
                                                    break
                                                if price >= (a + 0.0125) * avg:
                                                    PO_1 = samco.place_order(body=PO_body('sell', 'market', 'na', order_type))
                                                    break
                                            break
                                    break
                            break
                    break
            dict_PO_1 = eval(PO_1)
            print(dict_PO_1)
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
        price = live_price(Stock_samco)
        if price <= a * avg:
            while True:
                price = live_price(Stock_samco)
                if price >= (a + 0.0005) * avg:
                    PO_1 = samco.place_order(body=PO_body('buy', 'market', 'na', order_type))
                    break
                if price <= (a - 0.001) * avg:
                    while True:
                        price = live_price(Stock_samco)
                        if price >= (a - 0.0005) * avg:
                            PO_1 = samco.place_order(body=PO_body('buy', 'market', 'na', order_type))
                            break
                        if price <= (a - 0.0025) * avg:
                            while True:
                                price = live_price(Stock_samco)
                                if price >= (a - 0.002) * avg:
                                    PO_1 = samco.place_order(body=PO_body('buy', 'market', 'na', order_type))
                                    break
                                if price <= (a - 0.0045) * avg:
                                    while True:
                                        price = live_price(Stock_samco)
                                        if price >= (a - 0.0035) * avg:
                                            PO_1 = samco.place_order(body=PO_body('buy', 'market', 'na', order_type))
                                            break
                                        if price <= (a - 0.0075) * avg:
                                            while True:
                                                price = live_price(Stock_samco)
                                                if price >= (a - 0.0065) * avg:
                                                    PO_1 = samco.place_order(body=PO_body('buy', 'market', 'na', order_type))
                                                    break
                                                if price <= (a - 0.0125) * avg:
                                                    PO_1 = samco.place_order(body=PO_body('buy', 'market', 'na', order_type))
                                                    break
                                            break
                                    break
                            break
                    break
            dict_PO_1 = eval(PO_1)
            print(dict_PO_1)
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
csv_2 = pd.read_csv('ind_nifty500list.csv')
Stock_samco1 = csv_2.loc[:, 'Symbol':'Symbol']
Stock_samco1 = Stock_samco1.Symbol
Stock_samco1 = Stock_samco1.tolist()
Stock_samco1.remove('SBIN')
Stock_samco1.insert(0,'SBIN')

amount = 100000
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


cond(1,20,50)
df = ohlc_5m()
print(df)
time.sleep(240)

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

            goooo = 0
            printt_telegram('NEW ITERATION')
            bollz = bolling_macd()
            print(bollz)

            if bollz != "none":
                printt_telegram('Got the Stock ' + bollz)
                Stock_samco = bollz[:-2]
                price = live_price(Stock_samco)
                qty = math.ceil(amount / (1.01 * price))
                qty = str(qty)
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
                        PO_2 = samco.place_order(body=PO_body('sell', 'slm', str(0.05 * math.ceil((up_SL * avg) / 0.05)),order_type))
                        dict_PO_2 = eval(PO_2)
                        print(dict_PO_2)
                        while True:
                            price = live_price(Stock_samco)
                            if price < 0.05 * math.ceil((up_SL * avg) / 0.05):
                                if order_status_dict(dict_PO_2)["orderStatus"] == "EXECUTED":
                                    printt_telegram('SL hit SELL EXECUTED   avgExecutionPrice is ' +order_status_dict(dict_PO_2)["orderDetails"]["avgExecutionPrice"])
                                    break
                            if time_exceed(14, 50, 0, 0):
                                PO_1 = samco.place_order(body=PO_body('sell', 'limit', str(0.05 * math.ceil((up_target * avg) / 0.05)), order_type))
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
                        PO_2 = samco.place_order(body=PO_body('buy', 'slm', str(0.05 * math.ceil((down_SL * avg) / 0.05)),order_type))
                        dict_PO_2 = eval(PO_2)
                        print(dict_PO_2)
                        while True:
                            price = live_price(Stock_samco)
                            if price > 0.05 * math.ceil((down_SL * avg) / 0.05):
                                if order_status_dict(dict_PO_2)["orderStatus"] == "EXECUTED":
                                    printt_telegram(' SL hit BUY EXECUTED   avgExecutionPrice is ' +order_status_dict(dict_PO_2)["orderDetails"]["avgExecutionPrice"])
                                    break
                            if time_exceed(14, 50, 0, 0):
                                PO_1 = samco.place_order(body=PO_body('buy', 'limit', str(0.05 * math.ceil((down_target * avg) / 0.05)), order_type))
                                print(PO_1)
                                printt_telegram('BUY order may be Auto square off as time is two fifty ')
                                break
                            if square_off(down_target) == 1:
                                break
                        break
print('program ended')
samco.logout()