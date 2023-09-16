import numpy as np
import pandas as pd

from datetime import datetime, timedelta
from pytz import timezone


def run_backtest(
        backtest_hist, 
        buy_index, 
        sell_index,
        take_profit_series,
        stop_loss_series, 
        cash = 10000, 
        risk = 0.01,
        holding_period = None,
        min_holding_period = 0,
        hold_on_buy_signal = True,
        sltp = True,
        sltp_update = False):

    starting_cash = cash
    #cash = 0
    position = 0
    buy = 0
    sell = 0
    take_profit = 0
    stop_loss = 0
    buy_price = 0
    wins = []
    losses = []
    trades = []
    duration = 0
    buy_qty = 0
    trade_info = []

    for i in backtest_hist.index:

        price = backtest_hist.loc[i].close
        duration += 1
        market_open = i.replace(hour=9,minute=30,second=0,microsecond=0)
        market_close = i.replace(hour=16,minute=0,second=0,microsecond=0)
        if (i > market_open) & (i < market_close):
            trade_ok = True
        else:
            trade_ok = False

        buy_ok = 0
        sell_ok = 0
        if i in buy_index and position == 0 and trade_ok:
            buy_ok = 1
        # elif ((price > take_profit) | (price < stop_loss) | (i in sell_index) | (duration > holding_period)) & (position > 0) & (not i in buy_index) & trade_ok & (duration > min_holding_period):
        #     sell_ok = 1
        if position > 0:
            if sltp:
                if hold_on_buy_signal:
                    if ((price > take_profit) | (price < stop_loss) | ((i in sell_index) & (duration > min_holding_period)) | (duration > holding_period)) & (position > 0) & (not i in buy_index) & trade_ok:
                        sell_ok = 1
                else:
                    if ((price > take_profit) | (price < stop_loss) | ((i in sell_index) & (duration > min_holding_period)) | (duration > holding_period)) & (position > 0) & trade_ok:
                        sell_ok = 1
                if sltp_update:
                    take_profit = take_profit_series.loc[i]
                    stop_loss = stop_loss_series.loc[i]
            else:
                if (((i in sell_index) & (duration > min_holding_period)) | (duration > holding_period)) & (position > 0) & (not i in buy_index) & trade_ok:
                        sell_ok = 1
        
        if buy_ok:
            buy_qty = (cash * risk)/price
            # fractional for crypto, full for stock
            cash -= buy_qty * price
            buy += 1
            position = buy_qty
            take_profit = take_profit_series.loc[i]
            stop_loss = stop_loss_series.loc[i]
            buy_price = price
            #print(f'buying {buy_qty} bitcoin at {price} price for {buy_qty * price}')
            trade_info = []
            duration = 0

            trade_info.append(i)
            trade_info.append(buy_price)
            trade_info.append(position)
            trade_info.append(stop_loss)
            trade_info.append(take_profit)
        elif sell_ok:
            cash += position * price
            sell += 1
            #print(f'selling {position} bitcoin at {price} price for {position * price}')
            cash_gain = (position * price) - (buy_qty * buy_price)
            #print(f'on this trade we made {cash_gain}')
            position = 0
            returns1 = (price - buy_price) / buy_price
            #print(f'returns are {returns1}')

            if returns1 > 0:
                wins.append(returns1)
            else:
                losses.append(returns1)

            trade_info.append(i)
            trade_info.append(price)
            trade_info.append(cash_gain)
            trade_info.append(returns1)
            trade_info.append(duration)
            trades.append(trade_info)
            duration = 0

        if (position > 0) and (i == market_close):

            cash += price * position
            sell += 1
            cash_gain = (position * price) - (buy_qty * buy_price)
            position = 0
            returns1 = (price - buy_price) / buy_price
            
            trade_info.append(i)
            trade_info.append(price)
            trade_info.append(cash_gain)
            trade_info.append(returns1)
            trade_info.append(duration)
            trades.append(trade_info)
            duration = 0

    if position > 0:
        cash += price * position
        sell += 1
        cash_gain = (position * price) - (buy_qty * buy_price)
        position = 0
        returns1 = (price - buy_price) / buy_price
        
        trade_info.append(i)
        trade_info.append(price)
        trade_info.append(cash_gain)
        trade_info.append(returns1)
        trade_info.append(duration)
        trades.append(trade_info)
        duration = 0
 

    print('Cash money:')
    print(cash)
    print(buy)
    print(sell)
    if buy == 0:
        winrate = 0
    else:
        winrate = len(wins)/buy
    print('Winrate:')
    print(winrate)
    print('Avg win:')
    print(np.mean(wins))
    print('Avg loss:')
    print(np.mean(losses))

    stats = {
    'winrate': winrate,
    'trade_count': buy,
    'win_size': np.mean(wins),
    'loss_size': np.mean(losses), 
    'returns': (cash - starting_cash)/ starting_cash
    }

    trades = pd.DataFrame(trades,columns=['buy_index','buy_price','position','stop_loss','take_profit','sell_index','price','$ gain','returns','holding_duration'])
    return trades, stats

