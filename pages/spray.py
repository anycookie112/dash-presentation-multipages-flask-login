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

dash.register_page(__name__)

db_connection_str = 'mysql+pymysql://admin:UL1131@192.168.1.17/production'
db_connection = create_engine(db_connection_str)

df = pd.read_sql('''
    SELECT spray_batch_info.part_name, spray_batch_info.part_code , spray_batch_info.date_sprayed, spray_batch_info.spray_batch_id, spray_batch_info.total_output , history_spray.amount_reject, history_spray.movement_reason, spray_defect_list.*
    FROM spray_batch_info
    INNER JOIN history_spray 
        ON spray_batch_info.spray_batch_id = history_spray.spray_batch_id
    INNER JOIN spray_defect_list 
        ON spray_defect_list.spray_inspection_id = history_spray.spray_inspection_id
''', con=db_connection)
filtered_df = df[(df['movement_reason'] == '100') | (df['movement_reason'] == '200')| (df['movement_reason'] == 'print')]

result_overall = filtered_df.groupby('spray_batch_id').agg({
    'amount_reject': 'sum','dust_mark': 'sum',
    'fibre_mark': 'sum','paint_marks': 'sum','white_marks': 'sum',
    'sink_marks': 'sum', 'texture_marks': 'sum',
    'water_marks': 'sum','flow_marks': 'sum',
    'black_dot': 'sum','white_dot': 'sum',
    'over_paint': 'sum','under_spray': 'sum',
    'colour_out': 'sum','masking_ng': 'sum',
    'flying_paint': 'sum','weldline': 'sum',
    'banding': 'sum','short_mould': 'sum',
    'sliver_streak': 'sum','dented': 'sum',
    'scratches': 'sum','dirty': 'sum','print_defects': 'sum',
    "total_output": 'first',
    'date_sprayed': 'first',
    'part_name': 'first',  
    'part_code': 'first'    
}).reset_index()

result_100_200 = filtered_df.groupby(['movement_reason', 'spray_batch_id']).agg({
    'amount_reject': 'sum',
    'dust_mark': 'sum',
    'fibre_mark': 'sum',
    'paint_marks': 'sum',
    'white_marks': 'sum',
    'sink_marks': 'sum',
    'texture_marks': 'sum',
    'water_marks': 'sum',
    'flow_marks': 'sum',
    'black_dot': 'sum',
    'white_dot': 'sum',
    'over_paint': 'sum',
    'under_spray': 'sum',
    'colour_out': 'sum',
    'masking_ng': 'sum',
    'flying_paint': 'sum',
    'weldline': 'sum',
    'banding': 'sum',
    'short_mould': 'sum',
    'sliver_streak': 'sum',
    'dented': 'sum',
    'scratches': 'sum',
    'dirty': 'sum',
    'print_defects': 'sum',
    'total_output': 'first',
    'date_sprayed': 'first',
    'part_name': 'first',
    'part_code': 'first'
}).reset_index()


result_overall['% Rejection'] = result_overall.apply(
    lambda row: f"{((row['amount_reject'] / row['total_output']) * 100):.2f}%", axis=1
)
result_100_200['% Rejection'] = result_100_200.apply(
    lambda row: f"{((row['amount_reject'] / row['total_output']) * 100):.2f}%", axis=1
)


result_overall = result_overall[[
    'spray_batch_id', 'part_name', 'part_code', 'date_sprayed', 'total_output', 'amount_reject', '% Rejection',
    'dust_mark', 'fibre_mark', 'paint_marks', 'white_marks', 'sink_marks', 
    'texture_marks', 'water_marks', 'flow_marks', 'black_dot', 'white_dot', 
    'over_paint', 'under_spray', 'colour_out', 'masking_ng', 'flying_paint', 
    'weldline', 'banding', 'short_mould', 'sliver_streak', 'dented', 'scratches', 
    'dirty', 'print_defects'
]]

