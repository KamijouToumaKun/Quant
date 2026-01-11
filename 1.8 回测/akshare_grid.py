# readme: https://xueqiu.com/5610083273/323452373
# 华泰柏瑞上证红利ETF（代码510880）
# 回测了一下从2014年1月1日到2024年12月31日，采用分红再投资的方法买入510880，
# 其中网格最优参数下收益率是255.50%，买入一直持有是268.65%，
# 也就是510880,分红再投资获得10年2.68倍的收益

# 代码：https://xueqiu.com/5610083273/323453634
# 1、整个红利ETF，也就是510880从2019年1月4日到2021年12月31日，完全不考虑网格和分红的情况下，其持有收益为41.10%
# 由于对于红利ETF来说，其分红是非常重要的属性，所以我在这种情况下并没有考虑网格交易，而是改进代码，将其改成基于分红再投资
# 而分红后的资金将立即买入作为新的份额输入
# 当我们考虑分红再投资后，整个期间基金的收益将上升到84.02%，也就是相较于不考虑分后在投资的收益，其总收益几乎增加了1倍，这个结论非常的有意思
# 但是到目前为止，还没有考虑网格搜索，和网格交易

# 引入了网格搜索：寻找最优参数组合 + 网格交易：做T
# 采用网格后，其收益情况如何？
# 我尝试了大量的网格组合，其中关键的变量有以下这些：
# 第一，initial_ration：也就是我初始投入多少资金，初始仓位占比；
# 第二，rise_threshold：也就是我的上涨阈值，在上涨多少后抛出部分基金；
# 第三，fall_threshold：也就是我下跌阈值，下跌多少时抛出部分基金；
# 最后，是trade_ratio：也就是我每次抛出的交易比例

# 我发现最优参数组合下超额收益为-6.73%,这就说明了如果我是从2019年1月4日开始，也就是上轮牛市的起点开始，
# 我采用网格的方法无法战胜全仓持有红利ETF并分红再投资
# 也就是如果同样是分红再投资，中间则无法战胜长期持有

# 2、2019年1月4日是绝对低点，我如果选择2019年4月8日，也就是牛市的第一个高点会如何？
# （也就是下面代码的部分）
# 我继续进行了回测，当我将日期设置为2019年4月8日至2021年12月31日时，
# 我们全仓持有并复投的收益降低到35.24%，同时采用最优参数下的网格收益提升到44.04%，也就是获得了8.8%的超额收益。
# （代码可以复现，我的缩进复原应该没有问题）
# 这个现象很有意思，说明了当我们全仓在一个最高点买入后，我最终的收益要大幅度降低
# 同时网格策略似乎比较适合于在一个高点切入，并获得了一定的超额收益
# === 最优参数组合 ===
# 初始仓位比例: 0%
# 上涨阈值: 12%
# 下跌阈值: 2%
# 交易比例: 16%

# 发现了一些代码问题：
# 1、
# cash += dividend_cash
# 我的修改：分红的金额不是全买成股票了吗，为什么cash要加？
# 修改之后：结果降低了很多

# 2、以下代码采用的是：前复权+手动模拟分红复投
# 那为什么不直接采用后复权呢？自动分红复投，计算自己的真实总收益、对比长期投资回报
# google的ai也是这么说的
# 我对于复权的理解：
# 不复权：相当于股价降低了，现金多了。把现金拿回去买股票，则相当于股价降低了，股票份额多了，整体资产几乎不变？
# 前复权+手动分红复投：相当于采用变低的股价 + 高股票份额
# 后复权：相当于采用约等于不变的股价（因为整体资产几乎不变） + 不变的股票份额
# 于是对于后复权调整了一下 ratio，结果差别不大
# 按理说还需要调整 base_price，但看起来意义也不大

# 于是，我又尝试从前复权改成了后复权，结果这下变化很大了

# 查了一下，分红数量不对，修改了
# 现在的结果：
# 核心问题在于：就连买入持有，结果相差还是可能很大！

