import backtrader as bt

def downcast(amount, lot):
    return abs(amount // lot * lot)
# downcast函数通过整数除法将订单数量向下舍入到最接近的合约单位倍数
# 其中，amount为原始订单数量（可正负，正数代表买入，负数代表卖出），lot为合约单位（如100股）。
# 该函数确保输出数量始终为lot的整数倍，且符号与输入一致。
# 例如，downcast(418, 100)返回400（即4手），downcast(-418, 100)返回-400。

# 1. 策略类定义
# 基类code: https://zhuanlan.zhihu.com/p/6214432946
class BaseStrategy(bt.Strategy):
    def __init__(self):
        # 可配置参数
        self.params = dict(
            printlog = True  # 打印交易日志，可以修改
        )

        self.start_cash = self.broker.get_cash()
        self.order = None
        self.buyprice = None
        self.buycomm = None

    def stop(self):
        # 输出回测结果
        print(f"初始资金: {self.start_cash:.2f}")
        port_value = self.broker.getvalue()
        print(f"最终资金: {port_value:.2f}")
        pnl = port_value - self.start_cash
        print(f"净收益: {pnl:.2f}")
        roi = pnl / self.start_cash
        print('ROI: {:.2f}%'.format(100.0 * roi))

        # 可视化
        # cerebro.plot(iplot=False,
        #     style="line", # 绘制线型价格走势，可改为"candelstick" 样式
        #     lcolors=colors,
        #     plotdist=0.1,
        #     bartrans=0.2,
        #     volup="#ff9896",
        #     voldown="#98df8a",
        #     loc="#5f5a41",
        #     grid=False
        # ) # 删除水平网格

    def log(self, text, dt=None, doprint=False):
        if self.params["printlog"] or doprint:
            # self.datas[0] 就是 self.data 在只加载单只股票时可以用，下同
            dt = dt or self.data.datetime.date(0)
            print('%s, %s' % (dt.isoformat(), text))

    def notify_order(self, order):
        # order可以看订单状态
        if order.status in [order.Submitted, order.Accepted]:
            return # 如订单已被处理：提交或接受了，则不用做任何事情
        elif order.status in [order.Completed]:
            if order.isbuy(): # 是买入
                self.log(
                    '买入 价格:%.2f, 金额:%.2f, 手续费:%.2f' %
                    (order.executed.price,
                    order.executed.value,
                    order.executed.comm)
                )

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                self.bar_executed_close = self.data.close[0]
            # else: 
            elif order.issell(): # 是卖出
                self.log(
                    '卖出 价格:%.2f, 金额:%.2f, 手续费:%.2f' %
                    (order.executed.price,
                    order.executed.value,
                    order.executed.comm)                   
                )

            self.bar_executed = len(self) # 记录当前交易数量
        elif order.status in [order.Canceled, order.Margin, order.Rejected]: # 订单因为缺少资金之类的原因被拒绝执行
            self.log('取消订单/合并订单:保证金不足/拒绝订单')

        # 订单状态处理完成，设为空
        self.order = None

    def notify_trade(self, trade):
        # notify_trade() 是策略类（Strategy）中的一个回调方法
        # 当交易状态发生变化时由系统自动触发，用于接收和处理交易事件，如开仓、更新或平仓。
        # 包括：
        # 开仓：当订单导致仓位从0变为非零（正值或负值）时触发，表示新交易打开。
        # 平仓：当订单使仓位从非零变为0时触发，表示交易关闭。
        # 更新：在交易期间，若仓位变化但未关闭（如加仓或减仓），可能触发更新事件。

        # https://zhuanlan.zhihu.com/p/299630905
        # 在我们一般买卖股票时，只涉及向券商发订单，并无交易（trade）的概念。
        # 并不是下一个买单，就是一个交易，下一个卖单，又代表另一个交易。交易的概念实际是用户方的概念。

        # 第一次下买单买100股，此订单执行时，仓位从0变为正值（100），系统打开一个交易，会触发notify_trade方法，在notify_trade中检查交易状态status，为1 open。
        # 然后下第二张买单100股，订单执行时不会触发notify_trade，仓位变为200。
        # 然后下卖单卖100股，仍然不会触发notify_trade，仓位变为100。
        # 再下一个卖单卖100股，执行时，仓位从100变为0，关闭交易，触发notify_trade，交易状态为2 close。
        if not trade.isclosed: # 表示已平仓
            return

        # 显示交易的毛利率和净利润
        self.log("交易中 毛利%.2f, 净利 %.2f, 手续费 %.2f" %
            (trade.pnl, trade.pnlcomm, trade.commission))

class MACDStrategy(BaseStrategy):
    lines = ('signal',)
    def __init__(self):
        super().__init__()
        self.params.update(
            dict(
                p_fast = 5,     # 短周期：5日
                p_slow = 10,    # 长周期：10日
                p_dif = 7,      # dif -> dea 周期：7日
            )
        )
        # 原参数为 12, 26, 9
        # self.order_type = '1st&2nd order' # 可以修改
        self.order_type = '0th order'

        # 初始化指标，比如简单均线
        # self.ma_fast = bt.ind.SMA(self.data.close, period=self.params["p_fast"]) # 全称 bt.indicators.SimpleMovingAverage
        # self.ma_slow = bt.ind.SMA(self.data.close, period=self.params["p_slow"]) # 全称 bt.indicators.SimpleMovingAverage
        # 可以没有第一个参数，则默认是收盘价？
        # 改成指数均线
        self.ma_fast = bt.ind.EMA(self.data.close, period=self.params["p_fast"]) # 全称 bt.indicators.ExponentialMovingAverage
        self.ma_slow = bt.ind.EMA(self.data.close, period=self.params["p_slow"]) # 全称 bt.indicators.ExponentialMovingAverage
        self.dif = self.ma_fast - self.ma_slow # DIF = EMA_fast - EMA_slow
        self.dea = bt.ind.EMA(self.dif, period=self.params["p_dif"]) # 全称 bt.indicators.ExponentialMovingAverage
        self.macdhis = self.dif - self.dea

    def next(self):
        # 如果还有订单在执行中，就不做新的仓位调整
        if self.order:
            return

        # buy 和 sell 的默认参数
        # 当size=None时，系统会通过策略的Sizer机制自动确定实际委托数量；
        # 如果策略未显式设置Sizer，Backtrader会应用默认的SizerFix，其固定委托数量（stake）为1单位。
        
        # 更简单的方法
        # self.order_target_percent(target=...) 按持仓百分比下单，“多退少补”原则，
        # 对于股票当前无持仓或持有的是多单（size>=0）的情况，
        # 若目标占比 target > 当前持仓占比，买入不够的部分；若目标占比 target < 当前持仓占比，卖出多余的部分。
        # self.close() 表示平仓，也可以加上具体的参数，但默认是完全平仓

        # 买卖一手
        # buy_size = sell_size = 100
        
        # 买卖全仓
        commission_info = self.broker.getcommissioninfo(self.data)
        cash = self.broker.get_cash() - commission_info.getsize(1, self.data.close[0])
        buy_size = cash / self.data.close[0]
        buy_size = int(buy_size * 0.95)
        buy_size = downcast(buy_size, 100)
        # 不打折扣的话，可能买入不进来：因为实际操作是第二天开盘才做，可能跳空高开：
        # https://zhuanlan.zhihu.com/p/1896245068052034669

        sell_size = self.position.size

        # https://blog.csdn.net/weixin_52071682/article/details/116903559
        # self.dataclose[0] # 当日的收盘价
        # self.dataclose[-1] # 昨天的收盘价
        # self.dataclose[-2] # 前天的收盘价
        # 这一点我在一开始使用的时候也被作者的逻辑震惊了，原来还能这么设置   

        if not self.position: # 没有持仓才买入
            # 零阶逻辑：价格上穿均线买入，下穿卖出
            if self.order_type == '0th order':
                if self.data.close[-1] < self.ma_slow[-1] and self.data.close[0] > self.ma_slow[0]:
                    self.order = self.buy(size=buy_size)
            # 一阶逻辑：MA_fast 上穿 MA_slow 买入，下穿卖出（也就是双均线策略）
            elif self.order_type == '1st order':
                if self.ma_fast[-1] < self.ma_slow[-1] and self.ma_fast[0] > self.ma_slow[0]:
                    self.order = self.buy(size=buy_size)
            # 二阶逻辑：DIF上穿DEA买入，下穿卖出
            elif self.order_type == '2nd order':
                if self.dif[-1] < self.dea[-1] and self.dif[0] > self.dea[0]:
                    self.order = self.buy(size=buy_size)
            # 一阶+二阶：零上DIF上穿DEA买入，零下DIF下穿DEA卖出
            elif self.order_type == '1st&2nd order':
                if self.ma_fast[0] > self.ma_slow[0] and self.dif[-1] < self.dea[-1] and self.dif[0] > self.dea[0]:
                    self.order = self.buy(size=buy_size)
        else: # 有持仓才卖出
            # 零阶逻辑：价格上穿均线买入，下穿卖出
            if self.order_type == '0th order':
                if self.data.close[-1] > self.ma_slow[-1] and self.data.close[0] < self.ma_slow[0]:
                    self.order = self.sell(size=sell_size)
            # 一阶逻辑：MA_fast 上穿 MA_slow 买入，下穿卖出
            elif self.order_type == '1st order':
                if self.ma_fast[-1] > self.ma_slow[-1] and self.ma_fast[0] < self.ma_slow[0]:
                    self.order = self.sell(size=sell_size)
            # 二阶逻辑：DIF上穿DEA买入，下穿卖出
            elif self.order_type == '2nd order':
                if self.dif[-1] > self.dea[-1] and self.dif[0] < self.dea[0]:
                    self.order = self.sell(size=sell_size)
            # 一阶+二阶：零上DIF上穿DEA买入，零下DIF下穿DEA卖出
            elif self.order_type == '1st&2nd order':
                if self.ma_fast[0] < self.ma_slow[0] and self.dif[-1] > self.dea[-1] and self.dif[0] < self.dea[0]:
                    self.order = self.sell(size=sell_size)
        
        # 还可以直接如下写，但我这么写发现会报错：
        # self.crossover_2nd = bt.ind.CrossOver(self.dif, self.dea)  # 穿越信号，直接调用，没有下标索引了
        # self.signal_1st = self.dif # 此时再调用 self.ma_fast - self.ma_slow 算出来就是一个数字？奇怪
        # # 下面调用 self.crossover_2nd > 0 这种写法报错：
        # # TypeError: __bool__ should return bool, returned LineOwnOperation
        # if not self.position: # 没有持仓才买入
        #     if self.signal_1st[0] > 0 and self.crossover_2nd > 0:  # 向上穿
        #         self.order = self.buy(size=buy_size)
        # else:
        #     if self.signal_1st[0] < 0 and self.crossover_2nd < 0:  # 向下穿
        #         self.order = self.sell(size=sell_size)

# self.lines.signal = bt.ind.CrossOver(self.dif, self.dea)
# https://zhuanlan.zhihu.com/p/6214432946
# 还可以写一个类，继承 bt.Indicator
# # 买入、卖出信号
# ## 买入信号
# self.buy_signal = bt.And(self.signal_1st > 0, self.crossover_2nd > 0)
# ## 卖出信号
# self.sell_signal = bt.And(self.signal_1st < 0, self.crossover_2nd < 0)
# self.lines = {
#     "signal": bt.Sum(self.buy_signal,self.sell_signal)
# }
# 添加交易信号
# cerebro.add_signal(bt.SIGNAL_LONG, MACDSignal)

import math
class BuyAndHoldStrategy(BaseStrategy):
    def __init__(self):
        super().__init__()

    def next(self):
        # 如果还有订单在执行中，就不做新的仓位调整
        if self.order:
            return

        if not self.position:
            init_price = self.data.open[0]
            # 默认情况下， buy()和sell()不带参数时等同于 exectype=bt.Order.Market
            # 表示以 下一个Bar的开盘价 成交
            self.buy(size=math.floor(start_cash / init_price))
            # 其他订单类型包括：
            # 市价到收盘单（exectype=bt.Order.Close）：以下一个Bar的收盘价成交。
            # 止损单（exectype=bt.Order.Stop）：当价格触及止损价时以市价成交。
            # 止损限价单（exectype=bt.Order.StopLimit）：先以止损价触发，再以限价成交。

# 2. 创建Cerebro引擎
# 又叫做：
# 实例化大脑
cerebro = bt.Cerebro()
cerebro.addstrategy(MACDStrategy)
# cerebro.addstrategy(BuyAndHoldStrategy)

# 此外，还可以通过 analyzers 策略分析模块和 observers 观测器模块提前配置好要返回的回测结果，
# 比如想要返回策略的收益率序列、常规的策略评价指标，就可以提前将指标添加给大脑：
# cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='pnl'）# 返回收益率时序数据
# cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
# cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown') # 最大回撤
# cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='_AnnualReturn') # 年化收益率
# cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='_SharpeRatio') # 夏普比率
# cerebro.addanalyzer(bt.analyzers.DrawDown, name='DrawDown') # 回撤

# 还可以添加观测器
# cerebro.addobserver(...)

# 3. 加载数据（以CSV为例）
# 方法1、从离线文件加载，暂时不采用
# data = bt.feeds.GenericCSVData(
#     dataname='your_data.csv',  # 请替换成你的CSV路径
#     dtformat='%Y-%m-%d',
#     timeframe=bt.TimeFrame.Days,
#     openinterest=-1,
#     volume=-1,
#     open=1,
#     high=2,
#     low=3,
#     close=4,
#     datetime=0
# )
# cerebro.adddata(data)

# 方法2、从接口api加载
fq_type = 'qfq'

import akshare as ak
# start_date = "20220701"
# end_date = "20250701"
start_date = "20230101"
end_date = "20241231"

# qfq，新浪接口
# 初始资金: 100000.00
# 最终资金: 148878.45
# 净收益: 48878.45
# ROI: 48.88%

# hfq，新浪接口
# 初始资金: 100000.00
# 最终资金: 148894.49
# 净收益: 48894.49
# ROI: 48.89%

# 不复权
# 初始资金: 100000.00
# 最终资金: 137601.52
# 净收益: 37601.52
# ROI: 37.60%

# 但是正确答案应该是接近100%！

# 怎么回事？？？
# 1、只交易一次，费率可以忽略不计
# 2、而且因为是全仓计算比例，所以采用前复权或者后复权价格都可以，反正结果是等比缩放的
# 不过以后还是应该用不复权价格吧！因为这样买的股票才是真实的价格



import pandas as pd
# pd.set_option('display.max_rows', None)  # 不限制行数
# pd.set_option('display.max_columns', None)  # 不限制列数
# pd.set_option('display.width', None)  # 不限制输出宽度

# 用 DataFeeds 模块导入DataFrame 数据框必须依次包含7个字段
# 'datetime'、 'open'、'high'、'low'、'close'、'volume'、'openinterest'
# 所以下面两个接口都需要对列名进行修改

# 1. 东财接口
# fund_hist = ak.fund_etf_hist_em( # TODO：这里有风险，是东财接口，用的是加减复权，不是比例复权
#     symbol="601398", period="daily",
#     start_date=start_date, end_date=end_date,
#     adjust=fq_type
# )
# fund_hist['datetime'] = pd.to_datetime(fund_hist['日期'])
# fund_hist['open'] = fund_hist['开盘']
# fund_hist['close'] = fund_hist['收盘']
# fund_hist['high'] = fund_hist['最高']
# fund_hist['low'] = fund_hist['最低']
# fund_hist['volume'] = fund_hist['成交量']
# fund_hist['openinterest'] = 0 # TODO: akshare不提供：未平仓合约的数量（Open Interest）

# 2. 新浪接口
fund_hist = ak.stock_zh_a_daily( # 换成了新浪的接口
    symbol="sh"+"601398",
    start_date="20220701", end_date="20250701", # 爸爸的操作时间比我以为的更长
    adjust=fq_type
)
fund_hist['datetime'] = pd.to_datetime(fund_hist['date'])
fund_hist['openinterest'] = 0 # TODO: akshare不提供：未平仓合约的数量（Open Interest）

# 加载到 cerebro 中
fund_hist.set_index("datetime", inplace=True) # 需要修改index为datetime这一列
from_date = pd.Timestamp(start_date)
to_date = pd.Timestamp(end_date)
data = bt.feeds.PandasData(dataname=fund_hist, fromdate=from_date, todate=to_date)
cerebro.adddata(data)

# 4. 设置初始资金和费率（以及滑点）
start_cash = 100000
cerebro.broker.setcash(start_cash)
cerebro.broker.setcommission(commission=0.002) # 双边佣金
# cerebro.broker.set_slippage_perc(perc=0.001) # 双边滑点

# 5. 启动回测
cerebro.run()