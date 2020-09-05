import plotly.graph_objs as go
import pandas as pd


# Moving average
def moving_average_trace(df):
    df2 = df.set_index('Date')
    df2 = df2.rolling(window=5).mean()
    trace = go.Scatter(
        x=df["Date"], y=df2["Close"], mode="lines", showlegend=True, name="MA"
    )
    return trace


# Exponential moving average
def e_moving_average_trace(df):
    df2 = df.set_index('Date')
    df2 = df2.rolling(window=20).mean()
    trace = go.Scatter(
        x=df["Date"], y=df2["Close"], mode="lines", showlegend=True, name="EMA"
    )
    return trace




# Bollinger Bands
def bollinger_trace(df, window_size=10, num_of_std=5):
    price = df["Close"]
    rolling_mean = price.rolling(window=window_size).mean()
    rolling_std = price.rolling(window=window_size).std()
    upper_band = rolling_mean + (rolling_std * num_of_std)
    lower_band = rolling_mean - (rolling_std * num_of_std)

    trace = go.Scatter(
        x=df["Date"], y=upper_band, mode="lines", showlegend=True, name="BB_upper"
    )

    trace2 = go.Scatter(
        x=df["Date"], y=rolling_mean, mode="lines", showlegend=True, name="BB_mean"
    )

    trace3 = go.Scatter(
        x=df["Date"], y=lower_band, mode="lines", showlegend=True, name="BB_lower"
    )
    return [trace, trace2, trace3]


# Pivot points
def pp_trace(df):
    PP = pd.Series((df["High"] + df["Low"] + df["Close"]) / 3)
    R1 = pd.Series(2 * PP - df["Low"])
    S1 = pd.Series(2 * PP - df["High"])
    R2 = pd.Series(PP + df["High"] - df["Low"])
    S2 = pd.Series(PP - df["High"] + df["Low"])
    R3 = pd.Series(df["High"] + 2 * (PP - df["Low"]))
    S3 = pd.Series(df["Low"] - 2 * (df["High"] - PP))
    trace = go.Scatter(x=df["Date"], y=PP, mode="lines", showlegend=True, name="Pivot points PP")
    trace1 = go.Scatter(x=df["Date"], y=R1, mode="lines", showlegend=True, name="Pivot points R1")
    trace2 = go.Scatter(x=df["Date"], y=S1, mode="lines", showlegend=True, name="Pivot points S1")
    trace3 = go.Scatter(x=df["Date"], y=R2, mode="lines", showlegend=True, name="Pivot points R2")
    trace4 = go.Scatter(x=df["Date"], y=S2, mode="lines", showlegend=True, name="Pivot points S2")
    trace5 = go.Scatter(x=df["Date"], y=R3, mode="lines", showlegend=True, name="Pivot points R3")
    trace6 = go.Scatter(x=df["Date"], y=S3, mode="lines", showlegend=True, name="Pivot points S3")
    return trace, trace1, trace2, trace3, trace4, trace5, trace6


# Volume Weighted Average Price
def volume_weighted_average_price_trace(df, ndays=5):
    TP = (df["High"] + df["Low"] + df["Close"]) / 3
    PV = TP*df['Volume']

    # 3 total price * volume
    total_pv = PV.rolling(ndays, min_periods=1).sum()
    # 4 total volume
    total_volume = df['Volume'].rolling(ndays, min_periods=1).sum()
    vwap = total_pv / total_volume
    vwap_series = pd.Series(vwap, name="vwap")
    trace = go.Scatter(x=df["Date"], y=vwap_series, mode="lines", showlegend=True, name="VWAP")
    return trace


# Stochastic oscillator %K
def stoc_trace(df):
    SOk = pd.Series((df["Close"] - df["Low"]) / (df["High"] - df["Low"]), name="Stochastic oscillator")
    trace = go.Scatter(x=df["Date"], y=SOk, mode="lines", showlegend=False, name="Stochastic oscillator")
    return trace


def candlestick_trace(df):
    return go.Candlestick(
        x=df["Date"],
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        increasing=dict(line=dict(color="#00ff00")),
        decreasing=dict(line=dict(color="red")),
        showlegend=False,
        name="candlestick",
    )


def scatter_trace(df):
    return go.Scatter(
        x=df["Date"],
        y=df["Close"],
        name="scatter",
        mode='lines+markers'
    )


def emasma_trace(df):
    df1 = df.set_index('Date')
    df1 = df1.rolling(window=5).mean()

    df2 = df.set_index('Date')
    df2 = df2.rolling(window=20).mean()

    return go.Scatter(
        x=df1["Close"],
        y=df2["Close"],
        name="scatter",
        mode='lines+markers',
        hovertext=df['Date']
    )



def OHLC_trace(df):
    return go.Ohlc(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    )
