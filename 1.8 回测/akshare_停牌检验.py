# 停牌的日期，都不会计入

import akshare as ak

stock_tfp_em_df = ak.stock_tfp_em(date="20240426")
print(stock_tfp_em_df)
# 登云股份  2024-04-15 开始连续停牌

data = ak.stock_zh_a_hist(
    symbol="002715", # 登云股份,
    period="daily",
    start_date="20240401",
    end_date="20240526",
    adjust=""
)
print(data)

# 可以验证，现在没有对于缺失的数据进行填补，而是假装没有这一天，跟闭市一样
# 也就是这一天无法进行任何操作，目前看起来是可以的