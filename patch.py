import tushare as ts
import pandas as pd
import numpy as np
import talib as ta
import matplotlib.pyplot as plt
import scipy.signal as signal
import scipy
from matplotlib.pyplot import MultipleLocator
from quant_macd_dif import *
from quant_macd_dif import detect_divergence
from quant_macd_dea import *
from quant_macd_histogram import *
from quant_estimate_market import *
plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
plt.rcParams['axes.unicode_minus'] = False
import sys
import time
import datetime
import csv

def patch(code, is_gold):
    ts.set_token('df295ed799578d45256a54380d7716c1653b50afe46716290c41deb4')#token需要自己在tushare网上上获得
    pro = ts.pro_api()
    today = datetime.date.today()
    begin_day = today - datetime.timedelta(days=365)
    begin_date = begin_day.strftime("%Y%m%d")
    end_date = today.strftime("%Y%m%d")
    if (is_gold):
        is_gold_cross='gold cross'
    else:
        is_gold_cross='dead cros'    
    print('code: ' + str(code) + ' detected ' + is_gold_cross +' from ' + begin_date + ', ' + 'to ' + end_date) 
    SHORT = 10  # 快速移动平均线的滑动窗口长度。
    LONG = 20  # 慢速移动平均线de 滑动窗口
    MID = 9
    df = pro.daily(ts_code=code, start_date=begin_date, end_date=end_date)
    data = pro.query('stock_basic', exchange='', list_status='L',
                      fields='ts_code,symbol,name,area,industry,list_date')
    code_name = data.loc[data['ts_code'] == code].name.values
    df2 = df.iloc[::-1]
    # 获取dif,dea,hist，它们的数据类似是tuple，且跟df2的date日期一一对应
    # 记住了dif,dea,hist前33个为Nan，所以推荐用于计算的数据量一般为你所求日期之间数据量的3倍
    # 这里计算的hist就是dif-dea,而很多证券商计算的MACD=hist*2=(dif-dea)*2
    dif, dea, hist = ta.MACD(df2['close'].astype(float).values, fastperiod=10, slowperiod=20, signalperiod=5)
    ma_60 = ta.MA(df2['close'].astype(float).values, timeperiod=60)
    ma_20 = ta.MA(df2['close'].astype(float).values, timeperiod=20)
    df3 = pd.DataFrame({'dif': dif[33:], 'dea': dea[33:], 'hist': hist[33:], 'ma60': ma_60[33:], 'ma20':ma_20[33:]},
                        index=df2['trade_date'][33:], columns=['dif', 'dea', 'hist', 'ma60', 'ma20'])
    df4 = pd.merge(df3, df2, on='trade_date', how='left')
    if (is_gold):
        cross_result = gold_death_cross().detect_gold_cross_all(df4)
    else:
        cross_result = gold_death_cross().detect_dead_cross_all(df4)
    cross_result.insert(0, code_name)
    cross_result.insert(0, code)
    return cross_result
    
if __name__ == '__main__':

    today = datetime.date.today()
    end_date = today.strftime("%Y%m%d")

    codes=[]
    with open('code_list.csv', 'r') as f2:
        reader = csv.DictReader(f2)
        for row in reader:
            codes.append(row['code'])


    with open(str(end_date)+'_gold.csv','wt') as f1:
        cw = csv.writer(f1)
        cw.writerow(['代号', '名字', '总斜率','最近一次斜率', '第一次金叉', '第二次金叉', '第三次金叉'])
        for code in codes:
            gold_cross_result = patch(code, True)
            if (gold_cross_result):
                cw.writerow(gold_cross_result)
    with open(str(end_date)+'_dead.csv','wt') as f1:
        cw = csv.writer(f1)
        cw.writerow(['代号', '名字', '总斜率','最近一次斜率', '第一次死叉', '第二次死叉', '第三次死叉'])
        for code in codes:
            dead_cross_result = patch(code, False)
            if (dead_cross_result):
                cw.writerow(dead_cross_result)            