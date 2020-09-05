import dash
import dash_core_components as dcc
import dash_html_components as html
import colorlover as cl
import dash_bootstrap_components as dbc
from stock_trace import *
import pandas as pd
import datetime
import webbrowser
pd.core.common.is_list_like = pd.api.types.is_list_like
from pandas_datareader import data as dr

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[
                    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
                ])
app.scripts.config.serve_locally = False
colorscale = cl.scales['9']['qual']['Paired']
server = app.server

### WEB LAYOUT AND COMPONENT ##

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa"
}

sidebar = html.Div(
    [
        html.H2("Tools", className="display-4"),

        html.Hr(),
        dbc.Button(
            "Indicator options", outline=True, color="info", className="lead", id="indicator-toggle", block=True,
        ),
        html.Div([html.H2()]),
        dbc.Collapse([
            dbc.Button("Bollinger Band", color="info", id="bollinger-button", className="stock-indices", block=True),
            dbc.Button("Moving Average", color="info", id="ma-button", className="stock-indices", block=True),
            dbc.Button("Exponential Moving Average", color="info", id="ema-button", className="stock-indices",
                       block=True),
            dbc.Button("Pivot Points", color="info", id="pp-button", className="stock-indices", block=True),
            dbc.Button("Volume Weighted Average Price", color="info", id="vwap-button", className="stock-indices",
                       block=True),
        ], id="indicator-collapse"
        ),
        html.Hr(),
        dbc.Button(
            "Chart options", outline=True, color="secondary", className="lead", id="chart-toggle", block=True,
        ),
        html.Div([html.H2()]),
        dbc.Collapse([
            dbc.Button("Candlestick graph", color="secondary", id="candle-button", className="chart-view", block=True),
            dbc.Button("line graph", color="secondary", id="scatter-button", className="chart-view", block=True),
            dbc.Button("OHLC graph", color="secondary", id="OHLC-button", className="chart-view", block=True),
        ], id="chart-collapse"),
        html.Hr(),
        dbc.Button(
            "Time options", outline=True, color="primary", className="lead", id="time-toggle", block=True,
        ),
        html.Div([html.H2()]),
        dbc.Collapse([
            dbc.Button("Week view", color="primary", id="week-button", className="time-view", block=True),
            dbc.Button("Month view", color="primary", id="month-button", className="time-view", block=True),
            dbc.Button("60 Days view", color="primary", id="60d-button", className="time-view", block=True),
            dbc.Button("90 Days view", color="primary", id="90d-button", className="time-view", block=True),
            dbc.Button("180 Days view", color="primary", id="180d-button", className="time-view", block=True),
            dbc.Button("Year view", color="primary", id="year-button", className="time-view", block=True),
        ], id="time-collapse"),

        html.Hr(),
        dbc.Button(
            "Feature options", outline=True, color="danger", className="lead", id="feature-toggle", block=True,
        ),
        html.Div([html.H2()]),
        dbc.Collapse([
            dbc.Button("EMA against SMA", color="danger", id="emasma-button", className="feature-view", block=True),
            dbc.Button("Rule building", color="danger", id="rule-button", className="feature-view", block=True),
        ], id="feature-collapse")
    ],
    style=SIDEBAR_STYLE
)
header = html.Div([
    html.H2('Stock Dashboard',
            style={'display': 'inline',
                   'float': 'left',
                   'font-size': '2.65em',
                   'margin-left': '7px',
                   'font-weight': 'bolder',
                   'font-family': 'Product Sans',
                   'color': "rgba(117, 117, 117, 0.95)",
                   'margin-top': '20px',
                   'margin-bottom': '0'
                   })
])

STOCKS = pd.read_csv("snp500.csv")
stock_menu = dcc.Dropdown(
    id='stock-ticker-input',
    options=[{'label': s[0], 'value': str(s[1])}
             for s in zip(STOCKS["Symbol"], STOCKS["Symbol"])],
    value=['AAPL', 'GOOG'],
    multi=True
)

graph_layout = {
    'margin': {'b': 0, 'r': 10, 'l': 60, 't': 0},
    'legend': {'x': 0}
}

app.layout = html.Div([
    header,
    stock_menu,
    sidebar,
    html.Div(id='graphs')
], className="container")


def get_period_view(stock_name, days):
    now = datetime.datetime.now()
    time_delta = datetime.timedelta(days=days)
    last_week = now - time_delta
    now = now.strftime("%d/%m/%y")
    last_week = last_week.strftime("%d/%m/%y")
    return load_stock(stock_name, last_week, now)


def get_60d_view(stock_name):
    return get_period_view(stock_name, days=60)


def get_90d_view(stock_name):
    return get_period_view(stock_name, days=90)


def get_180d_view(stock_name):
    return get_period_view(stock_name, days=180)


def get_month_view(stock_name):
    return get_period_view(stock_name, days=30)


def get_week_view(stock_name):
    return get_period_view(stock_name, days=7)


def load_stock(stock_name, start='01/02/2019', end='5/9/2020'):
    begins = list(map(int, start.split("/")))[::-1]
    finishs = list(map(int, end.split("/")))[::-1]
    start = datetime.datetime(*begins)
    end = datetime.datetime(*finishs)
    return dr.DataReader(stock_name, 'yahoo', start=start, end=end).reset_index()


####### STUDIES TRACES ######
draw_func = candlestick_trace
time_func = load_stock


