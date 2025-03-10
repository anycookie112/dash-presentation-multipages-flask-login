import dash
from dash import html, callback, Output, Input, State
from sqlalchemy import create_engine, text
from config.config import DB_CONFIG
import dash_bootstrap_components as dbc

# db_connection_str = f"mysql+pymysql://{DB_CONFIG['username']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
# dash.register_page(__name__, path='/register')



# # Styled Form
# form = dbc.Card(
#     dbc.CardBody([
#         html.H4("Register", className="text-center mb-4"),
#         dbc.Row(
#             [
#                 dbc.Col(
#                     dbc.InputGroup([
#                         dbc.InputGroupText("Email"),
#                         dbc.Input(type="email", placeholder="Enter email/username", id="login_id"),
#                     ]),
#                     width=12,
#                     className="mb-3",
#                 ),
#                 dbc.Col(
#                     dbc.InputGroup([
#                         dbc.InputGroupText("Password"),
#                         dbc.Input(type="password", placeholder="Enter password", id="login_pass"),
#                     ]),
#                     width=12,
#                     className="mb-3",
#                 ),
#                 dbc.Col(
#                     dbc.Button("Submit", color="primary", className="w-100"),
#                     width=12,
#                     className="text-center",
#                 ),
#             ],
#             className="g-2",
#         ),
#     ]),
#     className="shadow p-4 mx-auto",
#     style={"maxWidth": "400px"},
# )

# # Page Layout
# layout = html.Div(
#     [
#         dbc.Container([form], className="d-flex justify-content-center align-items-center vh-100"),
#     ],
#     className="bg-light",
# )


# @callback(
#     # Output(),
#     Input('login_id', 'children'),
#     Input('login_pass', 'children')
# )

# def register():
#     query = "INSERT INTO login_id (user, password) VALUES(%s, %s, normal)"


# Create database connection string for SQLAlchemy
db_connection_str = f"mysql+pymysql://{DB_CONFIG['username']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
engine = create_engine(db_connection_str)  # Keep connection alive

# Register page
dash.register_page(__name__, path='/register')

# Styled Form
form = dbc.Card(
    dbc.CardBody([
        html.H4("Register", className="text-center mb-4"),
        html.H5("Admin can see your password, so just use a common password", className="text-center mb-4"),
        dbc.Row(
            [
                dbc.Col(
                    dbc.InputGroup([
                        dbc.InputGroupText("Email"),
                        dbc.Input(type="email", placeholder="Enter email/username", id="login_id"),
                    ]),
                    width=12,
                    className="mb-3",
                ),
                dbc.Col(
                    dbc.InputGroup([
                        dbc.InputGroupText("Password"),
                        dbc.Input(type="password", placeholder="Enter password", id="login_pass"),
                    ]),
                    width=12,
                    className="mb-3",
                ),
                dbc.Col(
                    dbc.Button("Submit", id="submit-btn", color="primary", className="w-100"),
                    width=12,
                    className="text-center",
                ),
                html.Div(id="register-output", className="mt-3 text-center text-danger"),  # Output message
            ],
            className="g-2",
        ),
    ]),
    className="shadow p-4 mx-auto",
    style={"maxWidth": "400px"},
)

# Page Layout
layout = html.Div(
    [
        dbc.Container([form], className="d-flex justify-content-center align-items-center vh-100"),
    ],
    className="bg-light",
)

# Callback for handling registration
@callback(
    Output("register-output", "children"),  # To display success/failure message
    Input("submit-btn", "n_clicks"),
    State("login_id", "value"),
    State("login_pass", "value"),
    prevent_initial_call=True
)
def register(n_clicks, username, password):
    if not username or not password:
        return "Please enter both username and password."

    try:
        with engine.connect() as conn:
            # Check if user already exists
            check_query = text("SELECT * FROM login_id WHERE user = :username")
            result = conn.execute(check_query, {"username": username}).fetchone()

            if result:
                return "Username already exists. Try a different one."

            # Insert new user
            insert_query = text("INSERT INTO login_id (user, password) VALUES (:username, :password)")
            conn.execute(insert_query, {"username": username, "password": password})
            conn.commit()

            return "Registration successful! You can now log in."

    except Exception as e:
        return f"Error: {str(e)}"