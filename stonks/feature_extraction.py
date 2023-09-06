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

# To-do - normalisation, positive 
# gain from start of day in pct or vol
# gain from last day close in pct or vol
# time of day - open, close, minute
# last 7 day behaviour
# did stock close higher than open
# did stock go below open?
# what was the within-day volatility?
# right now the algo does not distinguish between 50 min ma and 50 min ma (yesterday)
# candle behaviour - open-close over time as pct, also open-close now relative to it
# features by temp bin? what has happened with this bin recently?

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


    base = [5, 8, 12, 20, 26, 40, 50, 60, 80, 100, 150, 200]

    # windows = [5, 8, 12, 20, 26, 40, 50, 60, 80, 100, 150, 200, 
    #     250, 300, 400, 500, 600, 700, 800, 1000, 1200, 1500,
    #     1800, 2000, 2500, 3000, 5000, 6000, 7000, 9000, 10000, 12000,
    #     15000, 20000, 30000, 45000, 60000, 80000, 100000, 150000, 200000]
    
    windows = [     1,      2,      3,      5,      8,     12,     20,     26,
           40,     50,     60,     80,    100,    150,    200,    250,
          300,    400,    500,    600,    700,    800,   1000,   1200,
         1500,   1800,   2000,   2500,   3000,   5000,   6000,   7000,
         9000,  10000,  12000,  15000,  20000,  30000,  45000,  60000,
        80000, 100000, 150000, 200000]
    # hour = 60
    # day = 1440
    # week = 10080
    # month = 43200
    # add this to windows
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
    print(windows)
    print(window_pairs)
    for i in windows:

        if (i < len(hist)) and (i < window_limit):
            # generate ATRs
            hist['ATR_' + str(i)] = average_true_range(hist.high,hist.low,hist.close,window=i)

            # generate RSIs
            hist['RSI_' + str(i)] = rsi(hist.close,window=i)

            # CCI
            hist['CCI_' + str(i)] = cci(high = hist.high, low = hist.low, close = hist.close, window=i)

            # ADX
            hist['ADX_' + str(i)] = adx(high = hist.high, low = hist.low, close = hist.close, window=i)

            # EMAs
            hist['ema_' + str(i)] = ema_indicator(hist.close,window=i)

            # volume
            hist['ema_volume_' + str(i)] = ema_indicator(hist.volume,window=i)

            # volatility
            hist['vol_std_' + str(i)] = hist.close.ewm(i).std()
            hist['vol_std_volume_' + str(i)] = hist.volume.ewm(i).std()

            # volatility pct 
            hist['vol_pct_' + str(i)] = hist.close.ewm(i).std() / hist.close.ewm(i).mean() * 100
            hist['vol_pct_volume_' + str(i)] = hist.volume.ewm(i).std() / hist.volume.ewm(i).mean() * 100

            # volatility of returns
            hist['returns_vol_std_' + str(i)] = hist['returns'].ewm(i).std()
            # shifted returns or log returns

            # swing low/ swing high
            # add pct and volatility based swing low/high
            hist['swing_low_' + str(i)] = hist.close.rolling(i).min()
            hist['swing_high_' + str(i)] = hist.close.rolling(i).max()

            # swing low pct
            hist['swing_low_pct_' + str(i)] = (hist['swing_low_' + str(i)] / hist['ema_' + str(i)]) * 100
            hist['swing_high_pct_' + str(i)] = (hist['swing_high_' + str(i)] / hist['ema_' + str(i)]) * 100

            # close_ema_vol_std
            hist['close_ema_vol_std_' + str(i)] = (hist.close - hist['ema_' + str(i)]) / hist['vol_std_' + str(i)]

            # close_ema_pct
            hist['close_ema_pct_' + str(i)] = (hist.close - hist['ema_' + str(i)]) / hist['ema_' + str(i)] * 100

            #         # normalised trend
            # eg 20m vs 100m
            # by how many stds is our trend shifting over a certain period of time?
            # for a time window of 100
            # take vol_std_100 and ema_100 for 100 units behind
            # then subtract the means and divide by the old std

            #hist['vol_std_shift_' + str(i)] = (hist['ema_' + str(i)] - hist['ema_' + str(i)].shift(i))/ hist['vol_std_' + str(i)].shift(i)
            hist['ema_vol_std_shift_' + str(i)] = (hist['ema_' + str(i)] - hist['ema_' + str(i)].shift(i))/ hist['vol_std_' + str(i)]

            # in addition, we want some metric of changing volatility
            # for example, in a very volatile time window 1 std may mean 0.01% change, but in a low volatility time window it may be 0.001
            # this is important as if we expect a positive trend of one std from the previous time it needs to be comparable to the current std.
            #

            # volatility pct
            hist['vol_std_pct_' + str(i)] = hist['vol_std_' + str(i)]/hist['ema_' + str(i)]
            hist['vol_std_pct_ratio_' + str(i)] = hist['vol_std_pct_' + str(i)]/ hist['vol_std_pct_' + str(i)].shift(i)
            #hist['vol_std_pct_shift_ratio' + str(i)] = hist['vol_std_pct' + str(i)]/ hist['vol_std_pct' + str(i)].shift(i)

            # max min in terms of volatility
            hist['min_vol_std_' + str(i)] = (hist['swing_low_' + str(i)] - hist['ema_' + str(i)]) /hist['vol_std_' + str(i)]
            hist['max_vol_std_' + str(i)] = (hist['swing_high_' + str(i)] - hist['ema_' + str(i)]) /hist['vol_std_' + str(i)]

            # returns ema
            hist['returns_ema_' + str(i)] = hist.returns.ewm(i).mean()

            # generate MACDs 

            hist['exp_ema_pct_shift_' + str(i)] = np.abs((1 - (hist['ema_' + str(i)]/ hist['ema_' + str(i)].shift(i)).ewm(i * 100).mean()))
            hist['exp_ema_pct_abs_shift_' + str(i)] = (np.abs(1 - hist['ema_' + str(i)]/ hist['ema_' + str(i)].shift(i))).ewm(i * 100).mean()
            hist['exp_ema_pct_dir_shift_' + str(i)] = ((1 - hist['ema_' + str(i)]/ hist['ema_' + str(i)].shift(i))).ewm(i * 100).mean()
            hist['exp_pct_volatility_' + str(i)] = (hist['vol_std_' + str(i)]/hist['ema_' + str(i)]).ewm(i * 100).mean()
            hist['exp_pct_volatility_old_' + str(i)] = hist['vol_std_' + str(i)]/hist['ema_' + str(i)].ewm(i * 100).mean()

    
    for i in window_pairs:

        window_fast = i[0]
        window_slow = i[1]

        if (window_fast < len(hist)) & (window_slow < len(hist)) & (window_slow < window_limit):

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
            # add volume expressed in volatilities and pct
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

            hist['ema_volume_vol_std_' + str(window_fast) + '_' + str(window_slow)] = hist['volume_macd_' + str(window_fast) + '_' + str(window_slow)] / hist['vol_std_volume_' + str(window_slow)]
            hist['ema_volume_vol_std_new_' + str(window_fast) + '_' + str(window_slow)] = hist['volume_macd_' + str(window_fast) + '_' + str(window_slow)] / hist['vol_std_volume_' + str(window_fast)]

            hist['volume_macd_pct_' + str(window_fast) + '_' + str(window_slow)] = hist['volume_macd_' + str(window_fast) + '_' + str(window_slow)] / hist['ema_volume_' + str(window_fast)] * 100

            hist['ema_vol_std_shift_' + str(window_fast) + '_' + str(window_slow)] = (hist['ema_' + str(window_fast)] - hist['ema_' + str(window_slow)])/hist['vol_std_' + str(window_slow)]
            hist['ema_vol_std_shift_new_' + str(window_fast) + '_' + str(window_slow)] = (hist['ema_' + str(window_fast)] - hist['ema_' + str(window_slow)])/hist['vol_std_' + str(window_fast)]

            hist['macd_pct_' + str(window_fast) + '_' + str(window_slow)] = (hist['ema_' + str(window_fast)] - hist['ema_' + str(window_slow)])/ hist['ema_' + str(window_fast)] * 100

            # ema shift (macd) as fraction of current closing price
            # 
            # hist['vol_std_macd_' + str(window_fast) + '_' + str(window_slow)] = (hist['ema_' + str(window_fast)] - hist['ema_' + str(window_slow)])/hist['vol_std_' + str(window_slow)]
            # hist['vol_std_new_macd' + str(window_fast) + '_' + str(window_slow)] = (hist['ema_' + str(window_fast)] - hist['ema_' + str(window_slow)])/hist['vol_std_' + str(window_fast)]

            hist['vol_std_pct_ratio_' + str(window_fast) + '_' + str(window_slow)] = (hist['vol_std_' + str(window_fast)]/hist['ema_' + str(window_fast)])/(hist['vol_std_' + str(window_slow)]/hist['ema_' + str(window_slow)])
            #hist['vol_std_pct_macd_ratio_' + str(window_fast) + '_' + str(window_slow)] = (hist['vol_std_' + str(window_fast)]/hist['ema_' + str(window_fast)])/(hist['vol_std_' + str(window_slow)]/hist['ema_' + str(window_slow)])

    # ATRs


    # # swing low/ high
    # hist['swing_low_50'] = hist.close.rolling(50).min()
    # hist['swing_high_50'] = hist.close.rolling(50).max()

    # RSI

    # # sma
    # returns ema
    hist['returns_EMA_20'] = hist.returns.ewm(20).mean()
    hist['returns_EMA_50'] = hist.returns.ewm(50).mean()
    hist['returns_EMA_80'] = hist.returns.ewm(80).mean()
    hist['returns_EMA_200'] = hist.returns.ewm(200).mean()
    hist['returns_EMA_1200'] = hist.returns.ewm(1200).mean()

    # candle features
    hist['candle'] = hist.close - hist.open
    hist['candle_pct'] = (hist.close - hist.open) / hist.open * 100


    # Combined indicators, crossovers, entry/exit signals
    # hist['Close_EMA_10'] = np.where(hist.close > hist.ema1, 1, 0)
    #hist['Close_SMA_50'] = np.where(hist.close > hist.sma50, 1, 0)

    # hist['EMA_10_EMA_30'] = np.where(hist.ema1 > hist.ema2, 1, 0)

    # hist['overbought_14_70'] = np.where(hist.RSI_14 > 70, 1, 0)
    # hist['oversold_14_30'] = np.where(hist.RSI_14 < 30, 1, 0)
    # hist['overbought_14_60'] = np.where(hist.RSI_14 > 60, 1, 0)
    # hist['oversold_14_40'] = np.where(hist.RSI_14 < 40, 1, 0)

    # hist['overbought_70'] = np.where(hist.RSI > 70, 1, 0)
    # hist['oversold_30'] = np.where(hist.RSI < 30, 1, 0)
    # hist['overbought_60'] = np.where(hist.RSI > 60, 1, 0)
    # hist['oversold_40'] = np.where(hist.RSI < 40, 1, 0)
    if features:
        #return hist.loc[:,features]
        return hist
    else:
        return hist

