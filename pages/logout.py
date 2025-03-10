import dash
from dash import callback, html, dcc
from flask_login import logout_user
from dash.dependencies import Input, Output
from config.config import DB_CONFIG
from datetime import datetime
from flask_login import logout_user, current_user
from sqlalchemy import text
from flask import session

db_connection_str = f"mysql+pymysql://{DB_CONFIG['username']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
dash.register_page(__name__, path='/logout')

layout = html.Div([
    dcc.Location(id="logout-redirect", refresh=True),  # Auto-redirect
    html.H1("Logging Out...", className="text-center"),
    html.Div("You will be redirected shortly.", className="text-center"),
])

# @callback(
#     [Output('logout-redirect', 'pathname', allow_duplicate=True), Output('output-state', 'children',allow_duplicate=True)],
#     Input('logout-button', 'n_clicks'),
#     prevent_initial_call=True
# )
# def logout_button_click(logout):
#     if current_user.is_authenticated:
#         try:
#             with db_connection_str.connect() as connection:
#                 time_out = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#                 # Update latest session where time_out is NULL
#                 update_query = text("""
#                     UPDATE login_history
#                     SET time_out = :time_out
#                     WHERE user = :username AND time_out IS NULL
#                     ORDER BY time_in DESC
#                     LIMIT 1
#                 """)
#                 connection.execute(update_query, {"username": current_user.id, "time_out": time_out})
#                 connection.commit()

#             # Flask-Login logout
#             logout_user()
#             session.clear()  # Clear Flask session

#             print(f"User {current_user.id} logged out at {time_out}")  # Debugging log
#             return "/", "Successfully logged out!"  # Redirect to login page

#         except Exception as e:
#             print(f"Error updating logout time: {str(e)}")
#             return dash.no_update, "Error logging out"

#     return dash.no_update, "You are not logged in"