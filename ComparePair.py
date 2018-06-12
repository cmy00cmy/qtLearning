#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 21:11:55 2018

@author: chenmengyuan
"""

import TradeLoopBack as tlp
import StockTradeDays as stc
#import TradeStrategy as ts
import TS_MACD as ts
import pandas as pd
from abupy import six, xrange, range, reduce, map, filter, partial
import matplotlib.pyplot as plt
import matplotlib.finance as mpf
import numpy as np
import talib
import time
import ccxt
import itertools

hb = ccxt.huobipro()
hb.proxies = {
        'http': 'http://127.0.0.1:8123',
        'https': 'http://127.0.0.1:8123',
        }

def loopBack(symbol, interval):

    buy = sell =1
    fee = 0.002
    #TODO：获取相同时间区间内的数据
    data = hb.fetch_ohlcv(symbol, interval)
    arr = np.array(data)
    ohlcv = pd.DataFrame(arr ,columns = ('time', 'open', 'highest', 'lowest', 'close', 'volume'))
    ohlcv = ohlcv.sort_index(by='time')
    timeIndex = pd.date_range(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(ohlcv.head(1).time) / 1000)), periods = ohlcv.shape[0], freq=(lambda x:x+'in' if x[-1] == 'm' else x)(interval))
    ohlcv.index = timeIndex
    dif, dea, bar = talib.MACD(ohlcv.close, fastperiod = 12, slowperiod = 26, signalperiod = 9)
    
    #找出交易日
    bar2 = bar * bar.shift(1)
    the_day = np.where(bar2 < 0, bar2, 0)
    
    trade_days = stc.StockTradeDays(ohlcv.close, timeIndex[0], timeIndex)
    trade_strategy1 = ts.TradeStrategy()
    trade_strategy1.ohlcv = ohlcv
    trade_loop_back = tlp.TradeLoopBack(trade_days, trade_strategy1)
    trade_loop_back.execute_trade()
    #买卖操作时间节点
    pdays = pd.DataFrame(trade_loop_back.days_array, columns = ('date', 'stock'))
    #除去第一个值 0-nan ！= 0
    totalFee = 1 - np.power(1 - fee, len(np.where((pdays.stock - pdays.shift(1).stock) != 0 )[0]) - 1)
    #print(symbol, interval)
#    print('总手续费：{}%'.format(totalFee))
#    print('回测策略1 总盈亏为：{}%'.format((reduce(lambda a, b: a + b, trade_loop_back.profit_array)) * 100))
    profit = -99
    if len(trade_loop_back.profit_array) > 0:
        profit = (reduce(lambda a, b: a + b, trade_loop_back.profit_array)) * 100
    return totalFee, profit, ohlcv.shape[0]

def getOHLCV(symbol, interval, since, to):
    data = []
    since = int(time.mktime(time.strptime(since, '%Y-%m-%d %H:%M:%S'))) * 1000
    if not to:
        to = int(time.time() * 1000)
    else:
        to = int(time.mktime(time.strptime(to, '%Y-%m-%d %H:%M:%S'))) * 1000
    while 1:    
        temp = hb.fetch_ohlcv(symbol, interval, since = since)
        data += temp
        if data[0][0] > to:
            break
        since = data[0][0] + (data[0][0] - data[1][0])
    return data
    
    
def main():
    #pair = ['BTC/USDT', 'IOTA/BTC', 'ADA/BTC', 'ETC/BTC', 'ETH/BTC', 'LTC/BTC']
    pair = ['ADA/BTC', 'ETH/BTC']
    interval = ['1m', '1d']
    startTime = '2018-01-01 00:00:00'
    res = []
    for p, i in itertools.product(pair, interval):
        fee, profit, num = loopBack(p, i)
        res.append([p, i, fee, profit, num])
    res = pd.DataFrame(res, columns=('pair', 'interval', 'fee', 'profit', 'dataLen'))
    
    print(res.sort_index(by='profit', ascending=False)[res.dataLen > 100])

if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print(end - start)
#    data = getOHLCV('BTC/USDT', '1m', '2018-02-01 00:00:00', '2018-06-01 00:00:00')
#    print(len(data))
#    print(data)
