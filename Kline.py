#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  2 13:11:59 2018

@author: chenmengyuan
"""

import pandas as pd
from abupy import six, xrange, range, reduce, map, filter, partial
import matplotlib.pyplot as plt
import matplotlib.finance as mpf
import numpy as np
import talib
import time
import ccxt

def main():
    hb = ccxt.huobipro()
    hb.proxies = {
            'http': 'http://127.0.0.1:8123',
            'https': 'http://127.0.0.1:8123',
            }
    data = hb.fetch_ohlcv('BTC/USDT', '15m')
    arr = np.array(data)
    ohlcv = pd.DataFrame(arr ,columns = ('time', 'open', 'highest', 'lowest', 'close', 'volume'))
    ohlcv = ohlcv.sort_index(by='time')
    timeIndex = pd.date_range(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(ohlcv.head(1).time) / 1000)), periods = ohlcv.shape[0], freq='15m')
    ohlcv.index = timeIndex
    dif, dea, bar = talib.MACD(ohlcv.close, fastperiod = 12, slowperiod = 26, signalperiod = 9)
    
    fig, axs = plt.subplots(figsize=(14,7))
    
    #可视化K线和交易日
    qutotes = []
    for index, (d, o, c, h, l) in enumerate(zip(ohlcv.index, ohlcv.open, ohlcv.close, ohlcv.highest, ohlcv.lowest)):
        print(d)
        d = mpf.date2num(d)
        print(d)
        val = (d, o, c, h, l)
        qutotes.append(val)
    mpf.candlestick_ochl(axs, qutotes, width=1, colorup="green", colordown="red")
    print(qutotes)
    axs.autoscale_view()
    #axs.xaxis_date()#仅日线时使用
    
    plt.show()
	
if __name__ == '__main__':
    main()
