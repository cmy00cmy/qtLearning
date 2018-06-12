#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 30 19:43:14 2018

@author: chenmengyuan
"""

import six
from abc import ABCMeta, abstractmethod
import talib
import pandas as pd

class TradeStrategyBase(six.with_metaclass(ABCMeta, object)):
    """
        交易策略抽象基类
    """

    @abstractmethod
    def buy_strategy(self, *args, **kwargs):
        # 买入策略基类
        pass

    @abstractmethod
    def sell_strategy(self, *args, **kwargs):
        # 卖出策略基类
        pass

class TradeStrategy(TradeStrategyBase):
    """
        交易策略1: macd bar>0买入，bar<0卖出
    """
    s_keep_stock_threshold = 20
    

    def __init__(self):
        self.keep_stock_day = 0
        # 7%上涨幅度作为买入策略阀值
        #self.__buy_change_threshold = 0.07
        self.__ohlcv = pd.DataFrame(columns = ('time', 'open', 'highest', 'lowest', 'close', 'volume'))

    def buy_strategy(self, trade_ind, trade_day, trade_days):
        dif, dea, bar = talib.MACD(self.__ohlcv.close, fastperiod = 12, slowperiod = 26, signalperiod = 9)
        if self.keep_stock_day == 0 and bar[trade_day.date] > 0:

            # 当没有持有股票的时候self.keep_stock_day == 0 并且
            # 符合买入条件上涨一个阀值，买入
            self.keep_stock_day += 1
        elif self.keep_stock_day > 0:
            # self.keep_stock_day > 0代表持有股票，持有股票天数递增
            self.keep_stock_day += 1

    def sell_strategy(self, trade_ind, trade_day, trade_days):
        dif, dea, bar = talib.MACD(self.__ohlcv.close, fastperiod = 12, slowperiod = 26, signalperiod = 9)
        if self.keep_stock_day > 0 and bar[trade_day.date] < 0:
            # 当持有股票天数超过阀值s_keep_stock_threshold，卖出股票
            self.keep_stock_day = 0

    """
        property属性稍后会讲到
    """
    @property
    def buy_change_threshold(self):
        return self.__buy_change_threshold

    @buy_change_threshold.setter
    def buy_change_threshold(self, buy_change_threshold):
        if not isinstance(buy_change_threshold, float):
            """
                上涨阀值需要为float类型
            """
            raise TypeError('buy_change_threshold must be float!')
        # 上涨阀值只取小数点后两位
        self.__buy_change_threshold = round(buy_change_threshold, 2)
    
    @property
    def ohlcv(self):
        return self.__ohlcv
    
    @ohlcv.setter
    def ohlcv(self, ohlcv):
        self.__ohlcv = ohlcv
        
if __name__ == '__main__':
	pass
	
	
	