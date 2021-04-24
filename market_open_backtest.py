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
    global samco,df_main,Stock_samco1,stocklist,pandl,dattt,pandlP,marginn,listtttttttt_pl, dictt_pandl, ddays

    period_rsi = 14
    period_bollinger = 20
    multiplier1 = 1.9
    multiplier2 = 1.9

    df = df_main.iloc[:-1 * yeyy+1]
    df_rada = df_main.iloc[:-1 * yeyy + 2]

    outputt,profitt,losss,neutral = [], [],[],[]
    for stk in stocklist:
        try:
            if str(df.index[-1])[11:19] != '09:15:00' or yeyy == ddays * 75:
                break
        except Exception as e:
            print(e)
            break
        baddy = 0
        gogogo = 'start'
        df_close = df['Close'][stk]
        df_open = df['Open'][stk]
        df_high = df['High'][stk]
        df_low = df['Low'][stk]

        if df_open.iloc[-1] > flsr(1.005 * df_close.iloc[-2]):
            baddy = 1
        if df_open.iloc[-1] < flsr(0.995 * df_close.iloc[-2]):
            baddy = 2



        aniket = 'none'
        if baddy == 1:
            sl1 = flsr(2 - sl)
            trr = flsr(trgett)
            godatt = df.index[-1]

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

                for jkl in [0, 1, 2, 3, 4]:
                    if df_1m_samco['high'].iloc[jkl] > flsr(1.0035 * df_open.iloc[-1]):
                        baddy = 1
                        break
                    else:
                        baddy = 0

            if baddy == 1:
                df_close_rada = flsr(1.0035 * df_open.iloc[-1])
                for i in range(len(df_1m_samco) - jkl, 0, -1):
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
            trgett1 = flsr(2 - trgett)
            mintarget1 = flsr(2 - mintarget)
            trr = flsr(trgett1)
            godatt = df.index[-1]

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

                for jkl in [0, 1, 2, 3, 4]:
                    if df_1m_samco['low'].iloc[jkl] < flsr(0.9965 * df_open.iloc[-1]):
                        baddy = 2
                        break
                    else:
                        baddy = 0

            if baddy == 2:
                df_close_rada = flsr(0.9965 * df_open.iloc[-1])
                for i in range(len(df_1m_samco) - jkl, 0, -1):
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
            try:
                dictt_profit_trades[stk[:-3]] = dictt_profit_trades[stk[:-3]] + 1
            except Exception:
                dictt_profit_trades[stk[:-3]] = 1
            if aniket[-2:] == 'up':
                profitt.append(float('{:.2f}'.format((float('{:.4f}'.format(float(aniket[1:len(aniket)-2-len(stk)])))-1)*100)))
                pandlP = flsr(pandlP + float('{:.2f}'.format((float('{:.4f}'.format(float(aniket[1:len(aniket)-2-len(stk)]))) - 1)*100)))
                pandlop = flsr((200 * float('{:.2f}'.format((float('{:.4f}'.format(float(aniket[1:len(aniket)-2-len(stk)]))) - 1)*100)) - 18 - 40)*margink)
                pandl = flsr(pandl + pandlop)
            if aniket[-2:] == 'do':
                profitt.append(float('{:.2f}'.format((1-float('{:.4f}'.format(float(aniket[1:len(aniket)-2-len(stk)]))))*100)))
                pandlP = flsr(pandlP + float('{:.2f}'.format((1 - float('{:.4f}'.format(float(aniket[1:len(aniket)-2-len(stk)]))))*100)))
                pandlop = flsr((200 * float('{:.2f}'.format((1 - float('{:.4f}'.format(float(aniket[1:len(aniket) - 2 - len(stk)])))) * 100)) - 18 - 40) * margink)
                pandl = flsr(pandl + pandlop)


        if aniket[:4] == 'loss':
            losss.append(aniket)
            try:
                dictt_loss_trades[stk[:-3]] = dictt_loss_trades[stk[:-3]] + 1
            except Exception:
                dictt_loss_trades[stk[:-3]] = 1
            if baddy == 2:
                pandlP = flsr(pandlP - flsr((sl-1)*100))
                pandlop = flsr(((-1 * flsr((sl - 1) * 100)) * 200 - 18 - 40) * margink)
            if baddy == 1:
                pandlP = flsr(pandlP - flsr((1 - sl1) * 100))
                pandlop = flsr(((-1 * flsr((1 - sl1)*100)) * 200 - 18 - 40) * margink)
            pandl = flsr(pandl + pandlop)
        if aniket[:4] == 'neut':
            neutral.append(aniket)
            try:
                dictt_neutral_trades[stk[:-3]] = dictt_neutral_trades[stk[:-3]] + 1
            except Exception:
                dictt_neutral_trades[stk[:-3]] = 1
        if aniket!='none':
            outputt.append(aniket)
            try:
                dictt_pandl[stk[:-3]] = dictt_pandl[stk[:-3]] + pandlop
            except Exception:
                dictt_pandl[stk[:-3]] = pandlop
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


