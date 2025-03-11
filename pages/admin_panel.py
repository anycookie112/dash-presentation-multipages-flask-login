import dash
from dash import Dash, html
import dash_bootstrap_components as dbc
from flask_login import current_user
import dash_ag_grid as dag
import pandas as pd
from config.config import DB_CONFIG
from sqlalchemy import create_engine

# Register the page
dash.register_page(__name__, path='/admin_panel')


db_connection_str = create_engine(f"mysql+pymysql://{DB_CONFIG['username']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}")

def fetch_data():  

    # Query the database
    query = """
        select * from login_history
    """

    # Run query and load into a DataFrame
    with db_connection_str.connect() as connection:
        df = pd.read_sql(query, connection)
    data_excluded = df.drop(columns=['time_out'], errors='ignore')
    return data_excluded

df = fetch_data()

login_history = dag.AgGrid(
            id="login_data",  # Unique ID per page
            rowData=df.to_dict("records"),
            dashGridOptions={'rowSelection': 'single', 'defaultSelected': [0]},
            columnDefs=[{"field": i} for i in df.columns],
            columnSize="sizeToFit",
        )

def layout():
    # If the user is not logged in, show login prompt
    if not current_user.is_authenticated:
        print("User is not authenticated")
        return dbc.Container(
            dbc.Alert(
                [
                    html.H4("Access Denied", className="alert-heading"),
                    html.P("You must be logged in to view this page."),
                    html.A("Login here", href="/", className="alert-link")
                ],
                color="danger",
                className="text-center mt-5"
            ),
            className="vh-100 d-flex align-items-center justify-content-center"
        )

    print(f"Current User: {repr(current_user.id)}, Role: {getattr(current_user, 'role', 'No role')}")

    if not hasattr(current_user, "role") or current_user.role != "admin": 
        print("Permission Denied")
        return dbc.Container(
            dbc.Alert(
                [
                    html.H4("Permission Denied", className="alert-heading"),
                    html.P("You do not have permission to view this page."),
                    html.A("Go to Home", href="/", className="alert-link")
                ],
                color="warning",
                className="text-center mt-5"
            ),
            className="vh-100 d-flex align-items-center justify-content-center"
        )
    
    return html.Div([
    login_history
])