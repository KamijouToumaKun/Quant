import akshare as ak

# 基于代码：https://zhuanlan.zhihu.com/p/1941241401863050175
# 核心：说明MACD、KDJ这些指标，无论做什么交易，都会放在分析图中最显眼的位置，但其实不大靠谱

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

OPEN_STR = r'开盘'
CLOSE_STR = r'收盘'

# b站：量化投资邢不行啊
# 测试了macd和kdj
def calc_macd(data):
    SHORT_EMA_STR = 'short_ema'
    LONG_EMA_STR = 'long_ema'
    main_line_names = [SHORT_EMA_STR, LONG_EMA_STR]

    minor_line_names = ['DIF', 'DEA']

    # 计算移动平均线，不是 .rolling(window=5).mean() 的算术平均值均线
    # 需要改成指数平均线
    # 参数：https://zhuanlan.zhihu.com/p/1912838594583827738
    # 可以把数值改成10,20,7，或者6,13,5这样
    short_window = 10
    long_window = 20
    signal_window = 7
    # 计算短期EMA
    data[SHORT_EMA_STR] = data[CLOSE_STR].ewm(span=short_window, adjust=False).mean()    
    # 计算长期EMA
    data[LONG_EMA_STR] = data[CLOSE_STR].ewm(span=long_window, adjust=False).mean()
    # 计算DIF线（MACD线）   通常大于dea，则为涨
    data['DIF'] = data[SHORT_EMA_STR] - data[LONG_EMA_STR]
    # 计算信号线（DEA）
    data['DEA'] = data['DIF'].ewm(span=signal_window, adjust=False).mean()
    # 计算MACD柱状图：二阶
    data['MACD'] = 2 * (data['DIF'] - data['DEA'])

    # 1表示金叉，-1表示死叉，0表示无信号
    # 0.还有的玩法是金叉买入，然后持有若干天卖出，不管死叉
    
    # 1.一阶信号
    data['1st Order Signal'] = np.where(data[SHORT_EMA_STR] > data[LONG_EMA_STR], 1, 0)
    data['1st Order Signal'] = np.where(data[SHORT_EMA_STR] < data[LONG_EMA_STR], -1, data['1st Order Signal'])
    data['1st Order Position'] = data['1st Order Signal'].diff()  # 信号变化位置
    # 2.二阶信号
    data['2nd Order Signal'] = np.where(data['DIF'] > data['DEA'], 1, 0)
    data['2nd Order Signal'] = np.where(data['DIF'] < data['DEA'], -1, data['2nd Order Signal'])
    data['2nd Order Position'] = data['2nd Order Signal'].diff()  # 信号变化位置
    # 3.二次金叉
    data_non_zero = data['2nd Order Signal'][data['2nd Order Signal'] != 0] # 提取非零值
    data_shifted = data_non_zero.shift(1, fill_value=0) # 上一个非零值 (第一个非零值的上一个也认为是0)
    new_non_zero_values = data_non_zero + data_shifted # 计算新值：让每个非零位置加上上一个非零位置的值
    data['2nd Order Double Signal'] = 0 # 创建一个全零的系列作为基础
    data['2nd Order Double Signal'][data['2nd Order Signal'] != 0] = new_non_zero_values # 用新计算出的非零值填充到原序列中的非零位置
    data['2nd Order Double Signal'] = np.where( # 再将-2～2的信号归一化到-1～1
        (data['2nd Order Double Signal'] > -2) & (data['2nd Order Double Signal'] < 2), 0, data['2nd Order Double Signal']
    ) # 其实更简单的方法是，除以2后向零取整
    data['2nd Order Double Signal'][data['2nd Order Double Signal'] == 2] = 1 # 连续两个金叉才买入
    data['2nd Order Double Signal'][data['2nd Order Double Signal'] == -2] = -1 # 连续两个死叉则卖出

    # TODO：https://baijiahao.baidu.com/s?id=1836453727364164671&wfr=spider&for=pc
    # 则认为零轴上方第二个金叉反而不如第一个金叉
    # 考虑的是：艾略特波浪理论，市场走势不断重复一种由5个上升浪（驱动浪）和3个下跌浪（调整浪）组成的周期性模式，且浪与浪之间存在斐波拉契比率关系。

    # 4.结合位置更好：零上金叉才买入，零下死叉才卖出，其他都不动
    data['1st&2nd Order Signal'] = np.where(
        (data[SHORT_EMA_STR] > data[LONG_EMA_STR]) & (data['2nd Order Signal'] == 1), 1, 0
    )
    data['1st&2nd Order Signal'] = np.where(
        (data[SHORT_EMA_STR] < data[LONG_EMA_STR]) & (data['2nd Order Signal'] == -1), -1, data['1st&2nd Order Signal']
    )
    data['1st&2nd Order Position'] = data['1st&2nd Order Signal'].diff()  # 信号变化位置
    # https://zhuanlan.zhihu.com/p/1941241401863050175
    # 这里也是回测后发现：在可转债中，零上金叉效果还不如零下金叉

    # 5. 背离 TODO
    # 看B站视频

    # 6. 三度背离 TODO
    # https://zhuanlan.zhihu.com/p/557132192
    # 这篇文章也是认为：背离的应用放在大盘指数上判断，可信度高一点。个股则不灵

    # TODO：组合，所谓的金叉共振
    # https://zhuanlan.zhihu.com/p/1985715008047440681
    # 这里提到：
    # 单独使用时，MACD 胜率不足 50%，KDJ 低至 47%，而 RSI 可达 68.3%；（有这么高吗？？？）
    # 但通过多指标组合可将胜率从 50% 提升至 78% 以上。形态识别中，头肩顶形态成功率达 81%-89%，显示出较高的可靠性。

    return data, main_line_names, minor_line_names