# google ai：使用前复权 = 后复权 约等于 不复权+手动模拟分红（无论是复投还是不复投，都是约等号，是正常的）
# 发现很大的问题在于，复权的计算方式不对，这个问题记录到了excel中
# 注意，需要是比例复权法给出的结果，于是换到了新浪接口
# 分红复投肯定比不复投结果会高一些
# 前复权和后复权，到底跟不复权+手动模拟分红 + 复投还是不复投更接近？ai的说法自己都在变

# 总结以下，这次回测得到了几点非常有意思的结论：
# 第一，在相对低点买入和最高点买入，其最终收益相差巨大，因此买入点非常重要。
# 买入点低，一直买入持有就够了
# 买入点高，就需要网格操作
    # 此时再将起始日期改成20190104
    # 后复权结果：
    # === 最优参数组合 ===
    # 初始仓位比例: 90%
    # 上涨阈值: 18%
    # 下跌阈值: 2%
    # 交易比例: 26%
    # 预期收益率: 23.68%
    # 交易次数: 22 次
    # === 最优策略详细回测 ===
    # 【网格策略】
    # 最终收益率: 23.68%
    # 【买入持有策略】
    # 最终收益率: 22.22%
    # 超额收益率: 1.46%

    # 改成不复权+手动模拟分红复投试试
    # === 最优参数组合 ===
    # 初始仓位比例: 90%
    # 上涨阈值: 18%
    # 下跌阈值: 6%
    # 交易比例: 26%
    # 预期收益率: 29.55%
    # 交易次数: 9 次
    # === 最优策略详细回测 ===
    # 【网格策略】
    # 最终收益率: 29.55%
    # 【买入持有策略】
    # 最终收益率: 28.22%
    # 超额收益率: 1.33%

    # 上述结论可以验证
# 第二，对于红利ETF来说，如果采用网格方式，出现较为频繁的网格参数如下，即上涨阈值设置为12%,下跌阈值设置为2%，买入份额一般为16%。
# 第三，红利ETF分红后复投非常的重要，会极大的影响收益，例如我如果分红后不复投，我同样选择2019年4月8日这样一个高点，我买入并持有的收益只有3.71%，但是如果我选择分红后复投，其收益将增加到35.24%。这也就意味着，哪怕我红利基金买的位置很高，甚至我全仓买了个高点，我采用分红后复投的方法也能极大程度上增加收益。
    # 作者关于分红复投的进一步说明：https://xueqiu.com/5610083273/325187886
    # 我不复投的结果跟作者相仿，复投也只高了一点。是作者自己算错了！

# 第四，我选择的2021年12月31日其实也是一个很大的低点，如果合理控制高点和低点，我们选择在2019年1月4日到2021年这三年的牛市中，红利ETF这样一个基金也能够获得超过100%的收益。这也就是意味着，很多人认为牛市中红利ETF跑不过科技股的言论是错误的，我的代码回测说明，这轮大牛市，红利ETF这样一个普通的基金的收益也达到了84.02%，并没有严重落后于当时的白马基金和科技股基金

# 两个红利etf的差别很大
# 招商中证红利ETF（基金代码515080）跟踪的指数是中证红利指数
# 中证红利指数（沪市代码000922，深市代码399922）本身不能买，只能买ETF
# 中证指数官网的全收益指数，就是官方给的复投收益
#     https://www.csindex.com.cn/#/indices/family/detail?indexCode=000922
#     https://www.csindex.com.cn/#/indices/family/detail?indexCode=399922 则无法访问
#     其他指数也可以去查 https://www.csindex.com.cn/#/search?searchText=%E7%BA%A2%E5%88%A9

# 像这里说的这样看：https://xueqiu.com/7072298555/365921360

# 1、看价格指数，就是不复投，就不选择衍生指数
# 但是我选择了后，网页就出错，给不出结果
# 还是只能看雪球：https://xueqiu.com/S/SH000922

