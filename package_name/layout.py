# dash_app/layout.py

import dash_bootstrap_components as dbc
from dash import html, dcc

def create_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Hello, Dash!"),
                dcc.Input(id="input", type="text", placeholder="Enter some text"),
                html.Div(id="output"),
            ]),
        ]),
    ])