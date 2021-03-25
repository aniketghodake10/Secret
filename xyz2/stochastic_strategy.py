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

def bolling_macd(yeyy,sl,trgett,stepp,sqstepp,mintarget):
    global samco,df_main,Stock_samco1,stocklist,pandl,dattt,pandlP,marginn,listtttttttt_pl

    period_rsi = 14
    period_bollinger = 20
    multiplier1 = 2
    multiplier2 = 2

    df = df_main.iloc[:-1 * yeyy+1]
    df_rada  = df_main.iloc[:-1 * yeyy+2]

    outputt,profitt,losss,neutral = [], [],[],[]
    for stk in stocklist:
        baddy = 0
        gogogo = 'start'
        df_close = df['Close'][stk]
        df_open = df['Open'][stk]
        df_high = df['High'][stk]
        df_low = df['Low'][stk]

        # if df_close.iloc[-1] < 1000:
        #     continue

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

        df_rada_open = df_rada['Open'][stk]
        df_rada_high = df_rada['High'][stk]
        df_rada_low = df_rada['Low'][stk]

        if flsr(100*stochrsii_K[-1]) == 100 and df_close.iloc[-1] > flsr(1.0025*UpperBand.iloc[-1]):
            if df_high.iloc[-1] >= flsr(1.002*df_close.iloc[-1]) and df_low.iloc[-1] >= flsr(0.9975 * df_open.iloc[-1]):
                baddy = 2
            if df_rada_high.iloc[-1] >= flsr(1.002 * df_rada_open.iloc[-1]) and df_rada_low.iloc[-1] <= flsr(0.9993 * df_close.iloc[-1]) \
                    and df_low.iloc[-1] >= flsr(0.9975 * df_open.iloc[-1]):
                baddy = 2
                gogogo = 'go1'
            # for i in range(1, 6):
            #     if df_close.iloc[-1*i] < df_close.iloc[-1*i-1]:
            #         baddy = 0
            #         break
        if flsr(100*stochrsii_K[-1]) == 0 and df_close.iloc[-1] < flsr(0.9975*LowerBand.iloc[-1]):
            if df_low.iloc[-1] <= flsr(0.998*df_close.iloc[-1]) and df_high.iloc[-1] <= flsr(1.0025 * df_open.iloc[-1]):
                baddy = 1
            if df_rada_low.iloc[-1] <= flsr(0.998 * df_rada_open.iloc[-1]) and df_rada_high.iloc[-1] >= flsr(1.0007 * df_close.iloc[-1]) \
                    and df_high.iloc[-1] <= flsr(1.0025 * df_open.iloc[-1]):
                baddy = 1
                gogogo = 'go1'
            # for i in range(1, 6):
            #     if df_close.iloc[-1*i] > df_close.iloc[-1*i-1]:
            #         baddy = 0
            #         break

        aniket = 'none'
        if baddy == 1:
            sl1 = flsr(2-sl)
            trr = flsr(trgett)
            godatt = df.index[-1] + td(minutes=5)
            while True:
                try:
                    df_1m_samco = samco.get_intraday_candle_data(symbol_name=stk[:-3], exchange=samco.EXCHANGE_NSE,
                                                                 from_date=str(godatt)[:19],
                                                                 to_date=str(godatt)[:10] + ' 15:29:00')
                    df_1m_samco = eval(df_1m_samco)
                    break
                except Exception as e:
                    print(e)
            data = df_1m_samco["intradayCandleData"]
            df_1m_samco = pd.DataFrame(data)

            df_1m_samco['open'] = pd.to_numeric(df_1m_samco['open'], downcast='float')
            df_1m_samco['low'] = pd.to_numeric(df_1m_samco['low'], downcast='float')
            df_1m_samco['high'] = pd.to_numeric(df_1m_samco['high'], downcast='float')
            df_1m_samco['close'] = pd.to_numeric(df_1m_samco['close'], downcast='float')
            df_1m_samco['volume'] = pd.to_numeric(df_1m_samco['volume'], downcast='float')

            for jkl in [0,1,2,3,4]:
                if gogogo != 'go1':
                    break
                if df_1m_samco['low'].iloc[jkl] <= flsr(0.998 * df_1m_samco['open'].iloc[0]):
                    for tkl in range(jkl+1,5):
                        if df_1m_samco['high'].iloc[tkl] >= flsr(1.0007 * df_close.iloc[-1]):
                            gogogo = 'go'
                            break
                    break
            if gogogo != 'go1':
                for tkl in [0, 1, 2, 3, 4]:
                    if df_1m_samco['high'].iloc[tkl] >= flsr(1.0007 * df_close.iloc[-1]):
                        gogogo = 'po'
                        break
            if  gogogo == 'go' or gogogo == 'po':
                if df_1m_samco['high'].iloc[tkl] >= flsr(1.0007 * df_close.iloc[-1]):
                    df_close_rada = flsr(1.0007 * df_close.iloc[-1])
                    for i in range(len(df_1m_samco) - tkl, 0, -1):
                        if aniket[0] == 'p':
                            if trr == flsr(trgett + stepp):
                                if df_1m_samco['low'].iloc[-1 * i] <= flsr(flsr(mintarget) * df_close_rada):
                                    aniket = 'p' + str(flsr(mintarget)) + stk + 'up'
                                    dattt = df_1m_samco['dateTime'].iloc[-1 * i][:19]
                                    dattt = dt.strptime(dattt, '%Y-%m-%d %H:%M:%S')
                                    break
                            if trr != flsr(trgett + stepp):
                                if df_1m_samco['low'].iloc[-1 * i] <= flsr(flsr(trr - flsr(stepp + sqstepp)) * df_close_rada):
                                    aniket = 'p' + str(flsr(trr - flsr(stepp + sqstepp))) + stk + 'up'
                                    dattt = df_1m_samco['dateTime'].iloc[-1 * i][:19]
                                    dattt = dt.strptime(dattt, '%Y-%m-%d %H:%M:%S')
                                    break
                        if df_1m_samco['high'].iloc[-1 * i] >= flsr((trr) * df_close_rada):
                            aniket = 'p' + str(trr) + stk + 'up'
                            dattt = df_1m_samco['dateTime'].iloc[-1 * i][:19]
                            dattt = dt.strptime(dattt, '%Y-%m-%d %H:%M:%S')
                            tl = flsr(trr)
                            for k in range(1, 25):
                                k = flsr(k * stepp)
                                trrk = flsr(trr + k)
                                if df_1m_samco['high'].iloc[-1 * i] >= flsr((trrk) * df_close_rada):
                                    aniket = 'p' + str(trrk) + stk + 'up'
                                    dattt = df_1m_samco['dateTime'].iloc[-1 * i][:19]
                                    dattt = dt.strptime(dattt, '%Y-%m-%d %H:%M:%S')
                                    tl = flsr(trrk)
                            if tl == trgett:
                                if df_1m_samco['close'].iloc[-1 * i] <= flsr(flsr(mintarget) * df_close_rada):
                                    aniket = 'p' + str(flsr(mintarget)) + stk + 'up'
                                    dattt = df_1m_samco['dateTime'].iloc[-1 * i][:19]
                                    dattt = dt.strptime(dattt, '%Y-%m-%d %H:%M:%S')
                                    break
                            if tl != trgett:
                                if df_1m_samco['close'].iloc[-1 * i] <= flsr(flsr(tl - sqstepp) * df_close_rada):
                                    aniket = 'p' + str(flsr(tl - sqstepp)) + stk + 'up'
                                    dattt = df_1m_samco['dateTime'].iloc[-1 * i][:19]
                                    dattt = dt.strptime(dattt, '%Y-%m-%d %H:%M:%S')
                                    break
                            trr = flsr(tl + stepp)

                        if aniket[0] != 'p':
                            if df_1m_samco['low'].iloc[-1 * i] <= flsr(sl1 * df_close_rada):
                                aniket = 'loss' + stk + 'up'
                                dattt = df_1m_samco['dateTime'].iloc[-1 * i][:19]
                                dattt = dt.strptime(dattt, '%Y-%m-%d %H:%M:%S')
                                break
                            else:
                                aniket = 'neut' + stk + 'up'
                                dattt = df_1m_samco['dateTime'].iloc[-1 * i][:19]
                                dattt = dt.strptime(dattt, '%Y-%m-%d %H:%M:%S')

        if baddy == 2:
            trgett1 = flsr(2 - trgett)
            mintarget1 = flsr(2 - mintarget)
            trr = flsr(trgett1)
            godatt = df.index[-1] + td(minutes=5)
            while True:
                try:
                    df_1m_samco = samco.get_intraday_candle_data(symbol_name=stk[:-3], exchange=samco.EXCHANGE_NSE,
                                                         from_date=str(godatt)[:19],
                                                         to_date=str(godatt)[:10] + ' 15:29:00')
                    df_1m_samco = eval(df_1m_samco)
                    break
                except Exception as e:
                    print(e)
            data = df_1m_samco["intradayCandleData"]
            df_1m_samco = pd.DataFrame(data)

            df_1m_samco['open'] = pd.to_numeric(df_1m_samco['open'], downcast='float')
            df_1m_samco['low'] = pd.to_numeric(df_1m_samco['low'], downcast='float')
            df_1m_samco['high'] = pd.to_numeric(df_1m_samco['high'], downcast='float')
            df_1m_samco['close'] = pd.to_numeric(df_1m_samco['close'], downcast='float')
            df_1m_samco['volume'] = pd.to_numeric(df_1m_samco['volume'], downcast='float')

            for jkl in [0,1,2,3,4]:
                if gogogo != 'go1':
                    break
                if df_1m_samco['high'].iloc[jkl] >= flsr(1.002 * df_1m_samco['open'].iloc[0]):
                    for tkl in range(jkl+1,5):
                        if df_1m_samco['low'].iloc[tkl] <= flsr(0.9993 * df_close.iloc[-1]):
                            gogogo = 'go'
                            break
                    break
            if gogogo != 'go1':
                for tkl in [0, 1, 2, 3, 4]:
                    if df_1m_samco['low'].iloc[tkl] <= flsr(0.9993 * df_close.iloc[-1]):
                        gogogo = 'po'
                        break
            if gogogo == 'go' or gogogo == 'po':
                if df_1m_samco['low'].iloc[tkl] <= flsr(0.9993 * df_close.iloc[-1]):
                    df_close_rada = flsr(0.9993 * df_close.iloc[-1])
                    for i in range(len(df_1m_samco) - tkl, 0, -1):
                        if aniket[0] == 'p':
                            if trr == flsr(trgett1 - stepp):
                                if df_1m_samco['high'].iloc[-1 * i] >= flsr(flsr(mintarget1) * df_close_rada):
                                    aniket = 'p' + str(flsr(mintarget1)) + stk + 'do'
                                    dattt = df_1m_samco['dateTime'].iloc[-1 * i][:19]
                                    dattt = dt.strptime(dattt, '%Y-%m-%d %H:%M:%S')
                                    break
                            if trr != flsr(trgett1 - stepp):
                                if df_1m_samco['high'].iloc[-1 * i] >= flsr(flsr(trr + flsr(stepp + sqstepp)) * df_close_rada):
                                    aniket = 'p' + str(flsr(trr + flsr(stepp + sqstepp))) + stk + 'do'
                                    dattt = df_1m_samco['dateTime'].iloc[-1 * i][:19]
                                    dattt = dt.strptime(dattt, '%Y-%m-%d %H:%M:%S')
                                    break
                        if df_1m_samco['low'].iloc[-1 * i] <= flsr((trr) * df_close_rada):
                            aniket = 'p' + str(trr) + stk + 'do'
                            dattt = df_1m_samco['dateTime'].iloc[-1 * i][:19]
                            dattt = dt.strptime(dattt, '%Y-%m-%d %H:%M:%S')
                            tl = flsr(trr)
                            for k in range(1, 25):
                                k = flsr(k * stepp)
                                trrk = flsr(trr - k)
                                if df_1m_samco['low'].iloc[-1 * i] <= flsr((trrk) * df_close_rada):
                                    aniket = 'p' + str(trrk) + stk + 'do'
                                    dattt = df_1m_samco['dateTime'].iloc[-1 * i][:19]
                                    dattt = dt.strptime(dattt, '%Y-%m-%d %H:%M:%S')
                                    tl = flsr(trrk)
                            if tl == trgett1:
                                if df_1m_samco['close'].iloc[-1 * i] >= flsr(flsr(mintarget1) * df_close_rada):
                                    aniket = 'p' + str(flsr(mintarget1)) + stk + 'do'
                                    dattt = df_1m_samco['dateTime'].iloc[-1 * i][:19]
                                    dattt = dt.strptime(dattt, '%Y-%m-%d %H:%M:%S')
                                    break
                            if tl != trgett1:
                                if df_1m_samco['close'].iloc[-1 * i] >= flsr(flsr(tl + sqstepp) * df_close_rada):
                                    aniket = 'p' + str(flsr(tl + sqstepp)) + stk + 'do'
                                    dattt = df_1m_samco['dateTime'].iloc[-1 * i][:19]
                                    dattt = dt.strptime(dattt, '%Y-%m-%d %H:%M:%S')
                                    break
                            trr = flsr(tl - stepp)

                        if aniket[0] != 'p':
                            if df_1m_samco['high'].iloc[-1 * i] >= flsr(sl * df_close_rada):
                                aniket = 'loss' + stk + 'do'
                                dattt = df_1m_samco['dateTime'].iloc[-1 * i][:19]
                                dattt = dt.strptime(dattt, '%Y-%m-%d %H:%M:%S')
                                break
                            else:
                                aniket = 'neut' + stk + 'do'
                                dattt = df_1m_samco['dateTime'].iloc[-1 * i][:19]
                                dattt = dt.strptime(dattt, '%Y-%m-%d %H:%M:%S')

        if stk[:-3] in marginn.keys():
            margink = marginn[stk[:-3]]
        if stk[:-3] not in marginn.keys():
            margink = 1

        if aniket[0] == 'p':
            if aniket[-2:] == 'up':
                profitt.append(float('{:.2f}'.format((float('{:.4f}'.format(float(aniket[1:len(aniket)-2-len(stk)])))-1)*100)))
                pandlP = flsr(pandlP + float('{:.2f}'.format((float('{:.4f}'.format(float(aniket[1:len(aniket)-2-len(stk)]))) - 1)*100)))
                pandlop = flsr((200 * float('{:.2f}'.format((float('{:.4f}'.format(float(aniket[1:len(aniket)-2-len(stk)]))) - 1)*100)) - 18)*margink)
                pandl = flsr(pandl + pandlop)
            if aniket[-2:] == 'do':
                profitt.append(float('{:.2f}'.format((1-float('{:.4f}'.format(float(aniket[1:len(aniket)-2-len(stk)]))))*100)))
                pandlP = flsr(pandlP + float('{:.2f}'.format((1 - float('{:.4f}'.format(float(aniket[1:len(aniket)-2-len(stk)]))))*100)))
                pandlop = flsr((200 * float('{:.2f}'.format((1 - float('{:.4f}'.format(float(aniket[1:len(aniket) - 2 - len(stk)])))) * 100)) - 18) * margink)
                pandl = flsr(pandl + pandlop)
        loww_list = []
        highh_list = []
        min_loww = 0
        max_highh = 0
        loww_list_5 = []
        highh_list_5 = []
        min_loww_5 = 0
        max_highh_5 = 0

        if aniket[:4] == 'loss':
            losss.append(aniket)
            if baddy == 2:
                pandlP = flsr(pandlP - flsr((sl-1)*100))
                pandlop = flsr(((-1 * flsr((sl - 1) * 100)) * 200 - 18) * margink)
            if baddy == 1:
                pandlP = flsr(pandlP - flsr((1 - sl1) * 100))
                pandlop = flsr(((-1 * flsr((1 - sl1)*100)) * 200 - 18) * margink)
            pandl = flsr(pandl + pandlop)
        if aniket[:4] == 'neut':
            neutral.append(aniket)
        if aniket!='none':
            outputt.append(aniket)
            break
    if len(outputt) != 0:
        for i in range(len(df_1m_samco) - tkl, 0, -1):
            loww_list.append(df_1m_samco['low'].iloc[-1 * i])
            highh_list.append(df_1m_samco['high'].iloc[-1 * i])
        min_loww = min(loww_list)
        max_highh = max(highh_list)

        for i in range(len(df_1m_samco), len(df_1m_samco) - 5, -1):
            loww_list_5.append(df_1m_samco['low'].iloc[-1 * i])
            highh_list_5.append(df_1m_samco['high'].iloc[-1 * i])
        min_loww_5 = min(loww_list_5)
        max_highh_5 = max(highh_list_5)

        listtttttttt_pl.append(pandl)
        if baddy == 1:
            sl_perccc = flsr(min_loww/flsr(1.0007 * df_close.iloc[-1]))
            target_perccc = flsr(max_highh/flsr(1.0007 * df_close.iloc[-1]))
            sl_perccc_5 = flsr(min_loww_5 / flsr(1.0007 * df_close.iloc[-1]))
            target_perccc_5 = flsr(max_highh_5 / flsr(1.0007 * df_close.iloc[-1]))
        if baddy == 2:
            sl_perccc = flsr(max_highh / flsr(0.9993 * df_close.iloc[-1]))
            target_perccc = flsr(min_loww / flsr(0.9993 * df_close.iloc[-1]))
            sl_perccc_5 = flsr(max_highh_5 / flsr(0.9993 * df_close.iloc[-1]))
            target_perccc_5 = flsr(min_loww_5 / flsr(0.9993 * df_close.iloc[-1]))

        normal_dfclose_loww5_perc = flsr(min_loww_5 / flsr(df_close.iloc[-1]))
        normal_dfclose_highh5_perc = flsr(max_highh_5 / flsr(df_close.iloc[-1]))

        print(' margin is ',margink,' Entry time ', str(df.index[-1])[:19],'       ',
              profitt ,'               ',pandl,'                ',outputt,'               ','End time',dattt,'    ',
              flsr(min_loww),flsr(df_close.iloc[-1]),flsr(max_highh),' ',
              sl_perccc,target_perccc,' ',sl_perccc_5,target_perccc_5,' ',normal_dfclose_loww5_perc,normal_dfclose_highh5_perc)
    return len(outputt),len(profitt),len(losss),len(neutral)


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

