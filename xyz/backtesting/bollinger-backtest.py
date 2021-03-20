import pandas as pd

def bolling_macd(yeyy):
    global df_main,Stock_samco1,stocklist

    period_rsi = 14
    period_bollinger = 20
    multiplier1 = 2
    multiplier2 = 2

    df = df_main.iloc[:-1 * yeyy]
    df_confirm = df_main.iloc[:-1 * (yeyy-20)]

    outputt,profitt,losss,neutral = [], [],[],[]
    for stk in stocklist:
        baddy = 0
        df_close = df['close'+ stk]
        df_open = df['open'+ stk]
        df_high = df['high'+ stk]
        df_low = df['low'+ stk]
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
        BandDiffer = (UpperBand - LowerBand) / MiddleBand

        macd = df_close.ewm(span=12, adjust=False).mean() - df_close.ewm(span=26, adjust=False).mean()

        if df_close.iloc[-1] >= 1.0005 * UpperBand.iloc[-1]:
            if df_open.iloc[-1] <= UpperBand.iloc[-1] and df_open.iloc[-1] >= MiddleBand.iloc[-1] and macd.iloc[-1] > \
                    macd.iloc[-2] and macd.iloc[-2] > macd.iloc[-3] and rsii.iloc[-1] < 75:
                baddy = 1
                for i in range(2, 7):
                    if df_low.iloc[-1 * i] < LowerBand.iloc[-1 * i] or df_high.iloc[-1 * i] > UpperBand.iloc[-1 * i] or BandDiffer.iloc[
                        -1 * i] > 0.008:
                        baddy = 0
                        break
                for i in range(7, 9):
                    if df_open.iloc[-1 * i] < LowerBand.iloc[-1 * i] or df_close.iloc[-1 * i] > UpperBand.iloc[-1 * i] or BandDiffer.iloc[
                        -1 * i] > 0.008:
                        baddy = 0
                        break
        if df_close.iloc[-1] <= 0.9995 * LowerBand.iloc[-1]:
            if df_open.iloc[-1] >= LowerBand.iloc[-1] and df_open.iloc[-1] <= MiddleBand.iloc[-1] and macd.iloc[-1] < \
                    macd.iloc[-2] and macd.iloc[-2] < macd.iloc[-3] and rsii.iloc[-1] > 25:
                baddy = 2
                for i in range(2, 7):
                    if df_low.iloc[-1 * i] < LowerBand.iloc[-1 * i] or df_high.iloc[-1 * i] > UpperBand.iloc[-1 * i] or BandDiffer.iloc[
                        -1 * i] > 0.008:
                        baddy = 0
                        break
                for i in range(7, 9):
                    if df_close.iloc[-1 * i] < LowerBand.iloc[-1 * i] or df_open.iloc[-1 * i] > UpperBand.iloc[-1 * i] or BandDiffer.iloc[
                        -1 * i] > 0.008:
                        baddy = 0
                        break

        aniket = 'none'
        if baddy == 1:
            for i in range(20,0,-1):
                if df_confirm['low'+stk].iloc[-1 * i] >= (1.0025) * df_close.iloc[-1]:
                    aniket = 'prof'+stk + 'up'
                    break
                if df_confirm['high'+stk].iloc[-1 * i] <= (0.995) * df_close.iloc[-1]:
                    aniket = 'loss'+stk + 'up'
                    break
                else:
                    aniket = 'neut'+stk+'up'

        if baddy == 2:
            for i in range(20,0,-1):
                if df_confirm['high'+stk].iloc[-1 * i] <= (0.9975) * df_close.iloc[-1]:
                    aniket = 'prof'+stk + 'do'
                    break
                if df_confirm['low'+stk].iloc[-1 * i] >= (1.005) * df_close.iloc[-1]:
                    aniket = 'loss'+stk + 'do'
                    break
                else:
                    aniket = 'neut'+stk+'do'

        if aniket!='none':
            outputt.append(aniket)
        if aniket[:4] == 'prof':
            profitt.append(aniket)
        if aniket[:4] == 'loss':
            losss.append(aniket)
        if aniket[:4] == 'neut':
            neutral.append(aniket)

    return len(outputt),len(profitt),len(losss),len(neutral)

Total,Profit,Loss,Neutral = 0,0,0,0

df_main = pd.read_csv('dfff_samco.csv')

with open('stock_list.txt', 'r') as f:
    stocklist = f.read()
stocklist = eval(stocklist)

# ddays = int(input('Enter no. of days for backtesting'))
ddays = 15
ddays = ddays * 74 - 9

str= 0
for i in range(ddays,25,-1):
    str = str +1
    if str >= 48 and str <= 74:
        if str == 74:
            str =0
        continue
    v,b,n,m=bolling_macd(i)
    Total=Total+v
    Profit=Profit+b
    Loss=Loss+n
    Neutral=Neutral+m

print(Total,'\n',Profit,'\n',Loss,'\n',Neutral)
