# code: https://www.kaggle.com/code/flat831/4th-place-model/notebook?scriptVersionId=100052889
# 我的fork: https://www.kaggle.com/code/kamijoutoumakun/4th-place-model/edit?fromFork=1
# 这个代码在本地没法跑，需要 jpx_tokyo_market_prediction.make_env() 的线上环境

# readme: overview
# 按最近一次返回的逆序进行排名的模型
# 若存在ExpectedDividend，很可能出现负值，因此需制定降级规则



# part 1
# libraries
import os
from decimal import ROUND_HALF_UP, Decimal#float型の計算を正確に行うため

import numpy as np
import pandas as pd
from tqdm import tqdm#処理状況の可視化
import warnings

warnings.filterwarnings('ignore')



# part 2
# set base_dir to load data
# base_dir = "jpx-tokyo-stock-exchange-prediction"
base_dir = "." # 我的修改

train_files_dir = f"{base_dir}/train_files"
supplemental_files_dir = f"{base_dir}/supplemental_files"



# part 3
#分割・逆分割による過去の価格差を小さくするために、AdjustmentFactorの値を用いて、株価を修正する
def adjust_price(price):
    """
    Args:
        price (pd.DataFrame)  : pd.DataFrame include stock_price
    Returns:
        price DataFrame (pd.DataFrame): stock_price with generated AdjustedClose
    """
    # transform Date column into datetime
    price.loc[: ,"Date"] = pd.to_datetime(price.loc[: ,"Date"], format="%Y-%m-%d")

    def generate_adjusted_close(df):
        """
        Args:
            df (pd.DataFrame)  : stock_price for a single SecuritiesCode
        Returns:
            df (pd.DataFrame): stock_price with AdjustedClose for a single SecuritiesCode
        """
        # sort data to generate CumulativeAdjustmentFactor
        df = df.sort_values("Date", ascending=False)#降順(最新のものが先頭)
        # generate CumulativeAdjustmentFactor
        df.loc[:, "CumulativeAdjustmentFactor"] = df["AdjustmentFactor"].cumprod()#cumprodは累積積を求める関数
        # generate AdjustedClose
        df.loc[:, "AdjustedClose"] = (
            df["CumulativeAdjustmentFactor"] * df["Close"]
        ).map(lambda x: float(
            Decimal(str(x)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)#四捨五入
        ))
        # reverse order
        df = df.sort_values("Date")#昇順に戻す
        # to fill AdjustedClose, replace 0 into np.nan
        df.loc[df["AdjustedClose"] == 0, "AdjustedClose"] = np.nan
        # forward fill AdjustedClose
        df.loc[:, "AdjustedClose"] = df.loc[:, "AdjustedClose"].ffill()#ffill:前(上)の値に置換
        return df

    # generate AdjustedClose
    price = price.sort_values(["SecuritiesCode", "Date"])
    price = price.groupby("SecuritiesCode").apply(generate_adjusted_close).reset_index(drop=True)

    price.set_index("Date", inplace=True)
    return price



# part 4
def get_features_for_predict(price, code):
    """
    Args:
        price (pd.DataFrame)  : pd.DataFrame include stock_price
        code (int)  : A local code for a listed company
    Returns:
        feature DataFrame (pd.DataFrame)
    """
    close_col = "AdjustedClose"
    feats = price.loc[price["SecuritiesCode"] == code, ["SecuritiesCode", close_col, "ExpectedDividend"]].copy()

    # calculate return using AdjustedClose
    feats["return_1day"] = feats[close_col].pct_change(1)
    
    # ExpectedDividend
    feats["ExpectedDividend"] = feats["ExpectedDividend"].mask(feats["ExpectedDividend"] > 0, 1)

    # filling data for nan and inf
    feats = feats.fillna(0)
    feats = feats.replace([np.inf, -np.inf], 0)
    # drop AdjustedClose column
    feats = feats.drop([close_col], axis=1)

    return feats