def calc_kdj(data, n=9, m1=3, m2=3): # 经典参数组合9，3，3
    main_line_names = []
    minor_line_names = ['K', 'D', 'J']

    LOW_STR = '最低'
    HIGH_STR = '最高'

    low_min = data[LOW_STR].rolling(n).min()
    high_max = data[HIGH_STR].rolling(n).max()
    # 还可以使用rolling().mean()计算均线，np.where()对比均线位置以识别交叉点
    rsv = (data[CLOSE_STR] - low_min) / (high_max - low_min) * 100
    
    data['K'] = rsv.ewm(alpha=1/m1).mean()
    data['D'] = data['K'].ewm(alpha=1/m2).mean()
    data['J'] = 3 * data['K'] - 2 * data['D']

    # 1.一阶信号
    data['1st Order Signal'] = np.where(data['K'] > data['D'], 1, 0)
    data['1st Order Signal'] = np.where(data['K'] < data['D'], -1, data['1st Order Signal'])
    data['1st Order Position'] = data['1st Order Signal'].diff()  # 信号变化位置

    # 4.结合位置更好：低位金叉才买入，高位死叉才卖出，其他都不动
    # 就算只看D线，这个的信号也非常稀疏，基本没有买入和卖出
    # 如果要求KDJ三线都在低位或高位，就更稀疏了
    data['0th&1st Order Signal'] = np.where(
        (data['D'] < 20) & (data['1st Order Signal'] == 1), 1, 0
    )
    data['0th&1st Order Signal'] = np.where(
        (data['D'] > 80) & (data['1st Order Signal'] == -1), -1, data['0th&1st Order Signal']
    )
    data['0th&1st Order Position'] = data['0th&1st Order Signal'].diff()  # 信号变化位置
    return data, main_line_names, minor_line_names

def backtest(data, signal_type, initial_capital=10000):
    df = data.copy()
    """执行回测"""
    df['Position'] = 0  # 持仓状态
    df['Holdings'] = 0  # 持仓市值
    df['Cash'] = initial_capital  # 现金余额
    df['Total'] = initial_capital  # 总资产
    
    # 1. 考虑的是日线的MACD
    # 2. 采用最基础的策略，假设持仓只能为0或1；每次也只买卖一股
    # 茅台从330一直到700
    # 结果：一直操作买卖，就算不算交易成本，总资产也只赚了约320元，220元，320元，甚至跑输了买入持有：一直拿着一股
    # 按照b站上视频的说法，招商银行也是这样
    # 而且，跟随机抛硬币的概率差不多

    position = 0
    for i in range(1, len(df)):
        # 金叉买入
        if df.iloc[i][signal_type + ' Signal'] == 1 and position == 0:
            position = 1
            df.iloc[i, df.columns.get_loc('Position')] = position
            df.iloc[i, df.columns.get_loc('Holdings')] = position * df.iloc[i][CLOSE_STR]
            # df.iloc[i, df.columns.get_loc('Cash')] = df.iloc[i-1]['Cash'] - df.iloc[i][CLOSE_STR]
            # TODO：还需要计算交易成本
            # TODO：信号比较稀疏，暂时不考虑T+1的问题
            # 这里我进行了修改：当头天确认是金叉之后才买入，此时价格只能是第二天的开盘价了
            if i < len(df) - 1:
                df.iloc[i, df.columns.get_loc('Cash')] = df.iloc[i-1]['Cash'] - df.iloc[i+1][OPEN_STR]
            else:
                df.iloc[i, df.columns.get_loc('Cash')] = df.iloc[i-1]['Cash'] - df.iloc[i][CLOSE_STR]
        
        # 死叉卖出
        elif df.iloc[i][signal_type + ' Signal'] == -1 and position == 1:
            position = 0
            df.iloc[i, df.columns.get_loc('Position')] = position
            df.iloc[i, df.columns.get_loc('Holdings')] = 0
            # df.iloc[i, df.columns.get_loc('Cash')] = df.iloc[i-1]['Cash'] + df.iloc[i][CLOSE_STR]
            if i < len(df) - 1:
                df.iloc[i, df.columns.get_loc('Cash')] = df.iloc[i-1]['Cash'] + df.iloc[i+1][OPEN_STR]
            else:
                df.iloc[i, df.columns.get_loc('Cash')] = df.iloc[i-1]['Cash'] + df.iloc[i][CLOSE_STR]
            # TODO：还需要计算交易成本
            # TODO：信号比较稀疏，暂时不考虑T+1的问题
            # 这里我进行了修改：当头天确认是死叉之后才买入，此时价格只能是第二天的开盘价了
        
        # 持仓不变
        else:
            df.iloc[i, df.columns.get_loc('Position')] = position
            df.iloc[i, df.columns.get_loc('Holdings')] = position * df.iloc[i][CLOSE_STR]
            df.iloc[i, df.columns.get_loc('Cash')] = df.iloc[i-1]['Cash']
        
        df.iloc[i, df.columns.get_loc('Total')] = df.iloc[i]['Cash'] + df.iloc[i]['Holdings']

    # TODO：还可以计算胜率（低买高卖的次数占总次数的比例）
    # 和盈亏比：公式为：盈亏比 = 平均盈利金额 ÷ 平均亏损金额（通常以 N:1 表示）。
    # 例如 6 次盈利共 20 万，4 次亏损共 3 万，平均盈利 3.33 万，平均亏损 0.75 万，盈亏比即为 4.44:1。
    # 胜率低于50%不一定有问题，只要盈亏比高，那么就能亏小钱赚大钱
    # 但问题是，MACD、KDJ的执行一般都是对称的，金叉死叉一样多，盈亏比也是1:1
    # 推荐趋势交易的书

    return df

