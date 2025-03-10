import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table
from dash import Dash, html, dcc, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.subplots as sp

import plotly.graph_objects as go
from plotly.graph_objects import Figure
from plotly.subplots import make_subplots

import dash_ag_grid as dag
import pandas as pd
from sqlalchemy import create_engine
from datetime import date
from config.config import DB_CONFIG

from flask_login import current_user

db_connection_str = f"mysql+pymysql://{DB_CONFIG['username']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"

# db_connection_str = 'mysql+pymysql://admin:UL1131@192.168.1.17/production'
db_connection = create_engine(db_connection_str)

df_spray = pd.read_sql("""
SELECT 
    spray_batch_id AS 'Spray Batch ID', 
    part_name AS 'Part Name', 
    part_code AS 'Part Code', 
    date_sprayed AS 'Date Sprayed',
    total_output AS 'Total Output', 
    unchecked_balance AS 'Unchecked Balance', 
    hundered_balance AS '100 Balance', 
    finished_goods_balance AS '200 Balance',
    total_checked_100 AS 'Total Checked 100',
    total_checked_200 AS 'Total Checked 200'                       

FROM production.spray_batch_info
WHERE unchecked_balance != 0 OR hundered_balance != 0 ;
""", con=db_connection)

df_print = pd.read_sql("""
SELECT 
    print_info_id AS 'Print Batch ID', 
    part_name AS 'Part Name', 
    part_code AS 'Part Code', 
    date_printed AS 'Date Printed',
    total_output AS 'Total Output', 
    secondary_process_balance AS 'P1/P2 Balance', 
    hundered_balance AS '100/P3/P4 Balance', 
    finished_good_balance AS '200 Balance',
    total_checked_p1_p2 AS 'Total Checked P1/P2',
    total_checked_p3_p4_100 AS 'Total Checked 100/P3/P4 Balance',
    total_checked_200 AS 'Total Checked 200'
                       
FROM production.print_batch_info
WHERE secondary_process_balance != 0 OR hundered_balance != 0 ;
""", con=db_connection)



dash.register_page(__name__)

def layout():
    if not current_user.is_authenticated:
        # Show a simple message (or redirect message)
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
    return html.Div([
        dbc.Container(
    [
        # Date picker
        dbc.Row(
            dbc.Col(
                html.Div(
                    dcc.DatePickerRange(id='x'),
                    className="d-flex justify-content-left"  # Center the DatePickerRange
                ),
                width=6,
                className="mt-3 mb-3"
            )
        ),
        
        # Dropdown for part selection
        dbc.Row(
            dbc.Col(
                dcc.Dropdown(
                    id='dd1_balance_spray',
                    options=[],
                    placeholder="Select Parts....",
                ),
                width=6,  # Center with a width of 6 out of 12
                className="mt-3 mb-3"  # Add top and bottom margin
            )
        ),

        dbc.Button("Refresh", 
                   id= "refresh",
                   color="primary", className="mt-3 mb-3"),

        dbc.Row(
            dbc.Col(
                html.H3("Spray Balance", className="text-center mt-3 mb-3"),
                width=12
            )
        ),

        # AgGrid Table
        dbc.Row(
            dbc.Col(
                dag.AgGrid(
                    id='grid_balance',
                    rowData=df_spray.to_dict('records'),
                    columnDefs=[{"field": i} for i in df_spray.columns],
                    style={'height': '400px', 'width': '100%'}
                ),
                width=12,
                className="mb-4"
            )
        ),

        dbc.Row(
            dbc.Col(
                html.H3("Print Balance", className="text-center mt-3 mb-3"),
                width=12
            )
        ),

        # Defect data table
        dbc.Row(
            dbc.Col(
                dcc.Dropdown(
                    id='dd1_balance_print',
                    options=[],
                    placeholder="Select Parts....",
                ),
                width=6,  # Center with a width of 6 out of 12
                className="mt-3 mb-3"  # Add top and bottom margin
            )
        ),

        dbc.Row(
            dbc.Col(
                dcc.Dropdown(
                    id='dd1_balance_print',
                    options=[],
                    placeholder="Select Parts....",
                ),
                width=6,  # Center with a width of 6 out of 12
                className="mt-3 mb-3"  # Add top and bottom margin
            )
        ),

        dbc.Row(
            dbc.Col(
                dag.AgGrid(
                    id='grid_balance_print',
                    rowData=df_print.to_dict('records'),
                    columnDefs=[{"field": i} for i in df_print.columns],
                    style={'height': '400px', 'width': '100%'},  # Adjust grid size
                ),
                width=12,  # Full width of the container
                className="mb-4"  # Add margin-bottom for spacing
            )
        ),

        dcc.Interval(id = 'interval_balance', interval= 10 * 1000, n_intervals = 0)
    ],
    fluid=True  # Makes the container span full width
)
    ])