# 招商中证红利ETF（基金代码515080）跟踪的指数是中证红利指数
# 雪球的结果和akshare东财的结果一样，都是不复权：因为指数本身没有分红和拆股
# 4188.69 -> 5209.90
# (5209.90 - 4188.69) / 4188.69 = 24.38%
# 实际上应该加上分红，但是太多了不好算

# akshare接口给出的结果：
# 东财接口：不能选择复权形式，结果是一样的
# 新浪接口：不能选择开始和结束时间，而且返回的内容不全

# 2、看衍生指数
# 约从 6549 到 8738
# (8738 - 6549) / 6549 = 33.42%
# 1、加上了分红，应该是主要增加的收益
# 2、分红复投，这部分我算出来效果一直很低，可以忽略不计

# https://baijiahao.baidu.com/s?id=1851638647954504498&wfr=spider&for=pc
#     其实净收益指数更真实，还考虑了扣税
#     但是也差不多：加入了分红和复投
# 中证红利全收益指数也有自己的代码：H00922
# 那也可以直接去：https://www.csindex.com.cn/#/indices/family/detail?indexCode=H00922
# 这里就不能选衍生指数了
# 结果是一样的

# 但是都不如ETF：结果比实际还好？买入持有跑出来51%的收益率
# 因为跟踪误差吗？但都说易方达中证红利ETF（515180）是跟踪误差最低的一档的
# 该基金通过完全复制法跟踪标的指数，以追求跟踪偏离度和跟踪误差的最小化。

# 这种etf也没有什么溢价率，所以也没必要引入净值来检验：也需要算复权/不复权净值

# 问：怎么两个红利etf差距这么大呢？这个就这么猛，以至于网格交易又开始没有用了
# 答：
# 1、红利指数差别大
# 这个阶段上证红利指数510880 分红不复投收益率 17.81%，中证红利指数515080 分红不复投收益率 35.84% 本来差距就大
# 2、本基金早期的正跟踪误差大，所以etf收益率52%，赚得更多了
# 以至于
# 510880两年收益16%，年化7.7%
# 515080两年收益50%，年化22.47%
# 但后来稳定之后，515080的一年收益率也只有9%，跟之前的510880也差不多了

# 再测一下爸爸的工商银行 601398
# 时间改到：2023年初-2024年末

# 更后来的结论：https://xueqiu.com/5610083273/323472673
# 510880，一个最老最普通的红利etf，从2014年1月1日到2024年12月31日，分红复投收益2.68倍，还看啥雪球，分红复投就行了
# （这个值我还没有测，感觉不靠谱啊）
# 下面回帖又说15.8倍，分红复投：这个值又是怎么来的？
# 也有人质疑：
# 应该去查 https://www.csindex.com.cn/#/search?searchText=%E7%BA%A2%E5%88%A9
# 中证指数官网的全收益指数，只是这里看不到510880
# 得换一个，例如中证红利：中证红利指数（沪市代码000922但似乎会重名冲突，深市代码399922）
# https://www.csindex.com.cn/#/indices/family/detail?indexCode=000922
# 像这里说的这样看：https://xueqiu.com/7072298555/365921360
# 从 7549 到 8738，增长15.75%：就这样看吗？

import akshare as ak
import pandas as pd
import itertools
import numpy as np
from tqdm import tqdm # 用于显示进度条
# 参数搜索空间设置
param_grid = {
    'initial_ratio': np.arange(0, 1, 0.1), # 初始仓位比例 40%-70%，现在修改成了0-100%
    'rise_threshold': np.arange(0.02, 0.2, 0.02), # 上涨阈值 2%-10%，现在修改成了2%-20%
    'fall_threshold': np.arange(0.02, 0.2, 0.02), # 下跌阈值 2%-10%，现在修改成了2%-20%
    'trade_ratio': np.arange(0.01, 0.3, 0.05) # 交易比例 5%-20%，现在修改成了10%-30%
}
# 生成所有参数组合
all_params = list(itertools.product(*param_grid.values()))
# all_params = all_params[0:1] # 用于测试是否能跑通