def visualize(df, signal_type, main_line_names, minor_line_names):
    plt.figure(figsize=(14, 7))

    plt.subplot(3, 1, 1)
    plt.plot(df[CLOSE_STR], label=CLOSE_STR, alpha=0.5)
    for main_line_name in main_line_names:
        plt.plot(df[main_line_name], label=main_line_name)
    # 标记金叉和死叉
    plt.plot(df[df[signal_type + ' Signal'] == 1].index, df[CLOSE_STR][df[signal_type + ' Signal'] == 1],
        '^', markersize=10, color='green', alpha=0.3, label=signal_type + ' Signal' + ' Gold Cross')
    plt.plot(df[df[signal_type + ' Signal'] == -1].index, df[CLOSE_STR][df[signal_type + ' Signal'] == -1],
        'v', markersize=10, color='red', alpha=0.3, label=signal_type + ' Signal' + ' Death Cross')
    plt.title(signal_type + ' Price with Buy/Sell Signals')
    plt.legend()

    plt.subplot(3, 1, 2)
    for minor_line_name in minor_line_names:
        plt.plot(df[minor_line_name], label=minor_line_name)
    # plt.bar(df.index, df['MACD'], color=np.where(df['MACD'] > 0, 'green', 'red'), alpha=0.3)
    # plt.title(signal_type + ' MACD Indicator') # TODO: 仅限于MACD二阶的指标，在这里显示有意义
    plt.legend()

    plt.subplot(3, 1, 3)
    plt.plot(df.index, df['Total'], label='Portfolio Value', color='purple')
    plt.title(signal_type + ' Portfolio Performance')
    plt.legend()

    plt.show()

if __name__ == '__main__':
    # ticker = ["000001"] # 上证指数为什么开盘是 9块多？
    ticker = ["399300"] # 沪深300: 399300（深市）和000300（沪市）
    # "AAPL"
    # ticker = ["600519"] # 贵州茅台
    # ticker = ["600036"] # 招商银行
    # ticker = ["600338"] # 西藏珠峰：妖股
    data = ak.stock_zh_a_hist(
        symbol=ticker[0],
        period="daily",
        start_date="20170101",
        end_date="20241231", # 周期拉长则需要考虑分红了
        adjust="hfq"
    )
    # 复权处理需手动指定参数，例如在获取A股数据时使用adjust参数：
    # adjust=""（空字符串）返回未复权数据；
    # adjust="qfq"获取前复权数据；
    # adjust="hfq"获取后复权数据。
    # 未复权数据，遇到分红等该怎么办？
    # 

    # https://zhuanlan.zhihu.com/p/1973769828771862363
    # yfinance库返回的历史价格数据中的收盘价（Close）是默认经过复权处理的，
    # 即它对应于雅虎财经网页上显示的“调整后收盘价”（Adj Close）
    # 和大部分券商一样，采用的是前复权
    # 如果需要原始价格（未复权）或验证复权效果，可以显式设置参数 auto_adjust=False
    # 此时数据中的 Close 列将为未复权价格，而 Adj Close 列则包含复权后的价格。
    
    macd_data, main_line_names, minor_line_names = calc_macd(data)
    for signal_type in ['1st Order', '2nd Order', '2nd Order Double', '1st&2nd Order']:
        macd_df = backtest(macd_data, signal_type)
        visualize(macd_df, signal_type, main_line_names, minor_line_names)

    kdj_data, main_line_names, minor_line_names = calc_kdj(data)
    for signal_type in ['1st Order', '0th&1st Order']:
        kdj_df = backtest(kdj_data, signal_type)
        visualize(kdj_df, signal_type, main_line_names, minor_line_names)