result_100_200 = result_100_200[[
    'spray_batch_id', 'part_name', 'part_code', 'date_sprayed', 'movement_reason', 'total_output', 'amount_reject', '% Rejection',
    'dust_mark', 'fibre_mark', 'paint_marks', 'white_marks', 'sink_marks', 
    'texture_marks', 'water_marks', 'flow_marks', 'black_dot', 'white_dot', 
    'over_paint', 'under_spray', 'colour_out', 'masking_ng', 'flying_paint', 
    'weldline', 'banding', 'short_mould', 'sliver_streak', 'dented', 'scratches', 
    'dirty', 'print_defects'
]]



"""
so when the user picks a part and a date range 
the data will be populated into a table with a checkbox beside it
when the user checks the box it will show data regarding the specific lot that the user picked
a graph and a table will be shown to the user with the rejection data 

(the range data will just use data from spray batch info 
filter with part name and date range, after getting the info then use id to filter 

the lot selected will extarct the lot number and the lot number will be used to filter out the data)

extra?
this one can also use spray id to filter in history_spray

another table will be populated with the inspection lots that led up to this point 
this one will show checker name, amount checked, amount reject and the % rejectiion 
a graph and table will also be shown right beside the table itself (same as the table at the top)

"""

##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



layout = dbc.Container(
    [
        # Dropdown for part selection
        dbc.Row(
            dbc.Col(
                dcc.Dropdown(
                    id='dd1',
                    options=[],
                    placeholder="Select Parts....",
                ),
                width=6,  # Center with a width of 6 out of 12
                className="mt-3 mb-3"  # Add top and bottom margin
            )
        ),

        # Date picker
        dbc.Row(
            dbc.Col(
                html.Div(
                    dcc.DatePickerRange(id='date_range'),
                    className="d-flex justify-content-left"  # Center the DatePickerRange
                ),
                width=6,
                className="mt-3 mb-3"
            )
        ),

        # AgGrid Table
        dbc.Row(
            dbc.Col(
                dag.AgGrid(
                    id='grid',
                    rowData=result_overall.to_dict('records'),
                    dashGridOptions={'rowSelection': 'single', 'defaultSelected': [0]},
                    columnDefs=[{"field": i} for i in result_overall.columns],
                    selectedRows=[],
                    style={'height': '400px', 'width': '100%'}  # Adjust height and width
                ),
                width=12,
                className="mb-4"
            )
        ),

        # Pie chart
        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    id='pie',
                    figure=go.Figure()
                ),
                width=6,
                className="mb-4"  # Add spacing below the chart
            ),
            justify="left"  # Center the chart
        ),

        # Defect data table
        dbc.Row(
            dbc.Col(
                dash_table.DataTable(
                    id='defect_table',
                    data=[],
                    style_table={'width': '100%', 'overflowX': 'auto'},  # Responsive table
                ),
                width=12,
                className="mb-4"
            )
        ),
        dcc.Interval(id = 'interval_spray', interval= 10 * 1000, n_intervals = 0)
    ],
    fluid=True  # Makes the container span full width
)