# 获取510880历史数据（使用前复权以准确计算分红）
# $红利ETF(SH510880)$
# $红利低波50ETF(SH515450)$
# 沪深300指数不能直接购买
# 红利ETF、沪深300ETF也有分红
# 但是股指期货没有分红

fq_type = '' # '': 不复权 / 'qfq': 前复权 / 'hfq': 后复权
if_reinvest = False # 复投 / 不复投
def get_fund_data():
    # 1. 510880 中证红利
    # fund_hist = ak.fund_etf_hist_em( # TODO：这里有风险，是东财接口，用的是加减复权，不是比例复权
    #     symbol="510880", period="daily",
    #     start_date="20190408", end_date="20211231",
    #     adjust=fq_type
    # )
    # fund_hist['日期'] = pd.to_datetime(fund_hist['日期'])

    # fund_hist = ak.stock_zh_a_daily( # 换成了新浪的接口，但目前只能用于不复权
    #     symbol="sh"+"510880",
    #     start_date="20191201", end_date="20211231",
    #     adjust=fq_type
    # )
    # 而且需要我对代码做hack，才能处理基金而不是股票
    # /opt/homebrew/Caskroom/miniconda/base/envs/quant-python-3.9/lib/python3.9/site-packages/akshare/stock/stock_zh_a_sina.py
    # 中修改：
    # if adjust == "":
    #     if not pd.api.types.is_datetime64_any_dtype(temp_df.index[0]): # 是基金，类型是 <class 'datetime.date'>
    #         temp_df.index = pd.to_datetime(temp_df.index) # 转化成 <class 'pandas._libs.tslibs.timestamps.Timestamp'>
    #         temp_df.drop(columns=['outstanding_share', 'turnover'], inplace=True) # 因为内容都是nan
    #     temp_df = temp_df[start_date:end_date]
    #     temp_df.drop_duplicates(
    #         subset=["open", "high", "low", "close", "volume", "amount"], inplace=True
    #     )
    # fund_hist['日期'] = pd.to_datetime(fund_hist['date'])
    # fund_hist['收盘'] = fund_hist['close']
    # fund_hist['最高'] = fund_hist['high']
    # fund_hist['最低'] = fund_hist['low']

    # 手动录入分红数据（数据来源：基金公告）
    # 分红信息核实：华泰柏瑞上证红利ETF (510880)
    # https://fundf10.eastmoney.com/fhsp_510880.html
    # 或者 https://www.dayfund.cn/fundfh/510880.html
    # 但是对不上啊？
    # 华泰柏瑞上证红利ETF联接A (012761) 也不对
    # https://fundf10.eastmoney.com/fhsp_012761.html
    # 或者 https://www.dayfund.cn/fundfh/012761.html
    # 原来代码中错误的数据我删掉了
    # 修正之后应该是
    # 每份派现金0.0980元，分红发放日2019-01-21
    # 每份派现金0.1440元，分红发放日2020-01-22
    # 每份派现金0.1410元，分红发放日2021-01-21
    # 其实还是不对：应该是分红发放日发钱，而不是除权除息日
    # 暂且不管了，就在这里填上权益登记日吧，因为这一天之后的除权除息日，股价会突变
    # etf_dividend_data = [
    #     {'除权除息日': '2019-01-15', '每份分红': 0.098}, # 2019年分红
    #     {'除权除息日': '2020-01-16', '每份分红': 0.144}, # 2020年分红
    #     {'除权除息日': '2021-01-15', '每份分红': 0.141} # 2021年分红
    # ]
    
    # 2. 515080 招商中证红利ETF (515080)：换一个红利etf
    # https://fundf10.eastmoney.com/fhsp_515080.html
    # fund_hist = ak.fund_etf_hist_em( # TODO：这里有风险，是东财接口，用的是加减复权，不是比例复权
    #     symbol="515080", period="daily", # TODO: 这里换一个红利etf，差别就特别大！
    #     start_date="20190408", end_date="20211231",
    #     adjust=fq_type
    # )
    fund_hist = ak.stock_zh_a_daily( # 换成了新浪的接口，但目前只能用于不复权
        symbol="sh"+"515080",
        # start_date="20191201", end_date="20211231",
        start_date="20240110", end_date="20250110",
        adjust=fq_type
    )
    fund_hist['日期'] = pd.to_datetime(fund_hist['date'])
    fund_hist['收盘'] = fund_hist['close']
    fund_hist['最高'] = fund_hist['high']
    fund_hist['最低'] = fund_hist['low']
    etf_dividend_data = [
        {'除权除息日': '2020-11-27', '每份分红': 0.060}, # 2020年分红
        {'除权除息日': '2021-06-17', '每份分红': 0.030}, # 2021年分红
        {'除权除息日': '2021-12-08', '每份分红': 0.030}, # 2021年分红
        {'除权除息日': '2022-06-24', '每份分红': 0.030},
        {'除权除息日': '2022-11-28', '每份分红': 0.030},
        {'除权除息日': '2023-06-15', '每份分红': 0.035},
        {'除权除息日': '2023-11-30', '每份分红': 0.035},
        {'除权除息日': '2024-03-27', '每份分红': 0.015},
        {'除权除息日': '2024-06-28', '每份分红': 0.020},
        {'除权除息日': '2024-09-19', '每份分红': 0.015},
        {'除权除息日': '2024-11-29', '每份分红': 0.020},
        {'除权除息日': '2025-03-18', '每份分红': 0.015},
        {'除权除息日': '2025-06-16', '每份分红': 0.015},
        {'除权除息日': '2025-09-16', '每份分红': 0.015},
        {'除权除息日': '2025-12-17', '每份分红': 0.020},
    ]

    # 3. 601398 工商银行
    # https://data.eastmoney.com/yjfp/detail/601398.html
    # https://basic.10jqka.com.cn/mobile/601398/bonusn.html
    # fund_hist = ak.fund_etf_hist_em( # TODO：这里有风险，是东财接口，用的是加减复权，不是比例复权
    #     symbol="601398", period="daily",
    #     start_date="20230101", end_date="20241231",
    #     adjust=fq_type
    # )
    # fund_hist['日期'] = pd.to_datetime(fund_hist['日期'])

    # fund_hist = ak.stock_zh_a_daily( # 换成了新浪的接口
    #     symbol="sh"+"601398",
    #     # start_date="20230101", end_date="20241231",
    #     start_date="20220701", end_date="20250701", # 爸爸的操作时间比我以为的更长
    #     adjust=fq_type
    # )
    # fund_hist['日期'] = pd.to_datetime(fund_hist['date'])
    # fund_hist['收盘'] = fund_hist['close']
    # fund_hist['最高'] = fund_hist['high']
    # fund_hist['最低'] = fund_hist['low']
    
    # etf_dividend_data = [
    #     {'除权除息日': '2019-06-29', '每份分红': 0.2628},
    #     {'除权除息日': '2020-07-05', '每份分红': 0.266},
    #     {'除权除息日': '2021-07-11', '每份分红': 0.2933},
    #     {'除权除息日': '2022-07-14', '每份分红': 0.3035},
    #     # 2023没有
    #     {'除权除息日': '2024-07-15', '每份分红': 0.3064},
    #     {'除权除息日': '2025-01-06', '每份分红': 0.1434},
    #     {'除权除息日': '2025-07-11', '每份分红': 0.1646},
    #     {'除权除息日': '2025-12-12', '每份分红': 0.1414},
    # ]

    # 设定完成后，得到结果
    dividend_df = pd.DataFrame(etf_dividend_data)
    dividend_df['除权除息日'] = pd.to_datetime(dividend_df['除权除息日'])
    return fund_hist.sort_values('日期').reset_index(drop=True), dividend_df

