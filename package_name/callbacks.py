from dash.dependencies import Input, Output, State, ALL
from dash import dcc, html, callback_context, no_update
import dash_bootstrap_components as dbc


def register_callbacks(app):

    @app.callback(
        Output("output", "children"),
        [Input("input", "value")],
    )
    def update_output(value):
        return value