import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QFileDialog, QGridLayout, QLabel, QPushButton, QMessageBox 
from PyQt5.QtCore import QThread, pyqtSignal,QDate,QStringListModel
from PyQt5.QtWidgets import QMainWindow
from Ui_stock import Ui_MainWindow
import requests
import pandas as pd
import yfinance as yf 
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt



cleaned_data = []
filter_data_up20MA = []
filter_data_down20MA = []
filter_data_range20MA = []
filter_data_up=[]
filter_data_down=[]
time_end=""
today=""
up_list=[]
down_list=[]

up_low_price=0
up_high_price=0
up_num=0
up_gain=0
down_low_price=0
down_high_price=0
down_num=0
down_gain=0
checkBox_up_bb_flag = False
checkBox_down_bb_flag = False


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        today=dt.datetime.today().strftime('%Y%m%d')
        date_Y=dt.datetime.today().strftime('%Y')
        date_M=dt.datetime.today().strftime('%m')
        date_D=dt.datetime.today().strftime('%d')
        d = QDate(int(date_Y), int(date_M), int(date_D))
        self.dateEdit_date_end.setDate(d)

    def display(self,int):
        if int==100:
            self.progressBar.setValue(100)
            self.listView_up.clicked.connect(self.up_clicked)
            self.listView_down.clicked.connect(self.down_clicked)
        else:
            self.progressBar.setValue(int)


    def get_sma(self,prices, rate):
        return prices.rolling(rate).mean()

    def get_bollinger_bands(self,prices, rate=20):
        sma = self.get_sma(prices, rate)
        std = prices.rolling(rate).std(ddof=0)
        bollinger_up = sma + std * 2 # Calculate top band
        bollinger_down = sma - std * 2 # Calculate bottom band
        return sma,bollinger_up, bollinger_down

    
    def up_clicked(self,qModelIndex):
        global up_list
        stock = up_list[qModelIndex.row()].split('|',1)[0]
        stock_name = up_list[qModelIndex.row()].split('|',2)[1]
        equity = yf.Ticker(stock+".TW")
        data = equity.history(period='1y')
        df = data[['Close']]
        sma,bollinger_up, bollinger_down = self.get_bollinger_bands(df)

        plt.title(stock + ' Bollinger Bands')
        plt.xlabel('Days')
        plt.ylabel('Closing Prices')
        plt.plot(df, label='Closing Prices')
        plt.plot(bollinger_up, label='Bollinger Up', c='g')
        plt.plot(sma, label='20MA', c='y')
        plt.plot(bollinger_down, label='Bollinger Down', c='r')
        plt.legend()
        plt.show()




    def down_clicked(self,qModelIndex):
        global down_list
        stock = down_list[qModelIndex.row()].split('|',1)[0]
        stock_name = up_list[qModelIndex.row()].split('|',2)[1]
        equity = yf.Ticker(stock+".TW")
        data = equity.history(period='1y')
        df = data[['Close']]
        sma,bollinger_up, bollinger_down = self.get_bollinger_bands(df)

        plt.title(stock + ' Bollinger Bands')
        plt.xlabel('Days')
        plt.ylabel('Closing Prices')
        plt.plot(df, label='Closing Prices')
        plt.plot(bollinger_up, label='Bollinger Up', c='g')
        plt.plot(sma, label='20MA', c='y')
        plt.plot(bollinger_down, label='Bollinger Down', c='r')
        plt.legend()
        plt.show()
        

    def display_listview_up(self,list):
        global up_list
        up_list = list
        slm=QStringListModel()
        slm.setStringList(up_list)
        self.listView_up.setModel(slm)
        

    def display_listview_down(self,list):
        global down_list
        down_list = list
        slm=QStringListModel()
        slm.setStringList(down_list)
        self.listView_down.setModel(slm)

            

    def slot1(self):
        global cleaned_data,filter_data_up20MA,filter_data_down20MA,filter_data_range20MA,filter_data_up,filter_data_down,time_end,today,up_low_price,up_high_price,up_num,up_gain,down_low_price,down_high_price,down_num,down_gain,checkBox_up_bb_flag,checkBox_down_bb_flag

        del cleaned_data[:]
        del filter_data_up20MA[:]
        del filter_data_down20MA[:]
        del filter_data_range20MA[:]
        del filter_data_up[:]
        del filter_data_down[:]
        if self.checkBox_up_bb.isChecked()==True:
            checkBox_up_bb_flag = True
        else:
            checkBox_up_bb_flag = False

        if self.checkBox_down_bb.isChecked()==True:
            checkBox_down_bb_flag = True
        else:
            checkBox_down_bb_flag = False


        up_low_price = int(self.lineEdit_up_low_price.text())
        up_high_price = int(self.lineEdit_up_high_price.text())
        up_num = int(self.lineEdit_up_num.text())
        up_gain = float(self.lineEdit_up_gain.text())

        down_low_price = int(self.lineEdit_down_low_price.text())
        down_high_price = int(self.lineEdit_down_high_price.text())
        down_num = int(self.lineEdit_down_num.text())
        down_gain = float(self.lineEdit_down_gain.text())

        date_Y = str(self.dateEdit_date_end.date().year())
        date_M = str(self.dateEdit_date_end.date().month()).zfill(2)
        date_D = str(self.dateEdit_date_end.date().day()).zfill(2)
        today = date_Y+date_M+date_D


        
        try:
            # 把csv檔抓下來
            url = 'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date='+today+'&type=ALL'
            res = requests.get(url)
            data = res.text

            # 把爬下來的資料整理乾淨

            for da in data.split('\n'):
                if len(da.split('","')) == 16 and da.split('","')[0][0] != '=':
                    cleaned_data.append([ele.replace('",\r','').replace('"','') 
                                        for ele in da.split('","')])

            filter_data_up20MA.append(cleaned_data[0])
            filter_data_down20MA.append(cleaned_data[0])
            filter_data_range20MA.append(cleaned_data[0])
            filter_data_up.append(cleaned_data[0])
            filter_data_down.append(cleaned_data[0])

            time_end=date_Y+"-"+date_M+"-"+date_D


            self.work = WorkThread()
            self.work.start()
            self.work.trigger.connect(self.display)
            self.work.trigger_up.connect(self.display_listview_up)
            self.work.trigger_down.connect(self.display_listview_down)
        except:
            QMessageBox.warning(None,"Error", "沒有資料(當日需2點後查看)")


    def slot2(self):
        global cleaned_data,filter_data_up20MA,filter_data_down20MA,filter_data_range20MA,filter_data_up,filter_data_down,time_end,today,up_low_price,up_high_price,up_num,up_gain,down_low_price,down_high_price,down_num,down_gain
        if len(cleaned_data)==0:
            QMessageBox.warning(None,"Error", "請先篩選條件並撈取資料")
        else:
            #-----上漲清單-----
            filter_data_newup=[]
            filter_data_newup.append(["證券代號","名稱","開","高","低","收","漲","成交股數","漲幅","下影線1.5"])
            for i in range(1,len(filter_data_up)):
                open = float(filter_data_up[i][5].replace(',', ''))
                high = float(filter_data_up[i][6].replace(',', ''))
                low = float(filter_data_up[i][7].replace(',', ''))
                close = float(filter_data_up[i][8].replace(',', ''))
                num = int(filter_data_up[i][2].replace(',', ''))
                value = float(filter_data_up[i][10])
                d_value = value/(close-value)*100
                a = "%.2f" % value
                b = float("%.2f" % d_value)
                try:
                    d_line = (open-low)/(close-open)
                    filter_data_newup.append([filter_data_up[i][0],filter_data_up[i][1],open,high,low,close,a,str(num),b,d_line])
                except:
                    filter_data_newup.append([filter_data_up[i][0],filter_data_up[i][1],open,high,low,close,a,str(num),b,""])
            #-----下跌清單-----
            filter_data_newdown=[]
            filter_data_newdown.append(["證券代號","名稱","開","高","低","收","漲","成交股數","漲幅","下影線1.5"])
            for i in range(1,len(filter_data_down)):
                open = float(filter_data_down[i][5].replace(',', ''))
                high = float(filter_data_down[i][6].replace(',', ''))
                low = float(filter_data_down[i][7].replace(',', ''))
                close = float(filter_data_down[i][8].replace(',', ''))
                num = int(filter_data_down[i][2].replace(',', ''))
                value = float(filter_data_down[i][10])
                d_value = value/(close-value)*100
                a = "-"+"%.2f" % value
                b = float("-"+"%.2f" % d_value)
                try:
                    d_line = (close-low)/(open-close)
                    filter_data_newdown.append([filter_data_down[i][0],filter_data_down[i][1],open,high,low,close,a,str(num),b,d_line])
                except:
                    filter_data_newdown.append([filter_data_down[i][0],filter_data_down[i][1],open,high,low,close,a,str(num),b,""])
            #-----大於20MA清單-----
            filter_data_up20MA_new=[]
            filter_data_up20MA_new.append(["證券代號","名稱","開","高","低","收","漲","成交股數","漲幅","下影線1.5"])
            for i in range(1,len(filter_data_up20MA)):
                open = float(filter_data_up20MA[i][5])
                high = float(filter_data_up20MA[i][6])
                low = float(filter_data_up20MA[i][7])
                close = float(filter_data_up20MA[i][8])
                num = int(filter_data_up20MA[i][2].replace(',', ''))
                value = float(filter_data_up20MA[i][10])
                d_value = value/(close-value)*100
                a = "%.2f" % value
                b = float("%.2f" % d_value)
                filter_data_up20MA_new.append([filter_data_up20MA[i][0],filter_data_up20MA[i][1],open,high,low,close,a,str(num),b,""])
            #-----低於20MA清單-----
            filter_data_down20MA_new=[]
            filter_data_down20MA_new.append(["證券代號","名稱","開","高","低","收","漲","成交股數","漲幅","下影線1.5"])
            for i in range(1,len(filter_data_down20MA)):
                open = float(filter_data_down20MA[i][5])
                high = float(filter_data_down20MA[i][6])
                low = float(filter_data_down20MA[i][7])
                close = float(filter_data_down20MA[i][8])
                num = int(filter_data_down20MA[i][2].replace(',', ''))
                value = float(filter_data_down20MA[i][10])
                d_value = value/(close-value)*100
                a = "%.2f" % value
                b = float("%.2f" % d_value)
                filter_data_down20MA_new.append([filter_data_down20MA[i][0],filter_data_down20MA[i][1],open,high,low,close,a,str(num),b,""])
            #-----20MA上下限內-----
            filter_data_range20MA_new=[]
            filter_data_range20MA_new.append(["證券代號","名稱","開","高","低","收","漲","成交股數","漲幅","下影線1.5"])
            for i in range(1,len(filter_data_range20MA)):
                open = float(filter_data_range20MA[i][5])
                high = float(filter_data_range20MA[i][6])
                low = float(filter_data_range20MA[i][7])
                close = float(filter_data_range20MA[i][8])
                num = int(filter_data_range20MA[i][2].replace(',', ''))
                value = float(filter_data_range20MA[i][10])
                d_value = value/(close-value)*100
                a = "%.2f" % value
                b = float("%.2f" % d_value)
                filter_data_range20MA_new.append([filter_data_range20MA[i][0],filter_data_range20MA[i][1],open,high,low,close,a,str(num),b,""])
            # #輸出成表格並呈現在excel上
            df = pd.DataFrame(cleaned_data, columns = cleaned_data[0])
            df = df.set_index('證券代號')[1:]
            # # 輸出成表格並呈現在excel上
            df1 = pd.DataFrame(filter_data_newup, columns = ["證券代號","名稱","開","高","低","收","漲","成交股數","漲幅","下影線1.5"])
            df1 = df1.set_index('證券代號')[1:]
            df1 = df1.sort_values(by=['漲幅'])
            df1['漲幅'] = df1['漲幅'].astype(str)+"%"
            # # 輸出成表格並呈現在excel上
            df2 = pd.DataFrame(filter_data_newdown, columns = ["證券代號","名稱","開","高","低","收","跌","成交股數","跌幅","下影線1.5"])
            df2 = df2.set_index('證券代號')[1:]
            df2 = df2.sort_values(by=['跌幅'])
            df2['跌幅'] = df2['跌幅'].astype(str)+"%"
            # # 輸出成表格並呈現在excel上
            df3 = pd.DataFrame(filter_data_up20MA_new, columns = ["證券代號","名稱","開","高","低","收","漲","成交股數","漲幅","下影線1.5"])
            df3 = df3.set_index('證券代號')[1:]
            df3 = df3.sort_values(by=['漲幅'])
            df3['漲幅'] = df3['漲幅'].astype(str)+"%"
            # # 輸出成表格並呈現在excel上
            df4 = pd.DataFrame(filter_data_down20MA_new, columns = ["證券代號","名稱","開","高","低","收","漲","成交股數","漲幅","下影線1.5"])
            df4 = df4.set_index('證券代號')[1:]
            df4 = df4.sort_values(by=['漲幅'])
            df4['漲幅'] = df4['漲幅'].astype(str)+"%"
            # # 輸出成表格並呈現在excel上
            df5 = pd.DataFrame(filter_data_range20MA_new, columns = ["證券代號","名稱","開","高","低","收","漲","成交股數","漲幅","下影線1.5"])
            df5 = df5.set_index('證券代號')[1:]
            df5 = df5.sort_values(by=['漲幅'])
            df5['漲幅'] = df4['漲幅'].astype(str)+"%"
            with pd.ExcelWriter(today+".xlsx") as writer:  
                df1.to_excel(writer, sheet_name='今日漲資料')
                df2.to_excel(writer, sheet_name='今日跌資料')
                df3.to_excel(writer, sheet_name='高於20MA')
                df4.to_excel(writer, sheet_name='低於20MA')
                df5.to_excel(writer, sheet_name='20MA上下限內')
                df.to_excel(writer, sheet_name='原始資料')