# 带分红处理的网格策略回测
# 四个参数是定死的，相当于一个固定参数的 optimized_grid_trading
# 所以这个函数其实不用跑
def grid_trading_backtest(data, dividend_df):
    initial_capital = 500000
    initial_ratio = 0.6
    rise_threshold = 0.1
    fall_threshold = 0.1
    trade_ratio = 0.05
    # 初始化持仓
    first_day = data.iloc[0]
    base_price = first_day['收盘']
    shares = (initial_capital * initial_ratio) / base_price
    cash = initial_capital * (1 - initial_ratio)
    history = []
    dividend_log = []
    # 创建日期索引
    date_index = data['日期'].dt.date
    dividend_dates = dividend_df['除权除息日'].dt.date.values
    for i in range(len(data)):
        row = data.iloc[i]
        current_date = row['日期']
        current_price = row['收盘']
        if fq_type == '':
            # 处理分红（T日除权）
            if current_date.date() in dividend_dates:
                div_info = dividend_df[dividend_df['除权除息日'].dt.date == current_date.date()].iloc[0]
                per_share_div = div_info['每份分红']
                # 计算分红金额
                dividend_cash = shares * per_share_div
                if if_reinvest:
                    # 红利再投资（以收盘价买入）
                    # 我的修改：分红的金额不是全买成股票了吗，为什么cash要加？
                    reinvest_shares = dividend_cash / current_price
                    shares += reinvest_shares
                    dividend_log.append(('Dividend', current_date, current_price, reinvest_shares))
                else:
                    cash += dividend_cash
                    dividend_log.append(('Dividend', current_date, current_price, dividend_cash))
        elif fq_type in ['qfq', 'hfq']:
            # 后复权直接把结果算好了，不需要自己处理了
            # 如果后复权要与 不复权+手动模拟分红复投 对齐的话，就需要调整
            # 不复权的股价变低，股票份额变多
            # 1、trade_ratio：采用后复权，则买卖的股票份额也要打折扣
            # 其实应该是用不复权的价格，对于 current_price 进行分红调整
            # 不过其实复权后一股3元左右，每份现金分红0.01-0.014元左右，影响0.33-0.5%，跑出来结果相差不大
            # 2、base_price：也需要调整，但是调整的影响应该也不大
            if current_date.date() in dividend_dates:
                dividend_log.append(('Dividend', current_date, current_price))
                div_info = dividend_df[dividend_df['除权除息日'].dt.date == current_date.date()].iloc[0]
                trade_ratio *= (current_price - div_info['每份分红']) / current_price
        # 跳过第一天交易
        if i == 0:
            continue
        # 网格交易逻辑
        # TODO：也没有计算交易成本
        # 针对上一次买入的价格进行调整，这里采用的是比例而不是加减
        if current_price >= base_price * (1 + rise_threshold):
            # 卖出逻辑（保守用最低价）
            execute_price = row['最低']
            sell_shares = shares * trade_ratio
            if sell_shares > 0:
                sell_value = sell_shares * execute_price
                cash += sell_value
                shares -= sell_shares
                base_price = execute_price
                history.append(('Sell', current_date, execute_price, sell_shares))
        elif current_price <= base_price * (1 - fall_threshold):
            # 买入逻辑（保守用最高价）
            execute_price = row['最高']
            buy_value = cash * trade_ratio
            if 0 < buy_value <= cash:
                buy_shares = buy_value / execute_price
                cash -= buy_value
                shares += buy_shares
                base_price = execute_price
                history.append(('Buy', current_date, execute_price, buy_shares))
    
    final_value = shares * data.iloc[-1]['收盘'] + cash
    return final_value, history, dividend_log

