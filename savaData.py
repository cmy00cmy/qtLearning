#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 31 18:27:37 2018

@author: chenmengyuan
"""

import numpy as np
import pandas as pd
import ccxt

hb = ccxt.huobipro()

hb.proxies = {
        'http': 'http://127.0.0.1:8123',
        'https': 'http://127.0.0.1:8123',
        }
data = hb.fetch_ohlcv('BTC/USDT', '1h')
arr = np.array(data)
ohlcv = pd.DataFrame(arr ,columns = ('time', 'open', 'highest', 'lowest', 'close', 'volume'))

ohlcv.to_csv('huobipro_20185311830_1h.csv', columns=ohlcv.columns, index=False)