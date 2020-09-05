import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_table
import dash_daq as daq
import pandas as pd

pd.core.common.is_list_like = pd.api.types.is_list_like
from pandas_datareader import data as dr
import pandas as pd

from app import app

def load_stock(stock_name, start='1/2/2019', end='20/4/2020'):
    return dr.DataReader(stock_name, 'yahoo', start=start, end=end).reset_index()

def bollinger_trace(df, window_size=10, num_of_std=5):
    price = df["Close"]
    rolling_mean = price.rolling(window=window_size).mean()
    rolling_std = price.rolling(window=window_size).std()
    upper_band = rolling_mean + (rolling_std * num_of_std)
    lower_band = rolling_mean - (rolling_std * num_of_std)
    return upper_band, rolling_mean, lower_band


df_builder = load_stock("AAPL")

params = ["Bollinger band", "Moving average"]

selected_indicator = params[1]

states=[("metric-select-dropdown", "value"),
        ("value-setter-panel", "children"),
        ("value-setter-store", "data"),
        ("value-setter-set-btn", "n_clicks"),
        ("value-setter-view-btn", "n_clicks"),
        ("value-setter-view-output", "children")]

def build_tabs():
    return html.Div(
        id="tabs",
        className="tabs",
        children=[
            dcc.Tabs(
                id="app-tabs",
                value="tab2",
                className="custom-tabs",
                children=[
                    build_spec_tab()
                ],
            )
        ],
    )


def build_spec_tab():
    return dcc.Tab(
        id="Specs-tab",
        label="Indicator Settings",
        value="tab1",
        className="custom-tab",
        selected_className="custom-tab--selected",
    )


def build_header():
    return html.Div(
        id="banner-text",
        children=[
            html.H5("Indicator rule building - AAPL"),
            html.H6("Real-time rule building interface"),
        ],
    )

def build_top():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            build_header()
        ],
    )

def create_alert():
    return html.Div(
        [
            dbc.Alert(
                [
                    "Please select an indicator first",
                ],
                color="primary",
            ),
        ]
    )


def load_df():
    result = {}
    upper, mean, lower = bollinger_trace(df_builder)
    df2 = df_builder.set_index('Date')
    df2 = df2.rolling(window=5).mean()
    result["Bollinger band"] = {
        "count": len(upper),
        'upper-band': upper,
        'mean-band': mean,
        'lower-band': lower,
        'data-mean': mean.describe()["mean"],
        'data-upper': upper.describe()["mean"],
        'data-lower': lower.describe()["mean"],
        "upper-bound": 0,
        "mean-bound": 0,
        "lower-bound": 0,
    }
    stats = df2["Close"].describe()
    result["Moving average"] = {
        "count": len(df2),
        "average": df2["Close"],
        'data-upper': stats["mean"] + stats["std"],
        'data-lower': stats["mean"] - stats["std"],
        "upper-bound": 0,
        "lower-bound": 0
    }
    return result


value_state = load_df()


def build_dropdown():
    return [html.Label(id="metric-select-title", children="Select Metrics"),
            html.Br(),
            dcc.Dropdown(
                id="metric-select-dropdown",
                options=list(
                    {"label": param, "value": param} for param in params
                ),
                value="Select an indicator...",
            )]


def build_buttons():
    return [html.Button("AND Operation", id="and-btn"),
            html.Button("OR Operation", id="or-btn"),
            html.Button("Update rules", id="value-setter-set-btn"),
            html.Button(
                "View current rules",
                id="value-setter-view-btn",
                n_clicks=0,
            ), ]


def build_tab_1():
    return [
        html.Div(
            children=html.P(
                "Multiple stock indicators rule building interface"
            ),
        ),
        html.Div(
            children=[
                html.Div(
                    children=build_dropdown(),
                ),
                html.Div(
                    id="value-setter-menu",
                    children=[
                        html.Div(id="value-setter-panel"),
                        html.Br(),
                        html.Div(
                            id="button-div",
                            children=build_buttons(),
                        ),
                        html.Div(
                            id="value-setter-view-output", className="output-datatable"
                        ),
                        html.Div(
                            id="indicator-operation-output", className="operation-datatable"
                        ),

                    ],
                ),
            ],
        ),
    ]


ud_ul_input = daq.NumericInput(
    id="ud_ul_input", className="setting-input", size=200, max=9999999, value=0
)
ud_ll_input = daq.NumericInput(
    id="ud_ll_input", className="setting-input", size=200, max=9999999, value=0
)
ud_ml_input = daq.NumericInput(
    id="ud_ml_input", className="setting-input", size=200, max=9999999, value=0
)


def build_value_setter_line(line_num, label, value, col3):
    return html.Div(
        [html.Label(label, className="four columns"),
         html.Label(value, className="four columns"),
         html.Div(col3, className="four columns"),
         ]
        , id=line_num,
        className="row",
    )


def generate_section_banner(title):
    return html.Div(className="section-banner", children=title)

