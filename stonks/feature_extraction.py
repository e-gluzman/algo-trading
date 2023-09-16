from ta.trend import macd_signal
import pandas as pd
import numpy as np
from ta.trend import macd
from ta.trend import MACD
from ta.trend import SMAIndicator
from ta.trend import ema_indicator
from ta.trend import adx, cci
import plotly.graph_objects as go
import yfinance as yf
from ta.volatility import average_true_range
from ta.momentum import rsi
from pytz import timezone

def get_features(hist: pd.DataFrame, features = None, window_limit = 100000):

    # returns, positive/negative, log?
    hist['returns'] = hist.close.pct_change()
    # volume indicators
    hist['volume_pct_change'] = hist.volume.pct_change()

    hist['minutes_open'] = hist.index.hour * 60 + hist.index.minute - 570
    hist['date'] = hist.index.date
    hist['datetime'] = hist.index
    hist['market_open'] = hist['datetime'].apply(lambda x: x.replace(
        hour=9,
        minute=30,
        second=0
    ))
    timestamp = hist.index
    hist = pd.merge(hist,hist[['close','datetime']],how='left',left_on='market_open',right_on='datetime',suffixes=[None,'_market_open'])
    hist.index = timestamp
    
    hist['pct_change_daily'] = (hist.close/ hist.close_market_open - 1) * 100

    bins = list(range(0,420,30))
    hist['30_min_bin'] = pd.cut(hist['minutes_open'],bins=bins, include_lowest=True, labels=False)
    hist['first_30_min'] = np.where(hist['30_min_bin'] == 0, 1, 0)
    hist['last_30_min'] = np.where(hist['30_min_bin'] == 12, 1, 0)

    # here is a list of minute windows to create features for.
    # this function iterates over them to create indicators that consider different timescales when forecasting stock price movements.
    # e.g. 
    # hour = 60
    # day = 1440
    # week = 10080
    # month = 43200

    windows = [     1,      2,      3,      5,      8,     12,     20,     26,
           40,     50,     60,     80,    100,    150,    200,    250,
          300,    400,    500,    600,    700,    800,   1000,   1200,
         1500,   1800,   2000,   2500,   3000,   5000,   6000,   7000,
         9000,  10000,  12000,  15000,  20000,  30000,  45000,  60000,
        80000, 100000, 150000, 200000]
    window_pairs = [[1,2],[2,3],[3,5],[5,8],[5,12],[5,26],[8,26],[12,26],[12,50],[12,100],[12,500],[20,60],[20,150],[26,50],[26,80],[26,100],[26,500],
                    [50,100],[50,200],[60,150],[60,1500],[300,500],[300,800],[700,1500],[1500,15000],
                    [7000,20000],[10000,45000],[45000,100000],[45000,200000]]

    if features != None:
        windows = []
        window_pairs = []
        for i in features:
            if '_' in i:
                f = i.split('_')
                if f[-1].isnumeric():
                    if int(f[-1]) not in windows:
                        windows.append(int(f[-1]))
                if f[-2].isnumeric():
                    if int(f[-2]) not in windows:
                        windows.append(int(f[-2]))
                    if [int(f[-2]), int(f[-1])] not in window_pairs:
                        window_pairs.append([int(f[-2]), int(f[-1])])

    for i in windows:

        if (i < len(hist)) and (i < window_limit):
            # generate ATRs
            hist['ATR_' + str(i)] = average_true_range(hist.high,hist.low,hist.close,window=i)

            # generate RSIs
            hist['RSI_' + str(i)] = rsi(hist.close,window=i)

            # CCI
            if i > 3:
                hist['CCI_' + str(i)] = cci(high = hist.high, low = hist.low, close = hist.close, window=i)
            # ADX
            if i > 1:
                hist['ADX_' + str(i)] = adx(high = hist.high, low = hist.low, close = hist.close, window=i)

            # EMAs
            hist['ema_' + str(i)] = ema_indicator(hist.close,window=i)

            # volume
            hist['ema_volume_' + str(i)] = ema_indicator(hist.volume,window=i)

            # volatility as exponential rolling standard deviation
            hist['vol_std_' + str(i)] = hist.close.ewm(i).std()
            hist['vol_std_volume_' + str(i)] = hist.volume.ewm(i).std()

            # volatility based on standard deviation expressed as percentage of exponential moving average window
            hist['vol_pct_' + str(i)] = hist.close.ewm(i).std() / hist.close.ewm(i).mean() * 100
            hist['vol_pct_volume_' + str(i)] = hist.volume.ewm(i).std() / hist.volume.ewm(i).mean() * 100

            # volatility of returns
            hist['returns_vol_std_' + str(i)] = hist['returns'].ewm(i).std()

            # swing low/ swing high
            hist['swing_low_' + str(i)] = hist.close.rolling(i).min()
            hist['swing_high_' + str(i)] = hist.close.rolling(i).max()

            # swing low/ swing high expressed as percentage
            hist['swing_low_pct_' + str(i)] = (hist['swing_low_' + str(i)] / hist['ema_' + str(i)]) * 100
            hist['swing_high_pct_' + str(i)] = (hist['swing_high_' + str(i)] / hist['ema_' + str(i)]) * 100

            # max min in terms of volatility
            hist['min_vol_std_' + str(i)] = (hist['swing_low_' + str(i)] - hist['ema_' + str(i)]) /hist['vol_std_' + str(i)]
            hist['max_vol_std_' + str(i)] = (hist['swing_high_' + str(i)] - hist['ema_' + str(i)]) /hist['vol_std_' + str(i)]

            # How far is the current close price over the EMA?
            # expressed in terms of standard deviation
            hist['close_ema_vol_std_' + str(i)] = (hist.close - hist['ema_' + str(i)]) / hist['vol_std_' + str(i)]
            # expressed in terms of pct
            hist['close_ema_pct_' + str(i)] = (hist.close - hist['ema_' + str(i)]) / hist['ema_' + str(i)] * 100

            # how much did the same ema change over a time period, expressed in standard deviations.
            hist['ema_vol_std_shift_' + str(i)] = (hist['ema_' + str(i)] - hist['ema_' + str(i)].shift(i))/ hist['vol_std_' + str(i)]

            # volatility as standard deviation converted to pct % of recent EMA
            hist['vol_std_pct_' + str(i)] = hist['vol_std_' + str(i)]/hist['ema_' + str(i)]

            # ratio of volatilities over differnt time periods. how is volatility changing from one period to another?
            hist['vol_std_pct_ratio_' + str(i)] = hist['vol_std_pct_' + str(i)]/ hist['vol_std_pct_' + str(i)].shift(i)

            # returns ema
            hist['returns_ema_' + str(i)] = hist.returns.ewm(i).mean()

            # I use these features to estimate how much price change we should expect in a time period, e.g. to set stop loss and take profit targets
            # e.g. how much does the stock's EMA change on average over a 50 minute window, based on the last 5000 minutes?
            hist['exp_ema_pct_shift_' + str(i)] = np.abs((1 - (hist['ema_' + str(i)]/ hist['ema_' + str(i)].shift(i)).ewm(i * 100).mean()))
            hist['exp_ema_pct_abs_shift_' + str(i)] = (np.abs(1 - hist['ema_' + str(i)]/ hist['ema_' + str(i)].shift(i))).ewm(i * 100).mean()
            hist['exp_ema_pct_dir_shift_' + str(i)] = ((1 - hist['ema_' + str(i)]/ hist['ema_' + str(i)].shift(i))).ewm(i * 100).mean()
            # what is the average volatility in time period i over the last i*100 minutes? 
            hist['exp_pct_volatility_' + str(i)] = (hist['vol_std_' + str(i)]/hist['ema_' + str(i)]).ewm(i * 100).mean()
            hist['exp_pct_volatility_old_' + str(i)] = hist['vol_std_' + str(i)]/hist['ema_' + str(i)].ewm(i * 100).mean()

    
    for i in window_pairs:

        window_fast = i[0]
        window_slow = i[1]

        if (window_fast < len(hist)) & (window_slow < len(hist)) & (window_slow < window_limit):

            # calculating MACDs
            # closing price
            name = 'macd_' + str(window_fast) + '_' + str(window_slow)

            hist[name] = macd(
                hist.close,
                window_fast=window_fast,
                window_slow=window_slow)
            
            signal_name = name + '_signal'

            signal_line = macd_signal(
                hist.close,
                window_fast=window_fast,
                window_slow=window_slow)
            
            hist[signal_name] = np.where(hist[name] > signal_line, 1, 0)

            # volume
            name = 'volume_macd_' + str(window_fast) + '_' + str(window_slow)

            hist[name] = macd(
                hist.volume,
                window_fast=window_fast,
                window_slow=window_slow)
            
            signal_name = name + '_signal'

            signal_line = macd_signal(
                hist.volume,
                window_fast=window_fast,
                window_slow=window_slow)
            
            hist[signal_name] = np.where(hist[name] > signal_line, 1, 0)

            # volume macd expressed in standard deviations
            hist['ema_volume_vol_std_' + str(window_fast) + '_' + str(window_slow)] = hist['volume_macd_' + str(window_fast) + '_' + str(window_slow)] / hist['vol_std_volume_' + str(window_slow)]
            hist['ema_volume_vol_std_new_' + str(window_fast) + '_' + str(window_slow)] = hist['volume_macd_' + str(window_fast) + '_' + str(window_slow)] / hist['vol_std_volume_' + str(window_fast)]
            # volume macd expressed in pct
            hist['volume_macd_pct_' + str(window_fast) + '_' + str(window_slow)] = hist['volume_macd_' + str(window_fast) + '_' + str(window_slow)] / hist['ema_volume_' + str(window_fast)] * 100

            # closing price macd as standard deviations
            hist['ema_vol_std_shift_' + str(window_fast) + '_' + str(window_slow)] = (hist['ema_' + str(window_fast)] - hist['ema_' + str(window_slow)])/hist['vol_std_' + str(window_slow)]
            hist['ema_vol_std_shift_new_' + str(window_fast) + '_' + str(window_slow)] = (hist['ema_' + str(window_fast)] - hist['ema_' + str(window_slow)])/hist['vol_std_' + str(window_fast)]

            # closing price macd as pct
            hist['macd_pct_' + str(window_fast) + '_' + str(window_slow)] = (hist['ema_' + str(window_fast)] - hist['ema_' + str(window_slow)])/ hist['ema_' + str(window_fast)] * 100

            # ratio of expected volatilites over two time periods
            hist['vol_std_pct_ratio_' + str(window_fast) + '_' + str(window_slow)] = (hist['vol_std_' + str(window_fast)]/hist['ema_' + str(window_fast)])/(hist['vol_std_' + str(window_slow)]/hist['ema_' + str(window_slow)])


    hist['returns_EMA_20'] = hist.returns.ewm(20).mean()
    hist['returns_EMA_50'] = hist.returns.ewm(50).mean()
    hist['returns_EMA_80'] = hist.returns.ewm(80).mean()
    hist['returns_EMA_200'] = hist.returns.ewm(200).mean()
    hist['returns_EMA_1200'] = hist.returns.ewm(1200).mean()

    # candle features
    hist['candle'] = hist.close - hist.open
    hist['candle_pct'] = (hist.close - hist.open) / hist.open * 100

    if features:
        #return hist.loc[:,features]
        return hist
    else:
        return hist

