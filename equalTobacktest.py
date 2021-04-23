import math
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta as td
from snapi_py_client.snapi_bridge import StocknoteAPIPythonBridge
import requests
import time
import configparser as cfg
import yfinance as yf
import matplotlib.pyplot as plt


def read_token_from_config_file(config, key):
    parser = cfg.ConfigParser()
    parser.read(config)
    return parser.get('creds', key)

def bolling_macd(yeyy,sl,trgett,stepp,sqstepp,mintarget):
    global samco,df_main,Stock_samco1,stocklist,pandl,dattt,pandlP,marginn,listtttttttt_pl

    period_rsi = 14
    period_bollinger = 20
    multiplier1 = 1.9
    multiplier2 = 1.9

    df = df_main.iloc[:-1 * yeyy+1]
    df_rada = df_main.iloc[:-1 * yeyy + 2]

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

        stochrsii = (rsii - rsii.rolling(period_rsi).min()) / (
                    rsii.rolling(period_rsi).max() - rsii.rolling(period_rsi).min())
        stochrsii_K = stochrsii.rolling(3).mean()
        stochrsii_D = stochrsii_K.rolling(3).mean()

        MiddleBand = df_close.rolling(period_bollinger).mean()
        UpperBand = MiddleBand + df_close.rolling(period_bollinger).std() * multiplier1
        LowerBand = MiddleBand - df_close.rolling(period_bollinger).std() * multiplier2

        df_rada_open = df_rada['Open'][stk]
        df_rada_high = df_rada['High'][stk]
        df_rada_low = df_rada['Low'][stk]

        # df_avg_perc = flsr(flsr(( df_close.iloc[-1] + df_open.iloc[-1] ) / 2) / df_close.iloc[-1])

        if df_close.iloc[-2] > 22 and flsr(100 * stochrsii_K[-2]) > 80 and df_close.iloc[-2] > flsr(
                UpperBand.iloc[-2]) > df_open.iloc[-2]:
            # if df_high.iloc[-1] >= flsr(1.002*df_close.iloc[-1]) and df_low.iloc[-1] >= flsr(0.9975 * df_open.iloc[-1]):
            #     baddy = 2
            if ((df_close.iloc[-2] - df_open.iloc[-1]) / df_close.iloc[-2] < 0.0002) and (
                    df_close.iloc[-2] > flsr(df_open.iloc[-2] * 1.008)) and (
                    df_close.iloc[-1] < flsr(df_close.iloc[-2] * 0.992)) \
                    and (df_close.iloc[-1] > df_open.iloc[-2]):
                baddy = 2
            # for i in range(1, 6):
            #     if df_close.iloc[-1*i] < df_close.iloc[-1*i-1]:
            #         baddy = 0
            #         break
        if df_close.iloc[-2] > 22 and flsr(100 * stochrsii_K[-2]) < 20 and df_close.iloc[-2] < flsr(
                LowerBand.iloc[-2]) < df_open.iloc[-2]:
            # if df_low.iloc[-1] <= flsr(0.998*df_close.iloc[-1]) and df_high.iloc[-1] <= flsr(1.0025 * df_open.iloc[-1]):
            #     baddy = 1
            if ((df_close.iloc[-2] - df_open.iloc[-1]) / df_close.iloc[-2] < 0.0002) and (
                    df_close.iloc[-2] < flsr(df_open.iloc[-2] * 0.992)) and (
                    df_close.iloc[-1] > flsr(df_close.iloc[-2] * 1.008)) and (
                    (df_low.iloc[-1] - df_open.iloc[-1]) / df_open.iloc[-1] > -0.007) and (
                    df_close.iloc[-1] < df_open.iloc[-2]):
                baddy = 1
            # for i in range(1, 6):
            #     if df_close.iloc[-1*i] > df_close.iloc[-1*i-1]:
            #         baddy = 0
            #         break

        aniket = 'none'
        if baddy == 1:
            print('baddy1 ', stk, df.index[-1])
            # sl1 = flsr(2 - sl)
            sl1 = flsr(df_low.iloc[-1] / df_high.iloc[-1])
            trr = flsr(trgett)
            godatt = df.index[-1] + td(minutes=5)

            df_1m_samco = pd.read_csv(stk[:-3] + "_1m_samco.csv")
            try:
                aalist = list(df_1m_samco['dateTime']).index(str(godatt)[:19] + '.0')
                aalist2 = list(df_1m_samco['dateTime']).index(str(godatt)[:10] + ' 15:29:00' + '.0')
            except Exception as e:
                print(stk + ' df 1m dateTime error  ', e)
                baddy = 0

            if baddy == 1:
                try:
                    df_1m_samco = df_1m_samco[aalist:aalist2 + 1]
                except Exception:
                    df_1m_samco = df_1m_samco[aalist:]

                for jkl in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
                    # if gogogo != 'go1':
                    #     break
                    if df_1m_samco['high'].iloc[jkl] > flsr(1.0005 * df_high.iloc[-1]):
                        tkl = jkl
                        gogogo = 'go'
                        # if jkl !=4:
                        #     for vkl in range(jkl, tkl + 1):
                        #         if df_1m_samco['low'].iloc[vkl] <= flsr(0.9962 * df_close.iloc[-1]):
                        #             gogogo = 'notgo'
                        #             break
                        break
                # if gogogo != 'go1':
                #     for tkl in [0, 1, 2, 3, 4]:
                #         if df_1m_samco['high'].iloc[tkl] >= flsr(1.0007 * df_close.iloc[-1]):
                #             gogogo = 'po'
                #             break
            if gogogo == 'go' or gogogo == 'po' and baddy == 1:
                if df_1m_samco['high'].iloc[tkl] > flsr(1.0005 * df_high.iloc[-1]):
                    datetime_samco1 = df_1m_samco['dateTime'].iloc[tkl][:19]
                    datetime_samco = dt.strptime(datetime_samco1, '%Y-%m-%d %H:%M:%S')
                    df_close_rada = flsr(1.0005 * df_high.iloc[-1])
                    for i in range(len(df_1m_samco) - tkl, 0, -1):
                        if aniket[0] == 'p':
                            if trr == flsr(trgett + stepp):
                                if df_1m_samco['low'].iloc[-1 * i] <= flsr(flsr(mintarget) * df_close_rada):
                                    aniket = 'p' + str(flsr(mintarget)) + stk + 'up'
                                    dattt = df_1m_samco['dateTime'].iloc[-1 * i][:19]
                                    dattt = dt.strptime(dattt, '%Y-%m-%d %H:%M:%S')
                                    break
                            if trr != flsr(trgett + stepp):
                                if df_1m_samco['low'].iloc[-1 * i] <= flsr(
                                        flsr(trr - flsr(stepp + sqstepp)) * df_close_rada):
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
            print('baddy2 ', stk, df.index[-1])
            sl = flsr(df_high.iloc[-1] / df_low.iloc[-1])
            trgett1 = flsr(2 - trgett)
            mintarget1 = flsr(2 - mintarget)
            trr = flsr(trgett1)
            godatt = df.index[-1] + td(minutes=5)

            df_1m_samco = pd.read_csv(stk[:-3] + "_1m_samco.csv")
            try:
                aalist = list(df_1m_samco['dateTime']).index(str(godatt)[:19] + '.0')
                aalist2 = list(df_1m_samco['dateTime']).index(str(godatt)[:10] + ' 15:29:00' + '.0')
            except Exception as e:
                print(stk + ' df 1m dateTime error  ', e)
                baddy = 0

            if baddy == 2:
                try:
                    df_1m_samco = df_1m_samco[aalist:aalist2 + 1]
                except Exception:
                    df_1m_samco = df_1m_samco[aalist:]

                for jkl in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
                    # if gogogo != 'go1':
                    #     break
                    if df_1m_samco['low'].iloc[jkl] < flsr(0.9995 * df_low.iloc[-1]):
                        tkl = jkl
                        gogogo = 'go'
                        # if jkl != 4:
                        #     for vkl in range(jkl, tkl + 1):
                        #         if df_1m_samco['high'].iloc[vkl] >= flsr(1.0038 * df_close.iloc[-1]):
                        #             gogogo = 'notgo'
                        #             break
                        break
                # if gogogo != 'go1':
                #     for tkl in [0, 1, 2, 3, 4]:
                #         if df_1m_samco['low'].iloc[tkl] <= flsr(0.9993 * df_close.iloc[-1]):
                #             gogogo = 'po'
                #             break
            if gogogo == 'go' or gogogo == 'po' and baddy == 2:
                if df_1m_samco['low'].iloc[jkl] < flsr(0.9995 * df_low.iloc[-1]):
                    datetime_samco1 = df_1m_samco['dateTime'].iloc[tkl][:19]
                    datetime_samco = dt.strptime(datetime_samco1, '%Y-%m-%d %H:%M:%S')
                    df_close_rada = flsr(0.9995 * df_low.iloc[-1])
                    for i in range(len(df_1m_samco) - tkl, 0, -1):
                        if aniket[0] == 'p':
                            if trr == flsr(trgett1 - stepp):
                                if df_1m_samco['high'].iloc[-1 * i] >= flsr(flsr(mintarget1) * df_close_rada):
                                    aniket = 'p' + str(flsr(mintarget1)) + stk + 'do'
                                    dattt = df_1m_samco['dateTime'].iloc[-1 * i][:19]
                                    dattt = dt.strptime(dattt, '%Y-%m-%d %H:%M:%S')
                                    break
                            if trr != flsr(trgett1 - stepp):
                                if df_1m_samco['high'].iloc[-1 * i] >= flsr(
                                        flsr(trr + flsr(stepp + sqstepp)) * df_close_rada):
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
                pandlop = flsr((200 * float('{:.2f}'.format((float('{:.4f}'.format(float(aniket[1:len(aniket)-2-len(stk)]))) - 1)*100)) - 18 - 20)*margink)
                pandl = flsr(pandl + pandlop)
            if aniket[-2:] == 'do':
                profitt.append(float('{:.2f}'.format((1-float('{:.4f}'.format(float(aniket[1:len(aniket)-2-len(stk)]))))*100)))
                pandlP = flsr(pandlP + float('{:.2f}'.format((1 - float('{:.4f}'.format(float(aniket[1:len(aniket)-2-len(stk)]))))*100)))
                pandlop = flsr((200 * float('{:.2f}'.format((1 - float('{:.4f}'.format(float(aniket[1:len(aniket) - 2 - len(stk)])))) * 100)) - 18 - 20) * margink)
                pandl = flsr(pandl + pandlop)


        if aniket[:4] == 'loss':
            losss.append(aniket)
            if baddy == 2:
                pandlP = flsr(pandlP - flsr((sl-1)*100))
                pandlop = flsr(((-1 * flsr((sl - 1) * 100)) * 200 - 18 - 20) * margink)
            if baddy == 1:
                pandlP = flsr(pandlP - flsr((1 - sl1) * 100))
                pandlop = flsr(((-1 * flsr((1 - sl1)*100)) * 200 - 18 - 20) * margink)
            pandl = flsr(pandl + pandlop)
        if aniket[:4] == 'neut':
            neutral.append(aniket)
        if aniket!='none':
            outputt.append(aniket)
            break
    if len(outputt) != 0:
        listtttttttt_pl.append(pandl)
        print(' margin is ', margink, ' Entry time ', str(df.index[-1])[:19], '       ',
              profitt, '          ', pandl, '            ', outputt, '               ', 'End time', dattt)

    return len(outputt),len(profitt),len(losss),len(neutral)