@callback(
    Output(component_id='dd1', component_property='options'),
    Output(component_id='grid', component_property='rowData'),
    Input(component_id='dd1', component_property='value'),
    Input(component_id='date_range', component_property='start_date'),
    Input(component_id='date_range', component_property='end_date'),
    Input(component_id='interval_spray', component_property='n_intervals')
)
def update_dropdown(dd1, start_date, end_date, n):

    df = pd.read_sql('''
    SELECT spray_batch_info.part_name, spray_batch_info.part_code , spray_batch_info.date_sprayed, spray_batch_info.spray_batch_id, spray_batch_info.total_output , history_spray.amount_reject, history_spray.movement_reason, spray_defect_list.*
    FROM spray_batch_info
    INNER JOIN history_spray 
        ON spray_batch_info.spray_batch_id = history_spray.spray_batch_id
    INNER JOIN spray_defect_list 
        ON spray_defect_list.spray_inspection_id = history_spray.spray_inspection_id
''', con=db_connection)
    filtered_df = df[(df['movement_reason'] == '100') | (df['movement_reason'] == '200')| (df['movement_reason'] == 'print')]

    result_overall = filtered_df.groupby('spray_batch_id').agg({
        'amount_reject': 'sum',
        'dust_mark': 'sum',
        'fibre_mark': 'sum',
        'paint_marks': 'sum',
        'white_marks': 'sum',
        'sink_marks': 'sum',
        'texture_marks': 'sum',
        'water_marks': 'sum',
        'flow_marks': 'sum',
        'black_dot': 'sum',
        'white_dot': 'sum',
        'over_paint': 'sum',
        'under_spray': 'sum',
        'colour_out': 'sum',
        'masking_ng': 'sum',
        'flying_paint': 'sum',
        'weldline': 'sum',
        'banding': 'sum',
        'short_mould': 'sum',
        'sliver_streak': 'sum',
        'dented': 'sum',
        'scratches': 'sum',
        'dirty':'sum',
        'print_defects': 'sum',
        "total_output": 'first',
        'date_sprayed': 'first',
        'part_name': 'first',  
        'part_code': 'first'    
    }).reset_index()

    result_100_200 = filtered_df.groupby(['movement_reason', 'spray_batch_id']).agg({
        'amount_reject': 'sum',
        'dust_mark': 'sum',
        'fibre_mark': 'sum',
        'paint_marks': 'sum',
        'white_marks': 'sum',
        'sink_marks': 'sum',
        'texture_marks': 'sum',
        'water_marks': 'sum',
        'flow_marks': 'sum',
        'black_dot': 'sum',
        'white_dot': 'sum',
        'over_paint': 'sum',
        'under_spray': 'sum',
        'colour_out': 'sum',
        'masking_ng': 'sum',
        'flying_paint': 'sum',
        'weldline': 'sum',
        'banding': 'sum',
        'short_mould': 'sum',
        'sliver_streak': 'sum',
        'dented': 'sum',
        'scratches': 'sum',
        'dirty':'sum',
        'print_defects': 'sum',
        'total_output': 'first',
        'date_sprayed': 'first',
        'part_name': 'first',
        'part_code': 'first'
    }).reset_index()


    result_overall['% Rejection'] = result_overall.apply(
        lambda row: f"{((row['amount_reject'] / row['total_output']) * 100):.2f}%", axis=1
    )
    result_100_200['% Rejection'] = result_100_200.apply(
        lambda row: f"{((row['amount_reject'] / row['total_output']) * 100):.2f}%", axis=1
    )


    result_overall = result_overall[[
        'spray_batch_id', 'part_name', 'part_code', 'date_sprayed', 'total_output', 'amount_reject', '% Rejection',
        'dust_mark', 'fibre_mark', 'paint_marks', 'white_marks', 'sink_marks', 
        'texture_marks', 'water_marks', 'flow_marks', 'black_dot', 'white_dot', 
        'over_paint', 'under_spray', 'colour_out', 'masking_ng', 'flying_paint', 
        'weldline', 'banding', 'short_mould', 'sliver_streak', 'dented', 'scratches', 
        'dirty', 'print_defects'
    ]]

    result_100_200 = result_100_200[[
        'spray_batch_id', 'part_name', 'part_code', 'date_sprayed', 'movement_reason', 'total_output', 'amount_reject', '% Rejection',
        'dust_mark', 'fibre_mark', 'paint_marks', 'white_marks', 'sink_marks', 
        'texture_marks', 'water_marks', 'flow_marks', 'black_dot', 'white_dot', 
        'over_paint', 'under_spray', 'colour_out', 'masking_ng', 'flying_paint', 
        'weldline', 'banding', 'short_mould', 'sliver_streak', 'dented', 'scratches', 
        'dirty', 'print_defects'
    ]]
    # Fetch distinct part_codes from the database for the dropdown
    df = pd.read_sql('SELECT DISTINCT part_code FROM spray_batch_info', con=db_connection)

    # Generate dropdown options from the part_codes
    part_code_list = df['part_code'].tolist()
    options = [{'label': code, 'value': code} for code in part_code_list]

    # Start with all data if no part_code is selected
    if not dd1:
        filtered_result_overall = result_overall.copy()  # Start with all data
    else:
        # Filter by the selected part_code
        filtered_result_overall = result_overall[result_overall['part_code'] == dd1].copy()

    # Ensure 'date_sprayed' is in datetime format and handle invalid values
    filtered_result_overall['date_sprayed'] = pd.to_datetime(
        filtered_result_overall['date_sprayed'], errors='coerce'
    )
    # Drop rows where 'date_sprayed' could not be converted
    filtered_result_overall = filtered_result_overall.dropna(subset=['date_sprayed'])

    # If no date range is provided, use the entire dataset
    if start_date is None or end_date is None:
        filtered_table = filtered_result_overall
    else:
        # Convert start_date and end_date to datetime
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # Filter by the date range
        filtered_table = filtered_result_overall[
            (filtered_result_overall['date_sprayed'] >= start_date) & (filtered_result_overall['date_sprayed'] <= end_date)
        ]

    # Sort by the most recent `date_sprayed`
    filtered_table = filtered_table.sort_values(by='date_sprayed', ascending=False)

    # Format 'date_sprayed' column to string for display purposes
    filtered_table['date_sprayed'] = filtered_table['date_sprayed'].dt.strftime('%Y-%m-%d')

    # Convert filtered table to dictionary format
    table_data = filtered_table.to_dict('records')


    return options, table_data