# 带分红的买入持有策略
def buy_and_hold(data, dividend_df):
    initial_capital = 500000
    initial_ratio = 1
    # 初始买入
    first_day = data.iloc[0]
    shares = (initial_capital * initial_ratio) / first_day['收盘']
    cash = initial_capital * (1 - initial_ratio)
    # 处理分红
    dividend_dates = dividend_df['除权除息日'].dt.date.values
    for i in range(len(data)):
        row = data.iloc[i]
        current_price = row['收盘']
        if fq_type == '':
            if row['日期'].date() in dividend_dates:
                div_info = dividend_df[dividend_df['除权除息日'].dt.date == row['日期'].date()].iloc[0]
                per_share_div = div_info['每份分红']
                dividend_cash = shares * per_share_div
                if if_reinvest:
                    # 红利再投资
                    # 我的修改：分红的金额不是全买成股票了吗，为什么cash要加？
                    reinvest_shares = dividend_cash / current_price
                    shares += reinvest_shares
                else:
                    cash += dividend_cash                
        # elif fq_type in ['qfq', 'hfq']:
        #     # 后复权直接把结果算好了，不需要自己处理了
        #     # 如果后复权要与 不复权+手动模拟分红复投 对齐的话，就需要调整
        #     # 不复权的股价变低，股票份额变多
        #     # 1、trade_ratio：采用后复权，则买卖的股票份额也要打折扣
        #     # 其实应该是用不复权的价格，对于 current_price 进行分红调整
        #     # 不过其实复权后一股3元左右，每份现金分红0.01-0.014元左右，影响0.33-0.5%，跑出来结果相差不大
        #     # 2、base_price：也需要调整，但是调整的影响应该也不大
        #     if row['日期'].date() in dividend_dates:
        #         div_info = dividend_df[dividend_df['除权除息日'].dt.date == row['日期'].date()].iloc[0]
        #         trade_ratio *= (current_price - div_info['每份分红']) / current_price
        # 买入持有不需要 trade_ratio 和 base_price
    final_value = shares * data.iloc[-1]['收盘'] + cash
    return final_value