# def get_select_features(hist: pd.DataFrame, features = None):

#     for i in features:

#         if ('ema_' in i) and (('ema_' + str(window)) not in hist.columns):
#             window = i.split('_')[-1]
#             # EMAs
#             hist['ema_' + str(window)] = ema_indicator(hist.close,window=window)

#         if ('vol_std_' in i) and (('vol_std_' + str(window)) not in hist.columns):
#             window = i.split('_')[-1]
#             # EMAs
#             hist['vol_std_' + str(window)] = hist.close.ewm(window).std()

#         if 'ema_vol_std' in i:
#             window = i.split('_')[-1]

#             # close_ema_vol_std
#             hist['ema_vol_std_' + str(window)] = (hist.close - hist['ema_' + str(window)]) / hist['vol_std_' + str(window)]
        
#         if 'vol_std_pct' in i:

#         if 'ema_vol_std_shift' in i:

#         hist['vol_std_shift_' + str(i)] = (hist['ema_' + str(i)] - hist['ema_' + str(i)].shift(i))/ hist['vol_std_' + str(i)]

#             # in addition, we want some metric of changing volatility
#             # for example, in a very volatile time window 1 std may mean 0.01% change, but in a low volatility time window it may be 0.001
#             # this is important as if we expect a positive trend of one std from the previous time it needs to be comparable to the current std.
#             #

#             # volatility pct
#             hist['vol_std_pct' + str(i)] = hist['vol_std_' + str(i)]/hist['ema_' + str(i)]
#             hist['vol_std_pct_ratio' + str(i)] = hist['vol_std_pct' + str(i)]/ hist['vol_std_pct' + str(i)].shift(i)