# part 5
# load stock price data
df_price_raw = pd.read_csv(f"{train_files_dir}/stock_prices.csv")
price_cols = [
    "Date",
    "SecuritiesCode",
    "Close",
    "AdjustmentFactor",
    "ExpectedDividend"
]
df_price_raw = df_price_raw[price_cols]

# forecasting phase leaderboard:
df_price_supplemental = pd.read_csv(f"{supplemental_files_dir}/stock_prices.csv")
df_price_supplemental = df_price_supplemental[price_cols]
df_price_raw = pd.concat([df_price_raw, df_price_supplemental])

# filter data to reduce culculation cost 
df_price_raw = df_price_raw.loc[df_price_raw["Date"] >= "2022-07-01"]



# part 6 这一段，所有提交的代码都需要这么写
# load Time Series API
import jpx_tokyo_market_prediction
# make Time Series API environment (this function can be called only once in a session)
env = jpx_tokyo_market_prediction.make_env()
# get iterator to fetch data day by day
iter_test = env.iter_test()



# part 7
counter = 0
# fetch data day by day
for (prices, options, financials, trades, secondary_prices, sample_prediction) in iter_test:
    current_date = prices["Date"].iloc[0]
    sample_prediction_date = sample_prediction["Date"].iloc[0]
    print(f"current_date: {current_date}, sample_prediction_date: {sample_prediction_date}")

    if counter == 0:
        # to avoid data leakage
        df_price_raw = df_price_raw.loc[df_price_raw["Date"] < current_date]#current_date以前のデータにする

    # to generate AdjustedClose, increment price data
    df_price_raw = pd.concat([df_price_raw, prices[price_cols]])
    # generate AdjustedClose
    df_price = adjust_price(df_price_raw)

    # get target SecuritiesCodes
    codes = sorted(prices["SecuritiesCode"].unique())

    # generate feature
    feature = pd.concat([get_features_for_predict(df_price, code) for code in codes])
    # filter feature for this iteration
    feature = feature.loc[feature.index == current_date]

    # prediction
    feature.loc[:, "predict"] = feature["return_1day"] + feature["ExpectedDividend"]*100

    # set rank by predict
    feature = feature.sort_values("predict", ascending=True).drop_duplicates(subset=['SecuritiesCode'])
    feature.loc[:, "Rank"] = np.arange(len(feature))
    feature_map = feature.set_index('SecuritiesCode')['Rank'].to_dict()
    sample_prediction['Rank'] = sample_prediction['SecuritiesCode'].map(feature_map)

    # check Rank
    assert sample_prediction["Rank"].notna().all()
    assert sample_prediction["Rank"].min() == 0
    assert sample_prediction["Rank"].max() == len(sample_prediction["Rank"]) - 1

    # register your predictions
    env.predict(sample_prediction)
    counter += 1

# head submission.csv # 由 env.predict 自己生成的结果 输出的是 2021-12-06
# tail submission.csv # 由 env.predict 自己生成的结果 输出的是 2021-12-07 每天股票的排名
print(sample_prediction) # 这个则是输出 2021-12-07 当天的预测
# 但是看不到之后每一天的结果

# 看起来是每一天跑一次，每一天都能拿到前一天的真值
# 训练数据集里面显示的最后一个交易日是 2021-12-03
# 奇怪了，那为什么第一天的预测结果不是 2021-12-06，而是 2021-12-07？？？

# 需要在 https://www.kaggle.com/code/kamijoutoumakun/4th-place-model/edit
# 点击右下角的 Submit to competition
# 完成后显示一个网站：https://www.kaggle.com/code/kamijoutoumakun/4th-place-model?scriptVersionId=289955464

# 回到 https://www.kaggle.com/competitions/jpx-tokyo-stock-exchange-prediction/submissions#
# 看结果，我等了十七分钟才刷出复现结果

# Kaggle竞赛的评分机制主要分为两种：
# 一种是公共排行榜（Public Leaderboard），提交后通常在几分钟内就能看到评分结果，用于实时跟踪进展；
# 另一种是私有排行榜（Private Leaderboard），其结果在比赛结束时才公布，用于最终排名。