@callback(
    Output(component_id= 'defect_table', component_property= 'data'),
    Output(component_id = 'pie', component_property = 'figure'),
    Input(component_id='grid', component_property='selectedRows'),
    Input(component_id='interval_spray', component_property='n_intervals')
)
def show_chart(selected_rows, n):
    # Ensure there is at least one selected row
    if selected_rows:
        subplot_titles = ["Overall Reject", "100% Reject", "200% Reject"]
        # Extract the first selected row
        part = selected_rows[0]
        # Get the spray_batch_id
        spray_batch_id = part['spray_batch_id']

        df = pd.read_sql(f'''
    SELECT spray_batch_info.part_name, spray_batch_info.part_code , spray_batch_info.date_sprayed, spray_batch_info.spray_batch_id, spray_batch_info.total_output , history_spray.amount_reject, history_spray.movement_reason, spray_defect_list.*
    FROM spray_batch_info
    INNER JOIN history_spray 
        ON spray_batch_info.spray_batch_id = history_spray.spray_batch_id
    INNER JOIN spray_defect_list 
        ON spray_defect_list.spray_inspection_id = history_spray.spray_inspection_id
    WHERE spray_batch_info.spray_batch_id = {spray_batch_id}
''', con=db_connection)
        filtered_df_pie = df[(df['movement_reason'] == '100') | (df['movement_reason'] == '200')| (df['movement_reason'] == 'print')]

        

        result_overall_pie = filtered_df_pie.groupby('spray_batch_id').agg({
            'amount_reject': 'sum',
            'dust_mark': 'sum',
            'fibre_mark': 'sum',
            'paint_marks': 'sum',
            'white_marks': 'sum',
            'sink_marks': 'sum', 
            'texture_marks': 'sum',
            'water_marks': 'sum',
            'flow_marks': 'sum',
            'black_dot': 'sum',
            'white_dot': 'sum',
            'over_paint': 'sum',
            'under_spray': 'sum',
            'colour_out': 'sum',
            'masking_ng': 'sum',
            'flying_paint': 'sum',
            'weldline': 'sum',
            'banding': 'sum',
            'short_mould': 'sum',
            'sliver_streak': 'sum',
            'dented': 'sum',
            'scratches':'sum',
            'dirty':'sum',
            'print_defects': 'sum',
            'total_output': 'first',
            'date_sprayed': 'first',
            'part_name': 'first',  
            'part_code': 'first'    
        }).reset_index()

        result_100_200_pie = filtered_df_pie.groupby(['movement_reason', 'spray_batch_id']).agg({
            'amount_reject': 'sum',
            'dust_mark': 'sum',
            'fibre_mark': 'sum',
            'paint_marks': 'sum',
            'white_marks': 'sum',
            'sink_marks': 'sum',
            'texture_marks': 'sum',
            'water_marks': 'sum',
            'flow_marks': 'sum',
            'black_dot': 'sum',
            'white_dot': 'sum',
            'over_paint': 'sum',
            'under_spray': 'sum',
            'colour_out': 'sum',
            'masking_ng': 'sum',
            'flying_paint': 'sum',
            'weldline': 'sum',
            'banding': 'sum',
            'short_mould': 'sum',
            'sliver_streak': 'sum',
            'dented': 'sum',
            'scratches': 'sum',
            'dirty': 'sum',
            'print_defects': 'sum',
            'total_output': 'first',
            'date_sprayed': 'first',
            'part_name': 'first',
            'part_code': 'first'
        }).reset_index()


        result_overall_pie['% Rejection'] = result_overall_pie.apply(
            lambda row: f"{((row['amount_reject'] / row['total_output']) * 100):.2f}%", axis=1
        )
        result_100_200_pie['% Rejection'] = result_100_200_pie.apply(
            lambda row: f"{((row['amount_reject'] / row['total_output']) * 100):.2f}%", axis=1
        )

        result_overall_pie = result_overall_pie[[
            'spray_batch_id', 'part_name', 'part_code', 'date_sprayed', 'total_output', 'amount_reject', '% Rejection',
            'dust_mark', 'fibre_mark', 'paint_marks', 'white_marks', 'sink_marks', 
            'texture_marks', 'water_marks', 'flow_marks', 'black_dot', 'white_dot', 
            'over_paint', 'under_spray', 'colour_out', 'masking_ng', 'flying_paint', 
            'weldline', 'banding', 'short_mould', 'sliver_streak', 'dented', 'scratches', 
            'dirty', 'print_defects'
        ]]

        result_100_200_pie = result_100_200_pie[[
            'spray_batch_id', 'part_name', 'part_code', 'date_sprayed', 'movement_reason', 'total_output', 'amount_reject', '% Rejection',
            'dust_mark', 'fibre_mark', 'paint_marks', 'white_marks', 'sink_marks', 
            'texture_marks', 'water_marks', 'flow_marks', 'black_dot', 'white_dot', 
            'over_paint', 'under_spray', 'colour_out', 'masking_ng', 'flying_paint', 
            'weldline', 'banding', 'short_mould', 'sliver_streak', 'dented', 'scratches', 
            'dirty', 'print_defects'
        ]]

        # print(result_overall_pie)
        # print(result_100_200_pie)

        # Select the columns of interest
        columns_of_interest = [
            'dust_mark', 'fibre_mark', 'paint_marks', 'white_marks', 'sink_marks', 
            'texture_marks', 'water_marks', 'flow_marks', 'black_dot', 'white_dot', 
            'over_paint', 'under_spray', 'colour_out', 'masking_ng', 'flying_paint', 
            'weldline', 'banding', 'short_mould', 'sliver_streak', 'dented', 'scratches', 
            'dirty', 'print_defects'
        ]

        defect_data = {col: {'Overall': 0, '100%': 0, '200%': 0} for col in columns_of_interest}

        # Loop through rows and process data
        for _, row in result_100_200_pie.iterrows():
            # Update Overall data
            for defect in columns_of_interest:
                if pd.notna(row.get(defect, None)):
                    defect_data[defect]['Overall'] += row[defect]

            # Update data for 100% and 200% checks
            if row['movement_reason'] == '100':
                for defect in columns_of_interest:
                    if pd.notna(row.get(defect, None)):
                        defect_data[defect]['100%'] += row[defect]
            elif row['movement_reason'] == '200':
                for defect in columns_of_interest:
                    if pd.notna(row.get(defect, None)):
                        defect_data[defect]['200%'] += row[defect]

        # Create the resulting DataFrame
        defect_df = pd.DataFrame(defect_data).T.reset_index()
        defect_df.columns = ['Defect Type', 'Overall', '100%', '200%']

        valid_columns = [col for col in columns_of_interest if col in result_overall_pie.columns]
        # print("Valid Columns: ", valid_columns)

        # Filter the data to only keep rows where any value in the selected columns is non-zero and not NaN
        subset_df = result_overall_pie.loc[:, valid_columns]  # Select only valid columns

        # Further filter to exclude rows where all values in selected columns are either 0 or NaN
        subset_df = subset_df.loc[(subset_df != 0).any(axis=1) & subset_df.notna().any(axis=1)]

        # Always include the overall rejection distribution
        overall_column_sums = subset_df.sum()
        filtered_overall_column_sums = overall_column_sums[overall_column_sums > 0]

        # Create the main subplot structure
        num_subplots = 1  # Start with 1 for the overall chart
        if not result_100_200_pie.empty:
            num_subplots += len(result_100_200_pie)

        # Define the number of columns you want for horizontal arrangement
        num_columns = 3  # Adjust this number for how many columns you want per row
        num_rows = (num_subplots + num_columns - 1) // num_columns  # Calculate number of rows dynamically

        # Create the subplots with the updated row and column structure
        fig = sp.make_subplots(
        rows=num_rows,
        cols=num_columns,
        subplot_titles=subplot_titles,
        specs=[[{'type': 'domain'}] * num_columns for _ in range(num_rows)]  # Consistent domain type
)

        # Add the overall defect distribution pie chart
        fig.add_pie(
            labels=filtered_overall_column_sums.index,
            values=filtered_overall_column_sums.values,
            name="Overall Defects",
            textinfo="label+value",  # Only label and value
            hole=0.3,  # Consistent hole size
            row=1,
            col=1
        )

        # Add pie charts for 100% and 200% checks
        if not result_100_200_pie.empty:
            for i, (_, row) in enumerate(result_100_200_pie.iterrows()):
                if row['movement_reason'] in ['100', '200']:
                    # Filter columns of interest that have values greater than 0
                    filtered_row = row[columns_of_interest][row[columns_of_interest] > 0]
                    
                    # Dynamic row and column assignment
                    row_pos = (i + 1) // num_columns + 1
                    col_pos = (i + 1) % num_columns + 1
                    
                    # Add pie chart for this row
                    fig.add_pie(
                        labels=filtered_row.index,
                        values=filtered_row.values,
                        name=f"Batch {row['spray_batch_id']} ({row['movement_reason']}%)",
                        textinfo="label+value",  # Only label and value
                        hole=0.3,  # Consistent hole size
                        row=row_pos,
                        col=col_pos
                    )

        # Update layout for consistency
        fig.update_layout(
            height=1000,  # Consistent size
            width=1200,  # Consistent size
            title_x=0.5,  # Center the main title
            title_y=0.95,  # Adjust the main title closer to the chart
            margin=dict(t=30, b=30, l=30, r=30),  # Reduce margins for better fit
            title="Defect Distribution Overview",
            showlegend=True
            
        )
        
        # Exclude the 'Defect Type' column when checking for non-zero rows
        defect_df_filtered = defect_df.loc[(defect_df.iloc[:, 1:] != 0).any(axis=1)]

        # Convert to dictionary for Dash DataTable
        defect_data_table = defect_df_filtered.to_dict('records')


        # print(defect_df)
        figure_dict = fig.to_dict()
        fig = Figure(fig)  # Ensure compatibility



        return defect_data_table, figure_dict



    else:
        # print("No rows selected.")
        empty_data = []
        empty_figure = go.Figure(data=[])
        return empty_data, empty_figure



