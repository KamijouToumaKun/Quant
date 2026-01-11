# 用Python的三个 “神器”——yfinance(数据获取)、Pandas(数据处理)、Matplotlib(可视化),就能从零搭建一套量化交易系统

# MACD，全名是moving average convergence/divergence，中文简称平滑异同移动平均线，或移动平均聚散指标，或指数平滑移动平均线。

import yfinance as yf # 需要降级，不然python3.9都import不进来

# 解决request 429的问题
# 方法1、
# import os
# proxy = 'http://127.0.0.1:7897' # 代理设置，此处修改
# os.environ['HTTP_PROXY'] = proxy 
# os.environ['HTTPS_PROXY'] = proxy

# 方法2、
YAHOOPROXY = 'http://127.0.0.1:5644'
yf.set_config(proxy=YAHOOPROXY) # 0.2.50版本都没有这个函数

# 还是下载不下来

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# yf.clear_cache()

# 下载历史数据
ticker = ["AAPL"] # ["002594.SZ"]  # 比亚迪股票代码
data = yf.download(ticker, start="2023-01-01", end="2024-01-01")

# 返回：<Response [429]>
# 原因解释：https://baijiahao.baidu.com/s?id=1835032322059725574&wfr=spider&for=pc

CLOSE_STR = 'Close'
MA5_STR = 'MA5'
MA20_STR = 'MA20'

# 计算移动平均线
# 这里使用rolling().mean()计算均线，np.where()对比均线位置以识别交叉点
data[MA5_STR] = data[CLOSE_STR].rolling(window=5).mean()  # 短期均线
data[MA20_STR] = data[CLOSE_STR].rolling(window=20).mean()  # 长期均线

# 生成信号：1表示金叉，-1表示死叉，0表示无信号
data['Signal'] = np.where(data[MA5_STR] > data[MA20_STR], 1, 0)
data['Signal'] = np.where(data[MA5_STR] < data[MA20_STR], -1, data['Signal'])
data['Position'] = data['Signal'].diff()  # 信号变化位置

plt.figure(figsize=(14, 7))
plt.plot(data[CLOSE_STR], label='Close Price', alpha=0.5)
plt.plot(data[MA5_STR], label=MA5_STR, color='blue')
plt.plot(data[MA20_STR], label=MA20_STR, color='orange')
# 标记金叉和死叉
plt.plot(data[data['Position'] == 1].index, data[MA5_STR][data['Position'] == 1], '^', markersize=10, color='green', lw=0, label='Gold Cross')
plt.plot(data[data['Position'] == -1].index, data[MA5_STR][data['Position'] == -1], 'v', markersize=10, color='red', lw=0, label='Death Cross')
plt.legend()
plt.title(f'{ticker} Gold Cross and Death Cross')
plt.show()