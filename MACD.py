#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import talib
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ccxt
from abupy import nd

hb = ccxt.huobipro()
symbol = 'BTC/USDT'

def main():
	# data = hb.fetch_ohlcv('BTC/USDT', '1m')
	# begtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[0][0] / 1000))
	# endtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[-1][0] / 1000))
	# arr = np.array(data)
	# ohlcv = pd.DataFrame(arr ,columns = ('time', 'open', 'highest', 'lowest', 'close', 'volume'))
    hb = ccxt.huobipro()
    hb.proxies = {
            'http': 'http://127.0.0.1:8123',
            'https': 'http://127.0.0.1:8123',
            }
    data = hb.fetch_ohlcv('BTC/USDT', '1d')
    arr = np.array(data)
    ohlcv = pd.DataFrame(arr ,columns = ('time', 'open', 'highest', 'lowest', 'close', 'volume'))
    ohlcv = ohlcv.sort_index(by='time')[-100:]
	
    #从文件读取 数据跨度 2018-05-28 06:36:00   -  2018-05-28 23:15:00 
    #ohlcv = pd.read_csv('hb.csv', parse_dates = True, index_col = 0)
    #ohlcv = ohlcv[::-1]
#	timeIndex = pd.date_range('2018-05-28 06:36:00', periods = 1000, freq='1min')
    timeIndex = pd.date_range(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(ohlcv.head(1).time) / 1000)), periods = ohlcv.shape[0], freq='1d')
    ohlcv.index = timeIndex
    dif, dea, bar = talib.MACD(ohlcv.close, fastperiod = 12, slowperiod = 26, signalperiod = 9)
    plt.plot(ohlcv.index, np.where(dif > 0, dif, 0), label = 'macd dif')
    plt.plot(ohlcv.index, np.where(dea > 0, dea, 0), label = 'signal dea')
    bar_red = np.where(bar > 0, bar, 0)
    bar_green = np.where(bar < 0, bar, 0)
    plt.bar(ohlcv.index, bar_red, facecolor = 'red', label = 'hist bar')
    plt.bar(ohlcv.index, bar_green, facecolor = 'green', label = 'hist bar')
    plt.legend(loc = 'best')

    #nd.macd.plot_macd_from_klpd(ohlcv)
    #print(dif, dea, bar)

if __name__ == '__main__':
    main()