# csv_2=pd.read_csv('ind_nifty500list.csv')
# Stock_samco1=csv_2.loc[:, 'Symbol':'Symbol']
# Stock_samco1=Stock_samco1.Symbol
# Stock_samco1=Stock_samco1.tolist()
# Stock_samco1.remove('BAJFINANCE')
# Stock_samco1.insert(0,'BAJFINANCE')
# Stock_samco1.remove('DIXON')
# Stock_samco1.remove('ASTRAL')
# Stock_samco1.remove('FINPIPE')

Stock_samco1 = ['ATGL','ASHOKA','ADANITRANS','GICRE']


stocklist = []
for i in Stock_samco1:
    j = i + '.NS'
    stocklist.append(j)

st = str(stocklist)
st = st[1:]
st = st[:-1]
st = st.replace('\'', '')
st = st.replace(',', '')

df_main = yf.download(tickers=st, start='2021-02-25', interval='5m')
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
ddays = 36
ddays = ddays * 75
llays = 0
llays = llays * 75

pandl = 0
pandlP = 0
dictt_pandl = {}
dictt_profit_trades = {}
dictt_loss_trades = {}
dictt_neutral_trades = {}
listtttttttt_pl = []
Total, Profit, Loss, Neutral = 0, 0, 0, 0
dattt = '2020-01-01 12:00:00'
dattt = dt.strptime(dattt, '%Y-%m-%d %H:%M:%S')
print(dt.now(),'\n')
for i in range(ddays, llays, -1):
    if str(df_main.index[:-1 * i+1])[:10] == '2021-02-25':
        continue
    v, b, n, m = bolling_macd(i, 1.002, 1.0025, 0.002, 0.0015, 1.002)
    Total = Total + v
    Profit = Profit + b
    Loss = Loss + n
    Neutral = Neutral + m
print('Total=',Total,'         Profit Trades=', Profit,'        Loss Trades=', Loss,'        Neutral trades=', Neutral)
print('p&l in percentage is ', pandlP,'\n')
print('p&l is ', pandl,'\n')

print(dictt_pandl)
print(dictt_profit_trades)
print(dictt_loss_trades)
print(dictt_neutral_trades)
maxkey = max(dictt_pandl, key=dictt_pandl.get)
# maxkey1 = (dictt_pandl, key=dictt_pandl.get)
maxkey2 = min(dictt_pandl, key=dictt_pandl.get)
print(maxkey, ' max= ', dictt_pandl[maxkey])
print(dictt_profit_trades[maxkey])
try:
    print(dictt_loss_trades[maxkey])
except Exception:
    pass
try:
    print(dictt_neutral_trades[maxkey])
except Exception:
    pass
# print(maxkey1, ' avg= ', dictt_pandl[maxkey1])
print(maxkey2, ' min= ', dictt_pandl[maxkey2])

sorttt = sorted(dictt_pandl,key=dictt_pandl.get,reverse=True)
print(sorttt)
jjj = 0
for r in sorttt:
    jjj = jjj + 1
    print(r,dictt_pandl[r])
    if jjj > 10:
        break


plt.style.use('dark_background')
plt.plot(listtttttttt_pl)
plt.show()