def flsr(a):
    return float('{:.5f}'.format(float(a)))

samco = StocknoteAPIPythonBridge()
# userId, password, yob = read_token_from_config_file("login_data.cfg", "userId"), read_token_from_config_file(
#         "login_data.cfg", "password"), read_token_from_config_file("login_data.cfg", "yob")
# login = samco.login(body={"userId": userId, 'password': password, 'yob': yob})
# # print('Login Details\n', login)
# login = eval(login)
# samco.set_session_token(sessionToken=login['sessionToken'])


csv_2=pd.read_csv('ind_nifty500list.csv')
Stock_samco1=csv_2.loc[:, 'Symbol':'Symbol']
Stock_samco1=Stock_samco1.Symbol
Stock_samco1=Stock_samco1.tolist()
Stock_samco1.remove('BAJFINANCE')
Stock_samco1.insert(0,'BAJFINANCE')
Stock_samco1.remove('DIXON')
Stock_samco1.remove('ASTRAL')

stocklist = []
for i in Stock_samco1:
    j = i + '.NS'
    stocklist.append(j)

st = str(stocklist)
st = st[1:]
st = st[:-1]
st = st.replace('\'', '')
st = st.replace(',', '')

df_main = yf.download(tickers=st, start='2021-03-23', end='2021-04-19', interval='5m')
dfgh = df_main
for i in range(len(df_main)):
    if str(df_main.index[i])[:10] == '2021-02-24' or str(df_main.index[i])[:10] == '2021-04-23' or \
            str(df_main.index[i])[:10] == '2021-04-22' or str(df_main.index[i])[:10] == '2021-04-21' or \
            str(df_main.index[i])[:10] == '2021-04-20' or str(df_main.index[i])[:10] == '2021-04-19':
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
ddays = 13
ddays = ddays * 75 - 1
llays = 0
llays = llays * 75 + 6

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
    if star >= 69 and star <= 75:
        if star == 75:
            star = 0
        continue
    rtyui = dt.strptime(str(df_main.index[-1*i])[:19], '%Y-%m-%d %H:%M:%S')
    if rtyui > dattt:
        v, b, n, m = bolling_macd(i, 1.006, 1.0025, 0.0015, 0.002, 1.002)
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