rule_builder=html.Div(
    id="big-app-container",
    children=[
        build_top(),
        html.Div(
            id="app-container",
            children=[
                build_tabs(),
                html.Div(id="app-content"),
            ],
        ),
        dcc.Store(id="value-setter-store", data=value_state)
    ],

)
@app.callback(
    Output("app-content", "children"),
    [Input("app-tabs", "value")],
)
def render_tab(tab_switch):
    return build_tab_1()

@app.callback(
    output=Output(*states[1]),
    inputs=[Input(*states[0])],
)
def build_panel(selected):
    global selected_indicator
    if selected == params[0]:
        selected_indicator = params[0]
        return (
            [
                build_value_setter_line(
                    "value-setter-panel-header",
                    "Indicator",
                    "Current value",
                    "Set condition value",
                ),
                build_value_setter_line(
                    "value-setter-panel-ul",
                    "Upper band limit",
                    value_state[selected]["data-upper"],
                    ud_ul_input,
                ),
                build_value_setter_line(
                    "value-setter-panel-ml",
                    "mean band limit",
                    value_state[selected]["data-mean"],
                    ud_ml_input,
                ),
                build_value_setter_line(
                    "value-setter-panel-ll",
                    "lower band limit",
                    value_state[selected]["data-lower"],
                    ud_ll_input,
                ),
            ]
        )
    if selected == params[1]:
        selected_indicator = params[1]
        return (
            [
                build_value_setter_line(
                    "value-setter-panel-header",
                    "Indicator",
                    "Current value",
                    "Set condition value",
                ),
                build_value_setter_line(
                    "value-setter-panel-ul",
                    "Upper limit",
                    value_state[selected]["data-upper"],
                    ud_ul_input,
                ),
                build_value_setter_line(
                    "value-setter-panel-ll",
                    "Lower limit",
                    value_state[selected]["data-lower"],
                    ud_ll_input,
                ),

            ]
        )


@app.callback(
    output=Output(*states[2]),
    inputs=[Input(*states[3])],
    state=[
        State(*states[0]),
        State(*states[2]),
        State(*states[1])
    ]
)
def store(*arg):
    set_btn, param, data = arg[:3]
    if set_btn is None:
        return data
    else:
        div = arg[3]
        if param == params[0]:
            data[param]["upper-bound"] = div[1]['props']['children'][2]['props']['children']['props']['value']
            data[param]["lower-bound"] = div[3]['props']['children'][2]['props']['children']['props']['value']
            data[param]["mean-bound"] = div[2]['props']['children'][2]['props']['children']['props']['value']
        elif param == params[1]:
            data[param]["upper-bound"] = div[1]['props']['children'][2]['props']['children']['props']['value']
            data[param]["lower-bound"] = div[2]['props']['children'][2]['props']['children']['props']['value']
        return data


@app.callback(
    output=Output("indicator-operation-output", "children"),
    inputs=[
        Input("and-btn", "n_clicks"),
        Input("or-btn", "n_clicks"),
        Input(*states[0]),
        Input(*states[2]),
    ],
)
def show_indicator_condition(and_click, or_click, selected, data):
    pass


def default_css():
    return [{"selector": "tr:hover td", "rule": "color: #d5d6dc !important;"},
            {"selector": "td", "rule": "border: none !important;"},
            {
                "selector": ".dash-cell.focused",
                "rule": "background-color: #d5d6dc !important;",
            },
            {"selector": "table", "rule": "--accent: #d5d6dc;"},
            {"selector": "tr", "rule": "background-color: transparent"}]


def default_cell():
    return {
        "fontFamily": "Open Sans",
        "padding": "0 2rem",
        "border": "none",
    }


@app.callback(
    output=Output(*states[5]),
    inputs=[
        Input(*states[4]),
        Input(*states[0]),
        Input(*states[2]),
    ],
)
def show_current_rules(n_clicks, selected, store_data):
    if n_clicks and n_clicks % 2:
        if selected not in params:
            return create_alert()

        data = store_data[selected]
        new_df_dict = {}
        if selected == params[0]:  # bollinger
            new_df_dict = {
                "Indicator": [
                    "Upper band limit",
                    "mean band limit",
                    "lower band limit",
                ],
                "Current Rules": [
                    data["upper-bound"],
                    data["mean-bound"],
                    data["lower-bound"],
                ],
            }
        if selected == params[1]:  # moving average
            new_df_dict = {
                "Indicator": [
                    "Upper limit",
                    "Lower limit",
                ],
                "Current Rules": [
                    data["upper-bound"],
                    data["lower-bound"],
                ],
            }

        new_df = pd.DataFrame.from_dict(new_df_dict)
        return dash_table.DataTable(
            style_header={"fontWeight": "bold", "color": "inherit"},
            style_as_list_view=True,
            fill_width=True,
            style_cell_conditional=[
                {"if": {"column_id": "Specs"}, "textAlign": "left"}
            ],
            style_cell=default_cell(),
            css=default_css(),
            data=new_df.to_dict("rows"),
            columns=[{"id": e, "name": e} for e in ["Indicator", "Current Rules"]],
        )
    else:
        html.Div()
