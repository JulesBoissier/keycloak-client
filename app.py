import os

from dash import Dash, html, callback, Input, Output, State, dcc
import dash_design_kit as ddk
import dash_ag_grid as dag
import dash_bootstrap_components as dbc

import utils.kc_client as kc_client


app = Dash(
    "keycloak-client",
    suppress_callback_exceptions=True,
)

app.title = "keycloak-client"


server = app.server

app.layout = ddk.Block(
    children=[
        # User Creation Modal
        dbc.Modal(
            [
                dbc.ModalHeader("Add a new user to the database..."),
                dbc.ModalBody([
                    html.Div("Username:"),
                    dcc.Input(id="username", type="text", placeholder="Username...", className="mb-2"),

                    html.Div("Email:"),
                    dcc.Input(id="email", type="text", placeholder="Email...", className="mb-2"),

                    html.Div("Roles:"),
                    dcc.Dropdown(['Viewer', 'Developper', 'Admin'], 'Viewer', id='role-dropdown', multi=True),
                ]),
                dbc.ModalFooter([
                    dbc.Button("Create User", id="submit-value", color="success"),
                    dbc.Button("Close", id="close-modal", color="secondary"),
                ])
            ], id="modal", is_open=False
        ),
        dbc.Modal(
            [
                dbc.ModalHeader("Are you sure you want to proceed?"),
                dbc.ModalBody([
                    html.Div("This process can't be reversed!"),
                ]),
                dbc.ModalFooter([
                    dbc.Button("Delete User", id="delete-user", color="success"),
                    dbc.Button("Close", id="close-warning", color="secondary"),
                ])
            ], id="deletion-modal", is_open=False
        ),
        # Buttons Row
        dbc.Row(
            [
                dbc.Col(dbc.Button("Create New User", id="create-user", color="primary"), width="auto"),
                dbc.Col(dbc.Button("Refresh User List", id="refresh-user-list", color="info"), width="auto"),
            ],
            className="mb-3 justify-content-start",  # Adds margin & aligns left
        ),

        # AG Grid Container
        dbc.Row(
            dbc.Col(
                dag.AgGrid(
                    id="keycloak-users",
                    columnDefs=[
                        {"field": "Name", "sortable": True, "flex": 1},
                        {"field": "Email", "sortable": True, "flex": 1},
                        {"field": "Roles", "sortable": True, "flex": 1},
                        {"field": "Delete", "cellRenderer": "Button", "cellRendererParams": {"className": "btn btn-success"}},#, "cellRendererParams": {"buttonText": "Delete"}},
                    ],
                    style={"height": "500px", "width": "100%"},  # Limits height
                ), width=12  # Full-width column
            )
        ),
    ]
)

@callback(
    Output("modal", "is_open", allow_duplicate=True),
    Input("create-user", "n_clicks"),
    State("modal", "is_open"),
    prevent_initial_call=True
)
def open_model(click_data, is_open):
    return True

@callback(
    Output("modal", "is_open", allow_duplicate=True),
    Input("submit-value", "n_clicks"),
    State("username", "value"),
    State("email", "value"),
    State("role-dropdown", "value"),
    prevent_initial_call=True
)
def create_user(click_data, username, email, roles):

    role_mapping = {
        "Viewer": "viewer",
        "Admin": "admin",
        "Developper": "licensed_user"
    }

    if isinstance(roles, list):
        roles = [role_mapping.get(role, role) for role in roles]
    elif isinstance(roles, str):
        role_mapping.get(roles, roles)

    print(f"Creating user: {username}, {email}, {roles}")

    success = kc_client.create_user(
        username = username,
        email = email,
        roles = roles
    )

    print(f"Success: {success}")
    return False

@callback(
    Output("modal", "is_open", allow_duplicate=True),
    Input("close-modal", "n_clicks"),
    prevent_initial_call=True
)
def close_modal(clicked):
    return False  # Close the modal


@callback(
    Output("keycloak-users", "rowData"),
    Input("refresh-user-list", "n_clicks")
)
def refresh_user_list(click_data):
    users = kc_client.list_all_users()
    for user in users:
        user["Delete"] = "Delete"
    return users

@callback(
    Output("deletion-modal", "is_open", allow_duplicate=True),  # Controls modal visibility
    Input("delete-user", "n_clicks"),
    State("keycloak-users", "rowData"),
    State("keycloak-users", "cellClicked"),
    prevent_initial_call=True

)
def handle_delete_user(n_clicks, users, cell_clicked):
    if not cell_clicked or cell_clicked["colId"] != "Delete":
        return
    
    idx = cell_clicked["rowIndex"]
    user = users[idx]

    print(f"Deleting user: {user['Name']}")
    
    user_id = user["ID"]
    kc_client.delete_user(user_id)
    return False

@callback(
    Output("deletion-modal", "is_open", allow_duplicate=True),  # Controls modal visibility
    Input("keycloak-users", "cellClicked"),
    prevent_initial_call=True

)
def toggle_modal(delete_clicks):
    return True

@callback(
    Output("deletion-modal", "is_open", allow_duplicate=True),  # Controls modal visibility
    Input("close-warning", "n_clicks"), 
    prevent_initial_call=True

)
def toggle_modal(delete_clicks):
    return False


if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