# 优化后的回测函数（参数可配置）
def optimized_grid_trading(data, dividend_df, params):
    initial_ratio, rise_threshold, fall_threshold, trade_ratio = params
    initial_capital = 500000
    first_day = data.iloc[0]
    base_price = first_day['收盘']
    shares = (initial_capital * initial_ratio) / base_price
    cash = initial_capital * (1 - initial_ratio)
    history = []
    dividend_log = []
    dividend_dates = dividend_df['除权除息日'].dt.date.values
    for i in range(len(data)):
        row = data.iloc[i]
        current_date = row['日期']
        current_price = row['收盘']
        if fq_type == '':
            # 处理分红
            if current_date.date() in dividend_dates:
                div_info = dividend_df[dividend_df['除权除息日'].dt.date == current_date.date()].iloc[0]
                per_share_div = div_info['每份分红']
                dividend_cash = shares * per_share_div
                if if_reinvest:
                    # 我的修改：分红的金额不是全买成股票了吗，为什么cash要加？
                    reinvest_shares = dividend_cash / current_price
                    shares += reinvest_shares
                else:
                    cash += dividend_cash                
        elif fq_type in ['qfq', 'hfq']:
            # 后复权直接把结果算好了，不需要自己处理了
            # 如果后复权要与 不复权+手动模拟分红复投 对齐的话，就需要调整
            # 不复权的股价变低，股票份额变多
            # 1、trade_ratio：采用后复权，则买卖的股票份额也要打折扣
            # 其实应该是用不复权的价格，对于 current_price 进行分红调整
            # 不过其实复权后一股3元左右，每份现金分红0.01-0.014元左右，影响0.33-0.5%，跑出来结果相差不大
            # 2、base_price：也需要调整，但是调整的影响应该也不大
            if current_date.date() in dividend_dates:
                div_info = dividend_df[dividend_df['除权除息日'].dt.date == current_date.date()].iloc[0]
                trade_ratio *= (current_price - div_info['每份分红']) / current_price
        if i == 0:
            continue
        # 网格交易逻辑
        # TODO：也没有计算交易成本
        # 针对上一次买入的价格进行调整，这里采用的是比例而不是加减
        if current_price >= base_price * (1 + rise_threshold):
            execute_price = row['最低']
            sell_shares = shares * trade_ratio
            if sell_shares > 1e-4: # 防止微小交易
                sell_value = sell_shares * execute_price
                cash += sell_value
                shares -= sell_shares
                base_price = execute_price
                history.append(('Sell', current_date, execute_price, sell_shares))
        elif current_price <= base_price * (1 - fall_threshold):
            execute_price = row['最高']
            buy_value = cash * trade_ratio
            if 1e-4 < buy_value <= cash:
                buy_shares = buy_value / execute_price
                cash -= buy_value
                shares += buy_shares
                base_price = execute_price
                history.append(('Buy', current_date, execute_price, buy_shares))
    final_value = shares * data.iloc[-1]['收盘'] + cash
    return {
        'final_value': final_value,
        'return_rate': (final_value / 500000 - 1) * 100,
        'trade_count': len(history),
        'params': params
    }