# layout = dbc.Container(
#     [
#         # Date picker
#         dbc.Row(
#             dbc.Col(
#                 html.Div(
#                     dcc.DatePickerRange(id='x'),
#                     className="d-flex justify-content-left"  # Center the DatePickerRange
#                 ),
#                 width=6,
#                 className="mt-3 mb-3"
#             )
#         ),
        
#         # Dropdown for part selection
#         dbc.Row(
#             dbc.Col(
#                 dcc.Dropdown(
#                     id='dd1_balance_spray',
#                     options=[],
#                     placeholder="Select Parts....",
#                 ),
#                 width=6,  # Center with a width of 6 out of 12
#                 className="mt-3 mb-3"  # Add top and bottom margin
#             )
#         ),

#         dbc.Button("Refresh", 
#                    id= "refresh",
#                    color="primary", className="mt-3 mb-3"),

#         dbc.Row(
#             dbc.Col(
#                 html.H3("Spray Balance", className="text-center mt-3 mb-3"),
#                 width=12
#             )
#         ),

#         # AgGrid Table
#         dbc.Row(
#             dbc.Col(
#                 dag.AgGrid(
#                     id='grid_balance',
#                     rowData=df_spray.to_dict('records'),
#                     columnDefs=[{"field": i} for i in df_spray.columns],
#                     style={'height': '400px', 'width': '100%'}
#                 ),
#                 width=12,
#                 className="mb-4"
#             )
#         ),

#         dbc.Row(
#             dbc.Col(
#                 html.H3("Print Balance", className="text-center mt-3 mb-3"),
#                 width=12
#             )
#         ),

#         # Defect data table
#         dbc.Row(
#             dbc.Col(
#                 dcc.Dropdown(
#                     id='dd1_balance_print',
#                     options=[],
#                     placeholder="Select Parts....",
#                 ),
#                 width=6,  # Center with a width of 6 out of 12
#                 className="mt-3 mb-3"  # Add top and bottom margin
#             )
#         ),

#         dbc.Row(
#             dbc.Col(
#                 dcc.Dropdown(
#                     id='dd1_balance_print',
#                     options=[],
#                     placeholder="Select Parts....",
#                 ),
#                 width=6,  # Center with a width of 6 out of 12
#                 className="mt-3 mb-3"  # Add top and bottom margin
#             )
#         ),

#         dbc.Row(
#             dbc.Col(
#                 dag.AgGrid(
#                     id='grid_balance_print',
#                     rowData=df_print.to_dict('records'),
#                     columnDefs=[{"field": i} for i in df_print.columns],
#                     style={'height': '400px', 'width': '100%'},  # Adjust grid size
#                 ),
#                 width=12,  # Full width of the container
#                 className="mb-4"  # Add margin-bottom for spacing
#             )
#         ),

#         dcc.Interval(id = 'interval_balance', interval= 10 * 1000, n_intervals = 0)
#     ],
#     fluid=True  # Makes the container span full width
# )

# Corrected callback
@callback(
    Output(component_id='dd1_balance_spray', component_property='options'),
    Output(component_id='grid_balance', component_property='rowData'),
    Input(component_id='dd1_balance_spray', component_property='value'),
    Input(component_id='x', component_property='start_date'),  
    Input(component_id='x', component_property='end_date'),
    Input(component_id='interval_balance', component_property='n_intervals'),
    Input(component_id = 'refresh', component_property = 'n_clicks')
) 
def update_dropdown_balance(dd1_balance_spray, start_date, end_date,n, clicks):

    db_connection_str = f"mysql+pymysql://{DB_CONFIG['username']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
    db_connection = create_engine(db_connection_str)

    df_spray = pd.read_sql("""
    SELECT 
        spray_batch_id AS 'Spray Batch ID', 
        part_name AS 'Part Name', 
        part_code AS 'Part Code', 
        date_sprayed AS 'Date Sprayed',
        total_output AS 'Total Output', 
        unchecked_balance AS 'Unchecked Balance', 
        hundered_balance AS '100 Balance', 
        finished_goods_balance AS '200 Balance',
        total_checked_100 AS 'Total Checked 100',
        total_checked_200 AS 'Total Checked 200'                       

    FROM production.spray_batch_info
    WHERE unchecked_balance != 0 OR hundered_balance != 0 ;
    """, con=db_connection)

    df = pd.read_sql('SELECT DISTINCT part_code FROM spray_batch_info WHERE unchecked_balance != 0 OR hundered_balance != 0 ', con=db_connection)

    # Generate dropdown options from the part_codes
    part_code_list = df['part_code'].tolist()
    options = [{'label': code, 'value': code} for code in part_code_list]

    # Start with all data if no part_code is selected
    if not dd1_balance_spray:
        filtered_result_overall = df_spray.copy()  # Start with all data
    else:
        # Filter by the selected part_code
        filtered_result_overall = df_spray[df_spray['Part Code'] == dd1_balance_spray].copy()

    # Ensure 'Date Sprayed' is in datetime format and handle invalid values
    filtered_result_overall['Date Sprayed'] = pd.to_datetime(
        filtered_result_overall['Date Sprayed'], errors='coerce'
    )
    # Drop rows where 'Date Sprayed' could not be converted
    filtered_result_overall = filtered_result_overall.dropna(subset=['Date Sprayed'])

    # If no date range is provided, use the entire dataset
    if start_date is None or end_date is None:
        filtered_table = filtered_result_overall
    else:
        # Convert start_date and end_date to datetime
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # Filter by the date range
        filtered_table = filtered_result_overall[
            (filtered_result_overall['Date Sprayed'] >= start_date) & (filtered_result_overall['Date Sprayed'] <= end_date)
        ]

    # Sort by the most recent `Date Sprayed`
    filtered_table = filtered_table.sort_values(by='Date Sprayed', ascending=False)

    # Format 'Date Sprayed' column to string for display purposes
    filtered_table['Date Sprayed'] = filtered_table['Date Sprayed'].dt.strftime('%Y-%m-%d')

    # Convert filtered table to dictionary format
    table_data = filtered_table.to_dict('records')

    return options, table_data

