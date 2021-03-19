from methods_bollinger import *

#---     VARIABLES  ---
down_target = 0.9975
down_SL = 1.0026
up_target = 1.0025
up_SL = 0.9974
#---     VARIABLES  ---


#---     INPUTS  ---
csv_2=pd.read_csv('ind_nifty500list.csv')
Stock_samco1=csv_2.loc[:, 'Symbol':'Symbol']
Stock_samco1=Stock_samco1.Symbol
Stock_samco1=Stock_samco1.tolist()
Stock_samco1.remove('SBIN')
Stock_samco1.insert(0,'SBIN')

print('Minimum Amount is Rs 30K')
amount = int(input('HOW MUCH AMOUNT TO TRADE TODAYYY = '))
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