stocklist = []
for i in Stock_samco1:
    j = i + '.NS'
    stocklist.append(j)

st = str(stocklist)
st = st[1:]
st = st[:-1]
st = st.replace('\'', '')
st = st.replace(',', '')

df_main = yf.download(tickers=st, start='2021-01-25',interval='5m')
dfgh = df_main
for i in range(len(df_main)):
    if str(df_main.index[i])[:10] == '2021-02-24':
        dfgh = dfgh.drop([df_main.index[i],])
df_main = dfgh
# print(df_main)
print('Shape of df_main is ',df_main.shape)


csv_1=pd.read_csv('ind_nifty500listnew.csv')
u=csv_1.loc[:, 'Margin':'Margin']
v=csv_1.loc[:, 'Symbol':'Symbol']
w=v.join(u)
marginn=dict(zip(w.Symbol,w.Margin))




# ddays = int(input('Enter no. of days for backtesting'))
ddays = 41
ddays = ddays * 75 - 9
llays = 0
llays = llays * 75 + 18

star = 0
pandl = 0
pandlP = 0
listtttttttt_pl = []
Total, Profit, Loss, Neutral = 0, 0, 0, 0
dattt = '2020-01-01 12:00:00'
dattt = dt.strptime(dattt, '%Y-%m-%d %H:%M:%S')
print(dt.now(),'\n')
for i in range(ddays, llays, -1):
    star = star + 1
    if star >= 49 and star <= 75:
        if star == 75:
            star = 0
        continue
    rtyui = dt.strptime(str(df_main.index[-1*i])[:19], '%Y-%m-%d %H:%M:%S')
    if rtyui > dattt:
        v, b, n, m = bolling_macd(i, 1.0061, 1.0018, 0.0005, 0.0005, 1.0015)
        Total = Total + v
        Profit = Profit + b
        Loss = Loss + n
        Neutral = Neutral + m
