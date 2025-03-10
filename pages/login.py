import dash
import dash_bootstrap_components as dbc
import pandas as pd

from datetime import datetime

from dash import html, dcc, callback, Input, Output, State, callback_context, ctx
from flask_login import login_user, logout_user, UserMixin, current_user
from flask import session
from config.config import DB_CONFIG
from sqlalchemy import create_engine, text
from flask import session


db_connection_str = create_engine(f"mysql+pymysql://{DB_CONFIG['username']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}")
# engine = create_engine(db_connection_str)  # Keep connection alive

dash.register_page(__name__, path="/")

# Simple User class
class User(UserMixin):
    def __init__(self, username, role = 'user'):
        self.id = username
        self.role = role

layout = dbc.Container(
    dbc.Row(
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H2("Please log in to continue", className="text-center mb-4"),
                    dbc.InputGroup([
                        dbc.InputGroupText("Username"),
                        dbc.Input(placeholder="Enter your username", type="text", id="uname-box"),
                    ], className="mb-3"),
                    dbc.InputGroup([
                        dbc.InputGroupText("Password"),
                        dbc.Input(placeholder="Enter your password", type="password", id="pwd-box"),
                    ], className="mb-3"),
                    dbc.Button("Login", id="login-button", color="primary", className="w-100 mb-2"),
                    dbc.Button("Logout", id="logout-button", color="danger", className="w-100 mb-2"),
                    dbc.Button("Register", id="register-button", color="secondary", className="w-100 mb-2"),
                    dcc.Location(id="login-redirect", refresh=True),
                    html.Div(id="output-state", className="text-center text-danger mt-2"),
                    dcc.Interval(id='activity-check', interval=60000, n_intervals=0),  # Checks every 60 sec
                    dcc.Location(id='redirect', refresh=True),  # Handles redirection
                ]),
                className="shadow p-4",
            ),
            width=4
        ),
        className="justify-content-center align-items-center vh-100"
    ),
    fluid=True,
    className="bg-light"
)

@callback(
    [Output('login-redirect', 'pathname'), Output('output-state', 'children')],
    [Input('login-button', 'n_clicks'),
     Input('logout-button', 'n_clicks'),
     Input('register-button', 'n_clicks')],
    [State('uname-box', 'value'), State('pwd-box', 'value')],
    prevent_initial_call=True
)
def login_button_click(login, logout, register, username, password):
    triggered_id = ctx.triggered_id  # Modern way to get triggered input
    
    if triggered_id == "login-button":
        if not username or not password:
            return dash.no_update, "Please enter both username and password"

        try:
            with db_connection_str.connect() as connection:
                query = text("SELECT password, role FROM login_id WHERE user = :username")
                result = connection.execute(query, {"username": username}).fetchone()

                if result:
                    db_password, user_role = result  # Unpack tuple
                    
                    if password == db_password:  # Simple check (hashing recommended)
                        user = User(username)   
                        login_user(user)
                        session["role"] = user_role  # Store role in session

                        time_in = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Get current timestamp
                        insert_query = text("INSERT INTO login_history (user, time_in) VALUES (:username, :time_in)")
                        connection.execute(insert_query, {"username": username, "time_in": time_in})
                        connection.commit()  # Commit transaction

                        return "/home", ""  # Redirect to home page
                    else:
                        return dash.no_update, "Incorrect username or password"
                else:
                    return dash.no_update, "User not found"
        
        except Exception as e:
            return dash.no_update, f"Error: {str(e)}"
    
    elif triggered_id == "logout-button":
        if current_user.is_authenticated:
            username = current_user.id  # Save username before logout
            time_out = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            try:
                with db_connection_str.connect() as connection:
                    update_query = text("""
                        UPDATE login_history
                        SET time_out = :time_out
                        WHERE user = :username AND time_out IS NULL
                        ORDER BY time_in DESC
                        LIMIT 1
                    """)
                    connection.execute(update_query, {"username": username, "time_out": time_out})
                    connection.commit()
                
                # Logout AFTER updating database
                logout_user()
                session.clear()  # Clear Flask session

                print(f"User {username} logged out at {time_out}")  # Debugging log
                return "/", ""  # Redirect to login page
            
            except Exception as e:
                print(f"Error updating logout time: {str(e)}")
                return dash.no_update, "Error logging out"
        
        return dash.no_update, "You are not logged in"


    elif triggered_id == "register-button":
        return "/register", ""


@callback(
    Output('redirect', 'pathname'),
    Input('activity-check', 'n_intervals'),
    prevent_initial_call=True
)
def check_user_timeout(n):
    if current_user.is_authenticated:
        last_active = session.get("last_active", datetime.datetime.utcnow())

        # Check if timeout exceeded
        if (datetime.datetime.utcnow() - last_active).total_seconds() > 18000:  # 30 min
            username = current_user.id  # Save username before logout
            time_out = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Update database
            try:
                with db_connection_str.connect() as connection:
                    update_query = text("""
                        UPDATE login_history
                        SET time_out = :time_out
                        WHERE user = :username AND time_out IS NULL
                        ORDER BY time_in DESC
                        LIMIT 1
                    """)
                    connection.execute(update_query, {"username": username, "time_out": time_out})
                    connection.commit()
            except Exception as e:
                print(f"Error updating timeout: {str(e)}")

            # Logout user
            logout_user()
            session.clear()
            print(f"User {username} timed out at {time_out}")

            return "/"  # Redirect to login page
    
    # Update last active time
    session["last_active"] = datetime.datetime.utcnow()
    return dash.no_update