@app.callback(
    dash.dependencies.Output('graphs', 'children'), [
        dash.dependencies.Input('stock-ticker-input', 'value'),

        dash.dependencies.Input("bollinger-button", "n_clicks"),
        dash.dependencies.Input("ma-button", "n_clicks"),
        dash.dependencies.Input("ema-button", "n_clicks"),
        dash.dependencies.Input("pp-button", "n_clicks"),
        dash.dependencies.Input("vwap-button", "n_clicks"),

        dash.dependencies.Input("candle-button", "n_clicks"),
        dash.dependencies.Input("scatter-button", "n_clicks"),
        dash.dependencies.Input("OHLC-button", "n_clicks"),

        dash.dependencies.Input("week-button", "n_clicks"),
        dash.dependencies.Input("month-button", "n_clicks"),
        dash.dependencies.Input("60d-button", "n_clicks"),
        dash.dependencies.Input("90d-button", "n_clicks"),
        dash.dependencies.Input("180d-button", "n_clicks"),
        dash.dependencies.Input("year-button", "n_clicks"),
        dash.dependencies.Input("emasma-button", "n_clicks"),
        dash.dependencies.Input("rule-button", "n_clicks"),
    ])
def update_graph(tickers, bollinger_click, ma_click, ema_click, pp_click, vwap_click,
                 candle_click, scatter_click, broken_click,
                 week, month, sixty_days, ninety_days, half_year, year, emasma_click,rule):
    if not tickers:
        return html.H3(
            "Select a stock ticker.",
            style={'marginTop': 20, 'marginBottom': 20})
    # if rule:
    #     webbrowser.open('http://159.138.146.202:8001/')

    # get button pressed
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    global draw_func
    global time_func
    graphs = []

    for i, ticker in enumerate(tickers):
        if "week-button" in changed_id:
            time_func = get_week_view
            dff = time_func(ticker)
        elif "month-button" in changed_id:
            time_func = get_month_view
            dff = time_func(ticker)
        elif "60d-button" in changed_id:
            time_func = get_60d_view
            dff = time_func(ticker)
        elif "90d-button" in changed_id:
            time_func = get_90d_view
            dff = time_func(ticker)
        elif "180d-button" in changed_id:
            time_func = get_180d_view
            dff = time_func(ticker)
        elif "year-button" in changed_id:
            time_func = load_stock
            dff = load_stock(ticker)
        else:
            dff = time_func(ticker)

        if "candle-button" in changed_id:
            draw_func = candlestick_trace
            fig = go.Figure(data=[candlestick_trace(dff)], layout=graph_layout)
        elif "scatter-button" in changed_id:
            draw_func = scatter_trace
            fig = go.Figure(data=[scatter_trace(dff)], layout=graph_layout)
        elif "OHLC-button" in changed_id:
            draw_func = OHLC_trace
            fig = go.Figure(data=[OHLC_trace(dff)], layout=graph_layout)
        else:
            fig = go.Figure(data=[draw_func(dff)], layout=graph_layout)

        # add trace by toggle button
        if ma_click and ma_click % 2:
            fig.add_trace(moving_average_trace(df=dff))

        if bollinger_click and bollinger_click % 2:
            [fig.add_trace(tr) for tr in bollinger_trace(df=dff)]

        if ema_click and ema_click % 2:
            fig.add_trace(e_moving_average_trace(df=dff))

        if pp_click and pp_click % 2:
            [fig.add_trace(tr) for tr in pp_trace(df=dff)]

        if vwap_click and vwap_click % 2:
            fig.add_trace(volume_weighted_average_price_trace(df=dff))

        # override the graph to show indicator feature only
        if "emasma-button" in changed_id:
            fig = go.Figure(data=[emasma_trace(dff)], layout=graph_layout)
            fig.update_layout(
                xaxis_title="SMA",
                yaxis_title="EMA",
                font=dict(
                    family="Courier New, monospace",
                    size=18,
                    color="#7f7f7f"
                )
            )

        graphs.extend([
            html.H2(ticker, className="stock name",
                    style={
                        'font-weight': 'bolder',
                        'font-family': 'Product Sans',
                        'color': "rgba(150, 150, 150, 0.95)"
                    }),
            dcc.Graph(
                id=ticker,
                figure=fig
            ), html.Div([html.H2()])])

    return graphs



@app.callback(
    dash.dependencies.Output("time-collapse", "is_open"),
    [dash.dependencies.Input("time-toggle", "n_clicks")],
    [dash.dependencies.State("time-collapse", "is_open")],
)
def time_collapse(n, is_open):
    return not is_open if n else is_open


@app.callback(
    dash.dependencies.Output("chart-collapse", "is_open"),
    [dash.dependencies.Input("chart-toggle", "n_clicks")],
    [dash.dependencies.State("chart-collapse", "is_open")],
)
def chart_collapse(n, is_open):
    return not is_open if n else is_open


@app.callback(
    dash.dependencies.Output("indicator-collapse", "is_open"),
    [dash.dependencies.Input("indicator-toggle", "n_clicks")],
    [dash.dependencies.State("indicator-collapse", "is_open")],
)
def indicator_collapse(n, is_open):
    return not is_open if n else is_open


@app.callback(
    dash.dependencies.Output("feature-collapse", "is_open"),
    [dash.dependencies.Input("feature-toggle", "n_clicks")],
    [dash.dependencies.State("feature-collapse", "is_open")],
)
def feature_collapse(n, is_open):
    return not is_open if n else is_open


if __name__ == '__main__':
    app.run_server(debug=True, port=8000)