print('Total=',Total,'         Profit Trades=', Profit,'        Loss Trades=', Loss,'        Neutral trades=', Neutral)
print('p&l in percentage is ', pandlP,'\n')
print('p&l is ', pandl,'\n')
plt.style.use('dark_background')
plt.plot(listtttttttt_pl)
plt.show()
print(dt.now(),'\n','\n')
















# for gh in range(20):
#     rado = 1.001 + 0.0005*gh
#     rado = flsr(rado)
#     print(rado)
#     star = 0
#     pandl = 0
#     Total, Profit, Loss, Neutral = 0, 0, 0, 0
#     dattt = '2020-01-01'
#     print(dt.now())
#     for i in range(ddays, llays, -1):
#         star = star + 1
#         if star >= 49 and star <= 75:
#             if star == 75:
#                 star = 0
#             continue
#         # if str(df_main.iloc[:-1 * i].index[-1])[:10] == dattt:
#         #     continue
#         v, b, n, m = bolling_macd(i, 1.0031, rado)
#         Total = Total + v
#         Profit = Profit + b
#         Loss = Loss + n
#         Neutral = Neutral + m
#     print('profit in % is ', pandl + Loss * 0.31)
#     pandl = 1000 * pandl - Total * 90
#     print(Total, Profit, Loss, Neutral)
#     print('p&l is ', pandl)
#     print(dt.now())