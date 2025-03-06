import os

from dash import Dash, html, callback, Input, Output, State, dcc
import dash_design_kit as ddk
from gql import gql

# from client import get_client

app = Dash(
    "keycloak-client",
    suppress_callback_exceptions=True,
)

app.title = "keycloak-client"

server = app.server

app.layout = ddk.Block(
    children =
        [
            ddk.Card(children = [
                dcc.Textarea(id="username", value = "", style={'width': '50%', 'height': 50},),
                dcc.Textarea(id="email", value = "", style={'width': '50%', 'height': 50},),
                dcc.Dropdown(['Viewer', 'Developper', 'Admin'], 'NYC', id='role-dropdown'),
                html.Button("Create User", id="create_user", n_clicks = 0),
                ]
            ),
            html.Div(id="output")
        ]
)

# @callback(
#     Output("gql-output", "children"),
#     Input("run-query", "n_clicks"),
#     State("query", "value"),
#     State("variables", "value"),
#     prevent_initial_call = True
# )
# def update_output(n_clicks, query, variables):
#     client = get_client()

#     if not variables:
#         variables = {}

#     try:
#         result = client.execute(gql(query), variable_values = variables)
#         return str(result)
#     except Exception as e:
#         print(f"Error executing query: {str(e)}")
#         return str(e)

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