@callback(
    Output(component_id='dd1_balance_print', component_property='options'),
    Output(component_id='grid_balance_print', component_property='rowData'),
    Input(component_id='dd1_balance_print', component_property='value'),
    Input(component_id='x', component_property='start_date'),  # Corrected ID here
    Input(component_id='x', component_property='end_date'),    # Corrected ID here
    Input(component_id='interval_balance', component_property='n_intervals'),
    Input(component_id = 'refresh', component_property = 'n_clicks')
)
def update_dropdown_balance(dd1_balance_print, start_date, end_date,n, clicks):

    df_print = pd.read_sql("""
    SELECT 
        print_info_id AS 'Print Batch ID', 
        part_name AS 'Part Name', 
        part_code AS 'Part Code', 
        date_printed AS 'Date Printed',
        total_output AS 'Total Output', 
        secondary_process_balance AS 'P1/P2 Balance', 
        hundered_balance AS '100/P3/P4 Balance', 
        finished_good_balance AS '200 Balance',
        total_checked_p1_p2 AS 'Total Checked P1/P2',
        total_checked_p3_p4_100 AS 'Total Checked 100/P3/P4 Balance',
        total_checked_200 AS 'Total Checked 200'
                        
    FROM production.print_batch_info
    WHERE secondary_process_balance != 0 OR hundered_balance != 0 ;
    """, con=db_connection)

    df = pd.read_sql('SELECT DISTINCT part_code FROM print_batch_info WHERE secondary_process_balance != 0 OR hundered_balance != 0 ', con=db_connection)

    # Generate dropdown options from the part_codes
    part_code_list = df['part_code'].tolist()
    options = [{'label': code, 'value': code} for code in part_code_list]

    # Start with all data if no part_code is selected
    if not dd1_balance_print:
        filtered_result_overall = df_print.copy()  # Start with all data
    else:
        # Filter by the selected part_code
        filtered_result_overall = df_print[df_print['Part Code'] == dd1_balance_print].copy()

    # Ensure 'Date Printed' is in datetime format and handle invalid values
    filtered_result_overall['Date Printed'] = pd.to_datetime(
        filtered_result_overall['Date Printed'], errors='coerce'
    )
    # Drop rows where 'Date Printed' could not be converted
    filtered_result_overall = filtered_result_overall.dropna(subset=['Date Printed'])

    # If no date range is provided, use the entire dataset
    if start_date is None or end_date is None:
        filtered_table = filtered_result_overall
    else:
        # Convert start_date and end_date to datetime
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # Filter by the date range
        filtered_table = filtered_result_overall[
            (filtered_result_overall['Date Printed'] >= start_date) & (filtered_result_overall['Date Printed'] <= end_date)
        ]

    # Sort by the most recent `Date Printed`
    filtered_table = filtered_table.sort_values(by='Date Printed', ascending=False)

    # Format 'Date Printed' column to string for display purposes
    filtered_table['Date Printed'] = filtered_table['Date Printed'].dt.strftime('%Y-%m-%d')

    # Convert filtered table to dictionary format
    table_data = filtered_table.to_dict('records')

    return options, table_data

# @callback(

#     Input(component_id = "y", component_property= "n_clicks")
# )

# def test(click):
#     print("hellwo")