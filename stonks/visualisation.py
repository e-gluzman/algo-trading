import plotly.graph_objects as go
from plotly import graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import timedelta

def show_boundaries(hist, day = None):
    if day:
        start = pd.to_datetime(day).date()
        end = pd.to_datetime(day).date() + timedelta(days=1)
        view_hist = hist[start:end]
    else:
        view_hist = hist.tail(500)
    #fig = make_subplots(1,2)
    fig = go.Figure(data=go.Scatter(x=view_hist.index,y=view_hist['close'], mode='lines', marker_color='black'))
    fig.add_trace(go.Scatter(x=view_hist.index,y=view_hist['higher_bound'],marker_color='blue',name='high'))
    fig.add_trace(go.Scatter(x=view_hist.index,y=view_hist['lower_bound'],marker_color='blue',name='low'))
    fig.show()

def show_trades(hist, trades, day = None):
    if day:
        start = pd.to_datetime(day).date()
        end = pd.to_datetime(day).date() + timedelta(days=1)
        view_hist = hist[start:end]
    else:
        view_hist = hist.tail(500)

    trades = [trade for trade in trades if trade[0] in view_hist.index]

    fig = go.Figure(data=go.Scatter(x=view_hist.index,y=view_hist['close'], mode='lines', marker_color='black'))

    for i in trades:
        if i[0] in view_hist.index:
            fig.add_vline(i[0], line_color = 'red')
        # add stop loss and take profit here
        if i[3] in view_hist.index:
            fig.add_vline(i[3], line_color = 'green')
            
    fig.show()