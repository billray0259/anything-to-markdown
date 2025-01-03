# dash_app/layout.py

import dash_bootstrap_components as dbc
from dash import html, dcc

def create_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("PDF to Markdown Converter"), className="text-center")
        ]),
        dbc.Row([
            dbc.Col(dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                multiple=False
            ), width=12)
        ]),
        dbc.Row([
            dbc.Col(dbc.Button(
                id="convert-button",
                color="primary",
                n_clicks=0,
                children="Convert",
                disabled=True
            ), width=4, className='mb-2'),
            dbc.Col(dbc.Button(
                id="collapse-button",
                color="primary",
                n_clicks=0,
                children=[
                    html.I(className="bi bi-caret-down-fill me-2", id="caret-icon"),
                    "Settings"
                ],
            ), width=4, className='mb-2'),
            dbc.Col(dbc.Button(
                id="download-button",
                color="success",
                n_clicks=0,
                children="Download Markdown",
                style={'display': 'none'}
            ), width=4, className='mb-2')
        ]),
        dbc.Row([
            dbc.Col(dbc.Collapse(
                dbc.Card([
                    dbc.CardBody([
                        dbc.Form([
                            dbc.Label("Method"),
                            dcc.Dropdown(
                                id='method-dropdown',
                                options=[
                                    {'label': 'MarkItDown', 'value': 'markitdown'},
                                    {'label': 'OpenAI Vision Model', 'value': 'openai'},
                                    # {'label': 'Pypandoc', 'value': 'pypandoc'}
                                ],
                                value='markitdown'
                            )
                        ]),
                        dbc.Form([
                            dbc.Label("OpenAI API Key", id='openai-api-key-label', style={'display': 'none'}),
                            dbc.Input(
                                id='openai-api-key',
                                type='text',
                                placeholder='Enter OpenAI API Key',
                                style={'display': 'none'}
                            )
                        ]),
                        dbc.Form([
                            dbc.Label("Model", id='model-dropdown-label', style={'display': 'none'}),
                            dcc.Dropdown(
                                id='model-dropdown',
                                options=[
                                    {'label': 'GPT-4o mini', 'value': 'gpt-4o-mini'},
                                    {'label': 'GPT-4o', 'value': 'gpt-4o'},
                                ],
                                style={'display': 'none'},
                                value='gpt-4o-mini'
                            )
                        ]),
                        dbc.Form([
                            dbc.Checklist(
                                options=[
                                    {"label": "Render as HTML", "value": 1},
                                ],
                                value=[],
                                id="render-as-html-switch",
                                switch=True,
                            ),
                        ])
                    ]) 
                ]),
                id="collapse",
                is_open=False
            ), width=12)
        ]),
        dbc.Row([
            dbc.Col(dcc.Loading(html.Div(
                [
                    html.Div('Upload a document to convert to Markdown', id='plaintext-output', style={'display': 'none',}),
                    html.Div('Upload a document to convert to Markdown', id='html-output', style={'display': 'none'}),
                ], style={
                    'width': '100%',
                    'borderWidth': '1px',
                    'borderStyle': 'solid',
                    'borderRadius': '5px',
                    'margin': '10px',
                    'padding': '10px',
                })), width=12),
        ]),
    ])