class WorkThread(QThread):
    trigger = pyqtSignal(int)
    trigger_up = pyqtSignal(list)
    trigger_down = pyqtSignal(list)
    #計算MACD
    def macd(self,DF,a,b,c):
        df=DF.copy()
        df['MA Fast']=df['Adj Close'].ewm(span=a, min_periods=a).mean()
        df['MA Slow']=df['Adj Close'].ewm(span=b, min_periods=b).mean()
        df["MACD"]=df['MA Fast']-df['MA Slow']
        df['Signal']=df.MACD.ewm(span=c, min_periods=c).mean()
        df["Histrogram"]=df.MACD-df.Signal
        df=df.dropna()
        return df
    #計算均線
    def moving_average(self,DF,period):
        df=DF.copy()
        return df['Close'].rolling(period).mean()



    def __init__(self):
        # 初始化函数
        super(WorkThread, self).__init__()

    def run(self):
        up=[]
        down=[]
        global cleaned_data,filter_data_up20MA,filter_data_down20MA,filter_data_range20MA,filter_data_up,filter_data_down,time_end,today,up_low_price,up_high_price,up_num,up_gain,down_low_price,down_high_price,down_num,down_gain,checkBox_up_bb_flag,checkBox_down_bb_flag
        for i in range(1,len(cleaned_data)):
            try:
                open = float(cleaned_data[i][5])
                high = float(cleaned_data[i][6])
                low = float(cleaned_data[i][7])
                close = float(cleaned_data[i][8])
                red_green = cleaned_data[i][9]
                num = int(cleaned_data[i][2].replace(',', ''))
                value = float(cleaned_data[i][10])
                d_value = value/(close-value)*100

                if(num>up_num and red_green=="+" and close>=up_low_price and close<=up_high_price):
                    if d_value>up_gain:
                        equity = yf.Ticker(cleaned_data[i][0]+".TW")
                        data = equity.history(period='1y')
                        #macd_data = self.macd(data, 12,26,9)
                        #macd_data = macd_data.iloc[::-1]
                        ma_5  = float("%.2f" % self.moving_average(data,5).iloc[-1:][0])
                        ma_10 = float("%.2f" % self.moving_average(data,10).iloc[-1:][0])
                        ma_20 = float("%.2f" % self.moving_average(data,20).iloc[-1:][0])


                        sma = data['Close'].rolling(window=20).mean().dropna()
                        rstd = data['Close'].rolling(window=20).std(ddof=0).dropna()
                        upper_band = sma + 2 * rstd
                        lower_band = sma - 2 * rstd
                        bolling_up = float("%.2f" % upper_band.iloc[-1:][0])
                        bolling_down = float("%.2f" % lower_band.iloc[-1:][0])
                        print(checkBox_up_bb_flag)

                        if(ma_5>ma_10 and ma_10>ma_20):
                            if close > bolling_up:
                                up.append(cleaned_data[i][0]+"|"+cleaned_data[i][1]+"|"+str(close)+" *")
                                self.trigger_up.emit(up)
                            else:
                                up.append(cleaned_data[i][0]+"|"+cleaned_data[i][1]+"|"+str(close))
                                self.trigger_up.emit(up)
    
                            if  close>ma_20*1.15:
                                filter_data_up20MA.append(cleaned_data[i])
                            if  close<ma_20*0.85:
                                filter_data_down20MA.append(cleaned_data[i])
                            if close<ma_20*1.15 and close>ma_20*0.85:
                                filter_data_range20MA.append(cleaned_data[i])
                            filter_data_up.append(cleaned_data[i])


                if(num>down_num and red_green=="-" and close>=up_low_price and close<=up_high_price):
                    if d_value<down_gain:
                        equity = yf.Ticker(cleaned_data[i][0]+".TW")
                        data = equity.history(period='1y')
                        ma_5  = float("%.2f" % self.moving_average(data,5).iloc[-1:][0])
                        ma_10 = float("%.2f" % self.moving_average(data,10).iloc[-1:][0])
                        ma_20 = float("%.2f" % self.moving_average(data,20).iloc[-1:][0])

                        sma = data['Close'].rolling(window=20).mean().dropna()
                        rstd = data['Close'].rolling(window=20).std(ddof=0).dropna()

                        upper_band = sma + 2 * rstd
                        lower_band = sma - 2 * rstd
                        bolling_up = float("%.2f" % upper_band.iloc[-1:][0])
                        bolling_down = float("%.2f" % lower_band.iloc[-1:][0])

    

                        if(ma_5<ma_10 and ma_10<ma_20):
                            if close < bolling_down:
                                down.append(cleaned_data[i][0]+"|"+cleaned_data[i][1]+"|"+str(close)+" *")
                                self.trigger_down.emit(down)
                                
                            else:
                                down.append(cleaned_data[i][0]+"|"+cleaned_data[i][1]+"|"+str(close))
                                self.trigger_down.emit(down)
                            # 股價>20MA價格*1.15
                            # 股價<20MA價格*0.85
                            if  close>ma_20*1.15:
                                filter_data_up20MA.append(cleaned_data[i])
                            if  close<ma_20*0.85:
                                filter_data_down20MA.append(cleaned_data[i])
                            if close<ma_20*1.15 and close>ma_20*0.85:
                                filter_data_range20MA.append(cleaned_data[i])
                            filter_data_down.append(cleaned_data[i])
        
            except Exception as e:
                print(e)
            per = int(i/(len(cleaned_data)-1)*100)
            self.trigger.emit(per)


        





if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())