# 执行回测
price_data, dividend_data = get_fund_data()
# 执行参数优化
results = []
for params in tqdm(all_params, desc="参数优化进度"):
    try:
        result = optimized_grid_trading(price_data, dividend_data, params)
        results.append(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"参数 {params} 执行失败: {str(e)}")

# 转换为DataFrame便于分析
results_df = pd.DataFrame(results)
# 找出最优参数组合（按收益率排序）
best_result = results_df.loc[results_df['return_rate'].idxmax()]
# 网格策略
# grid_final, grid_trades, dividends = grid_trading_backtest(price_data, dividend_data)
# grid_return = grid_final - 500000
# grid_rate = (grid_final / 500000 - 1) * 100
# 买入持有策略
bh_final = buy_and_hold(price_data, dividend_data)
bh_return = bh_final - 500000
bh_rate = (bh_final / 500000 - 1) * 100
# 输出结果
# print(f"【网格策略】")
# print(f"最终资产: {grid_final:.2f} 元")
# print(f"总收益: {grid_return:.2f} 元")
# print(f"收益率: {grid_rate:.2f}%")
# print(f"交易次数: {len(grid_trades)} 次")
# print(f"分红处理次数: {len(dividends)} 次\n")
print(f"【买入持有策略】")
print(f"最终资产: {bh_final:.2f} 元")
print(f"总收益: {bh_return:.2f} 元")
print(f"收益率: {bh_rate:.2f}%\n")
# print(f"【超额收益】")
# print(f"超额收益: {grid_return - bh_return:.2f} 元")
# print(f"超额收益率: {grid_rate - bh_rate:.2f}%")
# 输出最近交易记录
# print("\n【最近5次交易记录】")
# for trade in grid_trades[-5:]:
#     print(f"{trade[1].strftime('%Y-%m-%d')} {trade[0]} 价格:{trade[2]:.3f} 份额:{trade[3]:.2f}")
# 输出分红记录
# print("\n【分红再投资记录】")
# for d in dividends:
#     print(f"{d[1].strftime('%Y-%m-%d')} 分红再投资 {d[3]:.2f}份 @ {d[2]:.3f}")
# 显示优化结果
print("\n=== 最优参数组合 ===")
print(f"初始仓位比例: {best_result['params'][0]:.0%}")
print(f"上涨阈值: {best_result['params'][1]:.0%}")
print(f"下跌阈值: {best_result['params'][2]:.0%}")
print(f"交易比例: {best_result['params'][3]:.0%}")
print(f"\n预期收益率: {best_result['return_rate']:.2f}%")
print(f"交易次数: {best_result['trade_count']} 次")
# 执行最优参数回测
print("\n=== 最优策略详细回测 ===")
best_params = best_result['params']
detailed_result = optimized_grid_trading(price_data, dividend_data, best_params)
# 与买入持有策略对比
print(f"\n【网格策略】")
print(f"最终收益率: {detailed_result['return_rate']:.2f}%")
print(f"【买入持有策略】")
print(f"最终收益率: {bh_rate:.2f}%")
print(f"超额收益率: {detailed_result['return_rate'] - bh_rate:.2f}%")