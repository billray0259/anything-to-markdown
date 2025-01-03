from dash import html, dcc, no_update
from dash.dependencies import Input, Output, State

import base64

from .util import detect_file_type, parse_contents

def register_callbacks(app):

    @app.callback(
        Output("collapse", "is_open"),
        Output("caret-icon", "className"),
        [Input("collapse-button", "n_clicks")],
        [State("collapse", "is_open")],
    )
    def toggle_collapse(n, is_open):
        if n:
            is_open = not is_open
            icon_class = "bi bi-caret-up-fill me-2" if is_open else "bi bi-caret-down-fill me-2"
            return is_open, icon_class
        return is_open, "bi bi-caret-down-fill me-2"

    @app.callback(
        [Output('openai-api-key', 'style'), Output('model-dropdown', 'style'), Output('openai-api-key-label', 'style'), Output('model-dropdown-label', 'style')],
        [Input('method-dropdown', 'value')]
    )
    def toggle_openai_settings(method):
        if method == 'openai':
            return {'display': 'block'}, {'display': 'block'}, {'display': 'block'}, {'display': 'block'}
        return {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}

    @app.callback(
        [Output('upload-data', 'children'), Output('convert-button', 'disabled')],
        [Input('upload-data', 'contents')],
        [State('upload-data', 'filename')]
    )
    def update_upload_component(contents, filename):
        if contents is None or filename is None:
            return no_update, True
        
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        file_type = detect_file_type(decoded)
        
        file_info = html.Div([
            html.Span(f"File: {filename} (Type: {file_type})"),
            html.A('Replace File', style={'marginLeft': '10px'})
        ])
        return file_info, False

    @app.callback(
        [Output('plaintext-output', 'children'), Output('html-output', 'children'), Output('download-button', 'style')],
        [Input('convert-button', 'n_clicks')],
        [State('upload-data', 'contents'), State('upload-data', 'filename'), State('method-dropdown', 'value'), State('openai-api-key', 'value'), State('model-dropdown', 'value')]
    )
    def update_output(n_clicks, contents, filename, method, api_key, model):
        if n_clicks == 0 or contents is None or filename is None:
            return no_update, no_update, {'display': 'none'}
        
        markdown_content = parse_contents(contents, filename, method, api_key, model)
        html_render = dcc.Markdown(markdown_content)
        codeblock = html.Pre(markdown_content)
        return codeblock, html_render, {'display': 'block'}

    @app.callback(
        Output('download-button', 'href'),
        Output('download-button', 'download'),
        [Input('convert-button', 'n_clicks')],
        [State('upload-data', 'contents'), State('upload-data', 'filename'), State('method-dropdown', 'value'), State('openai-api-key', 'value'), State('model-dropdown', 'value')]
    )
    def update_download_link(n_clicks, contents, filename, method, api_key, model):
        if n_clicks == 0 or contents is None or filename is None:
            return no_update, no_update
        
        markdown_content = parse_contents(contents, filename, method, api_key, model)
        markdown_bytes = markdown_content.encode('utf-8')
        b64 = base64.b64encode(markdown_bytes).decode('utf-8')
        download_href = f"data:text/markdown;base64,{b64}"
        download_filename = filename.rsplit('.', 1)[0] + '.md'
        return download_href, download_filename

    @app.callback(
        [Output('plaintext-output', 'style'), Output('html-output', 'style')],
        [Input('render-as-html-switch', 'value')]
    )
    def toggle_output_display(render_as_html):
        if render_as_html:
            return {'display': 'none'}, {'display': 'block'}
        return {'display': 'block'}, {'display': 'none'}

    return app