#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import TradeLoopBack as tlp
import StockTradeDays as stc
#import TradeStrategy as ts
import TS_MACD as ts
import pandas as pd
from abupy import reduce
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
buy = sell =1
fee = 0.002

def main():
    symbols = ['IOTA/BTC']
    intervals = ['30m','1h']
    res = []
    for symbol, interval in itertools.product(symbols, intervals):
        ohlcv = fetchData(symbol, interval)
        res += [loopBack(ohlcv) + [symbol, interval]]
    res_df = pd.DataFrame(res ,columns = ('totalFee', 'profit', 'dataLen', 'symbol', 'interval'))
    res_df = res_df.sort_index(by='profit', ascending=False)
    print(res_df)

def fetchData(symbol, interval):
    
    data = hb.fetch_ohlcv(symbol, interval)
    arr = np.array(data)
    ohlcv = pd.DataFrame(arr ,columns = ('time', 'open', 'highest', 'lowest', 'close', 'volume'))
    ohlcv = ohlcv.sort_index(by='time')
    timeIndex = pd.date_range(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(ohlcv.head(1).time) / 1000)), periods = ohlcv.shape[0], freq=(lambda x:x+'in' if x[-1] == 'm' else x)(interval))
    ohlcv.index = timeIndex
    print(ohlcv.shape)
    return ohlcv

def loopBack(ohlcv):
    dif, dea, bar = talib.MACD(ohlcv.close, fastperiod = 12, slowperiod = 26, signalperiod = 9)
    macd = {'dif':dif, 'dea': dea, 'bar':bar}
    
    #找出交易日
    bar2 = bar * bar.shift(1)
    the_day = np.where(bar2 < 0, bar2, 0)
    timeIndex = ohlcv.index
    trade_days = stc.StockTradeDays(ohlcv.close, timeIndex[0], timeIndex)
    trade_strategy1 = ts.TradeStrategy()
    trade_strategy1.ohlcv = ohlcv
    trade_loop_back = tlp.TradeLoopBack(trade_days, trade_strategy1)
    trade_loop_back.execute_trade()
    #买卖操作时间节点
    pdays = pd.DataFrame(trade_loop_back.days_array, columns = ('date', 'stock'))
    #除去第一个值 0-nan ！= 0
    totalFee = 1 - np.power(1 - fee, len(np.where((pdays.stock - pdays.shift(1).stock) != 0 )[0]) - 1)
    print('总手续费：{}%'.format(totalFee))
    profit = -99
    if len(trade_loop_back.profit_array) > 0:
        profit = (reduce(lambda a, b: a + b, trade_loop_back.profit_array)) * 100
    print('回测策略1 总盈亏为：{}%'.format(profit))
    drawData(ohlcv, macd, trade_loop_back,pdays)
    return [totalFee, profit, ohlcv.shape[0]]

def drawData(ohlcv, macd, trade_loop_back, pdays):
    dif = macd['dif']
    dea = macd['dea']
    bar = macd['bar']
    fig, axs = plt.subplots(nrows = 3, ncols = 1, facecolor=(0.5, 0.5, 0.5), figsize=(14,7))
    draw1, draw2, draw3 = axs.ravel()
    # 可视化profit_array
    draw1.plot(np.array(trade_loop_back.profit_array).cumsum(), label = 'profit_array');
#    #print(trade_loop_back.days_array)
#    
    #可视化K线和交易日
    qutotes = []
    for index, (d, o, c, h, l) in enumerate(zip(ohlcv.index, ohlcv.open, ohlcv.close, ohlcv.highest, ohlcv.lowest)):
        d = mpf.date2num(d)
        val = (d, o, c, h, l)
        qutotes.append(val)
    mpf.candlestick_ochl(draw2, qutotes, width=0.4, colorup="green", colordown="red")
    #draw2.autoscale_view()
    #draw2.xaxis_date()
    act = pdays[(pdays.stock - pdays.shift(1).stock) != 0]
#    draw2.axvline(np.array([736875, 736876]), label = 'buy', color="green")
#    for index, line in act[act.stock == 1].date:
#        draw2.axvline(qutotes[index][0], label = 'buy', color="green")
#    for index, line in act[act.stock == 0].date:
#        draw2.axvline(qutotes[index][0], label = 'sell', color="red")
#    draw2.axvline(np.float32(act[act.stock == 1].date), label = 'buy', color="green")
#    draw2.axvline(np.float32(act[act.stock == 0].date), label = 'sell', color="red")
    
    draw3.plot(ohlcv.index, dif, label = 'macd dif')
    draw3.plot(ohlcv.index, dea, label = 'signal dea')
    bar_red = np.where(bar > 0, bar, 0)
    bar_green = np.where(bar < 0, bar, 0)
    draw3.bar(ohlcv.index, bar_red, facecolor = 'red', label = 'hist bar')
    draw3.bar(ohlcv.index, bar_green, facecolor = 'green', label = 'hist bar')
    draw3.legend(loc = 'best')
    plt.show()
	
if __name__ == '__main__':
    main()
