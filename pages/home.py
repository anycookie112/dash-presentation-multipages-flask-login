# pages/home.py
import dash
from dash import html, callback, Output, Input, dash_table
import dash_bootstrap_components as dbc
from dash import dcc
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import dash_ag_grid as dag
import plotly.express as px
import plotly.subplots as sp
import plotly.graph_objects as go
from plotly.graph_objects import Figure
from plotly.subplots import make_subplots
from config.config import DB_CONFIG
from flask_login import current_user
# Get today's date
today = datetime.now()

# Calculate the start of the current week (Monday)
start_of_this_week = today - timedelta(days=today.weekday())

# Calculate the start and end of last week
start_of_last_week = start_of_this_week - timedelta(days=7)
end_of_last_week = start_of_this_week - timedelta(days=1)

# print("Start of Last Week:", start_of_last_week)
# print("End of Last Week:", end_of_last_week)

start_date_str = start_of_last_week.strftime('%Y-%m-%d %H:%M:%S')
end_date_str = end_of_last_week.strftime('%Y-%m-%d %H:%M:%S')

dash.register_page(__name__, path='/home')

"""

right now the data shown is total rejects checked last week, not overall, if we want overall
get the unique spray_batch_id from the query then show the query result of the overall data
Note: they want to verify reject by lot, so the query drop by date 

the rejection data should be total_checked/total_reject instead of total_output/total_reject

the columns should be (moevement_date, movement_reason, total_checked, total_reject, % rejection)



"""

db_connection_str = f"mysql+pymysql://{DB_CONFIG['username']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
db_connection = create_engine(db_connection_str)

df = pd.read_sql(f'''
    SELECT spray_batch_info.part_name, spray_batch_info.part_code , spray_batch_info.date_sprayed, spray_batch_info.spray_batch_id, history_spray.amount_inspect, history_spray.amount_reject, history_spray.movement_reason, spray_defect_list.*, history_spray.movement_date
    FROM spray_batch_info
    INNER JOIN history_spray 
        ON spray_batch_info.spray_batch_id = history_spray.spray_batch_id
    INNER JOIN spray_defect_list 
        ON spray_defect_list.spray_inspection_id = history_spray.spray_inspection_id
    WHERE history_spray.movement_date BETWEEN '{start_date_str}' AND '{end_date_str}'

''', con=db_connection)

filtered_df = df[(df['movement_reason'] == '100') | (df['movement_reason'] == '200')| (df['movement_reason'] == 'print')]

result_overall = filtered_df.groupby(['spray_batch_id', 'movement_date']).agg({
        'amount_inspect': 'sum',
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
        'date_sprayed': 'first',
        'part_name': 'first',  
        'part_code': 'first'    
    }).reset_index()

# Ensure '% Rejection' column exists
result_overall['% Rejection'] = result_overall.apply(
    lambda row: f"{((row['amount_reject'] / row['amount_inspect']) * 100):.2f}%", axis=1
)


result_overall = result_overall[[
        'spray_batch_id', 'part_name', 'part_code', 'date_sprayed','movement_date', 'amount_inspect', 'amount_reject', '% Rejection'
    ]]

# Optional: Debugging step to verify column creation
# print(result_overall.head())  # Check if '% Rejection' is present

# Clean the '% Rejection' column
result_overall['% Rejection'] = result_overall['% Rejection'].str.replace('%', '', regex=False)  # Remove '%'
result_overall['% Rejection'] = result_overall['% Rejection'].str.strip()  # Remove extra spaces

# Convert '% Rejection' to numeric
result_overall['% Rejection'] = pd.to_numeric(result_overall['% Rejection'], errors='coerce')

# Drop rows with NaN in '% Rejection'
result_overall = result_overall.dropna(subset=['% Rejection'])

# Optional: Fill missing values if needed
result_overall['% Rejection'] = result_overall['% Rejection'].fillna(0)

# Find the top 5 rejections
top_rejections = result_overall.nlargest(5, '% Rejection')

###################################################### PRINT ################################################################################

df_print = pd.read_sql(f'''
    SELECT print_batch_info.part_name, print_batch_info.part_code , print_batch_info.date_printed, print_batch_info.print_info_id, history_print.amount_inspect, history_print.amount_reject, history_print.movement_reason, print_defect_list.*, history_print.date_print
    FROM print_batch_info
    INNER JOIN history_print
        ON print_batch_info.print_info_id = history_print.print_info_id
    INNER JOIN print_defect_list 
        ON print_defect_list.print_inspection_id = history_print.print_inspection_id
    WHERE history_print.date_print BETWEEN '{start_date_str}' AND '{end_date_str}'
    ''', con=db_connection)

filtered_df_print = df_print[(df_print['movement_reason'] == '100') | (df_print['movement_reason'] == '200')| (df_print['movement_reason'] == 'Secondary process') | (df_print['movement_reason'] == 'New print batch') ]

result_overall_print = filtered_df_print.groupby(['print_info_id', 'date_printed']).agg({
    'amount_reject': 'sum','dust_mark': 'sum', 'amount_inspect': 'sum',
    'under_spray': 'sum','scratches': 'sum','dented': 'sum',
    'bubble': 'sum', 'dust_paint': 'sum',
    'sink_mark': 'sum','white_dot': 'sum',
    'black_dot': 'sum','smear': 'sum',
    'dirty': 'sum','bulging': 'sum',
    'short_mould': 'sum','weldline': 'sum',
    'incompleted': 'sum','colour_out': 'sum',
    'gate_high': 'sum','over_stamp': 'sum',
    'ink_mark': 'sum','banding': 'sum',
    'shining': 'sum','overtrim': 'sum','dprinting': 'sum',
    'dust_fibre': 'sum','thiner_mark': 'sum','adjustment': 'sum',
    'position_out': 'sum',
    'part_name': 'first',  
    'part_code': 'first'    
}).reset_index()

# Ensure '% Rejection' column exists
result_overall_print['% Rejection'] = result_overall_print.apply(
    lambda row: f"{((row['amount_reject'] / row['amount_inspect']) * 100):.2f}%", axis=1
)

result_overall_print = result_overall_print[[
    'print_info_id', 'part_name', 'part_code', 'date_printed','amount_inspect', 'amount_reject', '% Rejection'
]]
# Clean the '% Rejection' column
result_overall_print['% Rejection'] = result_overall_print['% Rejection'].str.replace('%', '', regex=False)  # Remove '%'
result_overall_print['% Rejection'] = result_overall_print['% Rejection'].str.strip()  # Remove extra spaces

# Convert '% Rejection' to numeric
result_overall_print['% Rejection'] = pd.to_numeric(result_overall_print['% Rejection'], errors='coerce')

# Drop rows with NaN in '% Rejection'
result_overall_print = result_overall_print.dropna(subset=['% Rejection'])

# Optional: Fill missing values if needed
result_overall_print['% Rejection'] = result_overall_print['% Rejection'].fillna(0)

# Find the top 5 rejections
top_rejections_print = result_overall_print.nlargest(5, '% Rejection')

# columns_of_interest = ['dust_mark','under_spray','scratches','dented','bubble', 'dust_paint','sink_mark','white_dot','black_dot','smear',
#     'dirty','bulging','short_mould','weldline','incompleted','colour_out','gate_high','over_stamp','ink_mark','banding',
#     'shining','overtrim','dprinting','dust_fibre','thiner_mark','adjustment', 'position_out']

# defect_data = {col: {'Overall': 0, 'Process 1' : 0, 'Process 2' : 0, '100%': 0, '200%': 0} for col in columns_of_interest}



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
    return ([dbc.Container(
    [dbc.Row(
            dbc.Col(
                html.H3("Top 5 Rejects Lot of Last Week Spray (By Day)", className="text-center mt-3 mb-3"),
                width=12
            )
        ),
        
    html.Div(dag.AgGrid(
            id='grid_top5',
            rowData=top_rejections.to_dict('records'),
            dashGridOptions={'rowSelection': 'single', 'defaultSelected': [0]},
            columnDefs=[{"field": i} for i in top_rejections.columns],
            selectedRows=[],
        )),

    html.Div(dbc.Row(
            dbc.Col(
                dcc.Graph(
                    id='pie_top5',
                    figure=go.Figure()
                ),
                width=6,
                className="mb-4"  # Add spacing below the chart
            ),
            justify="left"  # Center the chart
        )),

    dbc.Row(
            dbc.Col(
                dash_table.DataTable(
                    id='defect_table_top5',
                    data=[],
                    style_table={'width': '100%', 'overflowX': 'auto'},  # Responsive table
                ),
                width=12,
                className="mb-4"
            )
        ),

    dbc.Row(
            dbc.Col(
                html.H3("Top 5 Rejects Lot of Last Week Print (By Day)", className="text-center mt-3 mb-3"),
                width=12
            )
        ),
        
    html.Div(dag.AgGrid(
            id='grid_top5_print',
            rowData=top_rejections_print.to_dict('records'),
            dashGridOptions={'rowSelection': 'single', 'defaultSelected': [0]},
            columnDefs=[{"field": i} for i in top_rejections_print.columns],
            selectedRows=[],
        )),

    html.Div(dbc.Row(
            dbc.Col(
                dcc.Graph(
                    id='pie_top5_print',
                    figure=go.Figure()
                ),
                width=6,
                className="mb-4"  # Add spacing below the chart
            ),
            justify="left"  # Center the chart
        )),

    dbc.Row(
            dbc.Col(
                dash_table.DataTable(
                    id='defect_table_top5_print',
                    data=[],
                    style_table={'width': '100%', 'overflowX': 'auto'},  # Responsive table
                ),
                width=12,
                className="mb-4"
            )
        ),
        dcc.Interval(id = 'interval_top5', interval= 10 * 1000, n_intervals = 0)],
    fluid=True  # Makes the container span full width
)])



@callback(
    Output(component_id= 'defect_table_top5', component_property= 'data'),
    Output(component_id = 'pie_top5', component_property = 'figure'),
    Input(component_id='grid_top5', component_property='selectedRows'),
    Input(component_id='interval_top5', component_property='n_intervals')
)
def show_chart(selected_rows,n):
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
    


@callback(
    Output(component_id= 'defect_table_top5_print', component_property= 'data'),
    Output(component_id = 'pie_top5_print', component_property = 'figure'),
    Input(component_id='grid_top5_print', component_property='selectedRows'),
    Input(component_id='interval_top5', component_property='n_intervals')
)
def show_chart_print(selected_rows,n):

    df_print = pd.read_sql('''
    SELECT 
                        print_batch_info.print_info_id, 
                        print_batch_info.date_printed,
                        print_batch_info.part_name,
                        print_batch_info.part_code,
                        SUM(print_defect_list.dust_mark) AS dust_mark,
                        SUM(print_defect_list.under_spray) AS under_spray,
                        SUM(print_defect_list.scratches) AS scratches,
                        SUM(print_defect_list.dented) AS dented,
                        SUM(print_defect_list.bubble) AS bubble,
                        SUM(print_defect_list.dust_paint) AS dust_paint,
                        SUM(print_defect_list.sink_mark) AS sink_mark,
                        SUM(print_defect_list.white_dot) AS white_dot,
                        SUM(print_defect_list.black_dot) AS black_dot,
                        SUM(print_defect_list.smear) AS smear,
                        SUM(print_defect_list.dirty) AS dirty,
                        SUM(print_defect_list.bulging) AS bulging,
                        SUM(print_defect_list.short_mould) AS short_mould,
                        SUM(print_defect_list.weldline) AS weldline,
                        SUM(print_defect_list.incompleted) AS incompleted,
                        SUM(print_defect_list.colour_out) AS colour_out,
                        SUM(print_defect_list.gate_high) AS gate_high,
                        SUM(print_defect_list.over_stamp) AS over_stamp,
                        SUM(print_defect_list.ink_mark) AS ink_mark,
                        SUM(print_defect_list.banding) AS banding,
                        SUM(print_defect_list.shining) AS shining,
                        SUM(print_defect_list.overtrim) AS overtrim,
                        SUM(print_defect_list.dprinting) AS dprinting,
                        SUM(print_defect_list.dust_fibre) AS dust_fibre,
                        SUM(print_defect_list.thiner_mark) AS thiner_mark,
                        SUM(print_defect_list.adjustment) AS adjustment,
                        SUM(print_defect_list.position_out) AS position_out,
                        SUM(CASE WHEN history_print.movement_reason = 'New print batch' or history_print.movement_reason = 'Secondary process' THEN history_print.amount_inspect ELSE 0 END) AS total_output,
                        SUM(CASE WHEN history_print.movement_reason IN ('New print batch', '200', '100', 'Secondary process') THEN history_print.amount_reject ELSE 0 END) AS total_reject,
                        CASE 
                            WHEN SUM(CASE WHEN history_print.movement_reason = 'New print batch' or history_print.movement_reason = 'Secondary process' THEN history_print.amount_inspect ELSE 0 END) > 0 
                            THEN ROUND(
                                (
                                    SUM(CASE WHEN history_print.movement_reason IN ('New print batch', '200', '100', 'Secondary process') THEN history_print.amount_reject ELSE 0 END) / 
                                    SUM(CASE WHEN history_print.movement_reason = 'New print batch' or history_print.movement_reason = 'Secondary process' THEN history_print.amount_inspect ELSE 0 END)
                                ) * 100, 2
                            )
                            ELSE 0 
                        END AS rejection_percentage
                    FROM 
                        print_batch_info
                    INNER JOIN 
                        history_print ON print_batch_info.print_info_id = history_print.print_info_id
                    INNER JOIN 
                        print_defect_list ON print_defect_list.print_inspection_id = history_print.print_inspection_id
                    GROUP BY 
                        print_batch_info.print_info_id, 
                        print_batch_info.date_printed
''', con=db_connection)

    # filtered_df_print = df_print[(df_print['movement_reason'] == '100') | (df_print['movement_reason'] == '200')| (df_print['movement_reason'] == 'Secondary process') | (df_print['movement_reason'] == 'New print batch') ]

    result_overall_print = df_print.groupby('print_info_id').agg({
        'total_reject': 'sum','dust_mark': 'sum', 'total_output': 'first', 'rejection_percentage': 'first',
        'under_spray': 'sum','scratches': 'sum','dented': 'sum',
        'bubble': 'sum', 'dust_paint': 'sum',
        'sink_mark': 'sum','white_dot': 'sum',
        'black_dot': 'sum','smear': 'sum',
        'dirty': 'sum','bulging': 'sum',
        'short_mould': 'sum','weldline': 'sum',
        'incompleted': 'sum','colour_out': 'sum',
        'gate_high': 'sum','over_stamp': 'sum',
        'ink_mark': 'sum','banding': 'sum',
        'shining': 'sum','overtrim': 'sum','dprinting': 'sum',
        'dust_fibre': 'sum','thiner_mark': 'sum','adjustment': 'sum',
        'position_out': 'sum',
        'date_printed': 'first',
        'part_name': 'first',  
        'part_code': 'first'    
    }).reset_index()

    result_overall_print = result_overall_print[[
        'print_info_id', 'part_name', 'part_code', 'date_printed', 'total_output', 'total_reject', 'rejection_percentage',
        'dust_mark','under_spray','scratches','dented','bubble', 'dust_paint','sink_mark','white_dot','black_dot','smear',
        'dirty','bulging','short_mould','weldline','incompleted','colour_out','gate_high','over_stamp','ink_mark','banding',
        'shining','overtrim','dprinting','dust_fibre','thiner_mark','adjustment', 'position_out'
    ]]
    # Ensure there is at least one selected row
    if selected_rows:
        # Extract the first selected row
        part = selected_rows[0]
        # Get the spray_batch_id
        print_info_id = part['print_info_id']

        df = pd.read_sql(f'''
    SELECT print_batch_info.part_name, print_batch_info.part_code , print_batch_info.date_printed, print_batch_info.print_info_id, print_batch_info.total_output , history_print.amount_reject, history_print.movement_reason, print_defect_list.*
    FROM print_batch_info   
    INNER JOIN history_print
        ON print_batch_info.print_info_id = history_print.print_info_id
    INNER JOIN print_defect_list 
        ON print_defect_list.print_inspection_id = history_print.print_inspection_id
    WHERE print_batch_info.print_info_id = {print_info_id}
''', con=db_connection)
        
        df['movement_reason'] = df['movement_reason'].str.strip().str.lower()
        filtered_df_print = df[
        (df['movement_reason'] == '100') | 
        (df['movement_reason'] == '200') |
        (df['movement_reason'] == 'secondary process') | 
        (df['movement_reason'] == 'new print batch')
        ]

        filtered_df_print = filtered_df_print[filtered_df_print['movement_reason'].notna()]

        # print("filtered_df_print")
        # print(filtered_df_print)
        # print("##-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        

        
        result_overall_print = filtered_df_print.groupby('print_info_id').agg({
        'amount_reject': 'sum',
        'movement_reason' : lambda x: 'overall',
        'dust_mark': 'sum', 
        'total_output': 'first',
        'under_spray': 'sum',
        'scratches': 'sum',
        'dented': 'sum',
        'bubble': 'sum', 
        'dust_paint': 'sum',
        'sink_mark': 'sum',
        'white_dot': 'sum',
        'black_dot': 'sum',
        'smear': 'sum',
        'dirty': 'sum',
        'bulging': 'sum',
        'short_mould': 'sum',
        'weldline': 'sum',
        'incompleted': 'sum',
        'colour_out': 'sum',
        'gate_high': 'sum',
        'over_stamp': 'sum',
        'ink_mark': 'sum',
        'banding': 'sum',
        'shining': 'sum',
        'overtrim': 'sum',
        'dprinting': 'sum',
        'dust_fibre': 'sum',
        'thiner_mark': 'sum',
        'adjustment': 'sum',
        'position_out': 'sum',
        'date_printed': 'first',
        'part_name': 'first',  
        'part_code': 'first'    
        }).reset_index()

        result_subclass = filtered_df_print.groupby(['movement_reason','print_info_id']).agg({
        'amount_reject': 'sum',
        'dust_mark': 'sum', 'total_output': 'first',
        'under_spray': 'sum','scratches': 'sum','dented': 'sum',
        'bubble': 'sum', 'dust_paint': 'sum',
        'sink_mark': 'sum','white_dot': 'sum',
        'black_dot': 'sum','smear': 'sum',
        'dirty': 'sum','bulging': 'sum',
        'short_mould': 'sum','weldline': 'sum',
        'incompleted': 'sum','colour_out': 'sum',
        'gate_high': 'sum','over_stamp': 'sum',
        'ink_mark': 'sum','banding': 'sum',
        'shining': 'sum','overtrim': 'sum','dprinting': 'sum',
        'dust_fibre': 'sum','thiner_mark': 'sum','adjustment': 'sum',
        'position_out': 'sum',
        'date_printed': 'first',
        'part_name': 'first',  
        'part_code': 'first'    
        }).reset_index()

        # print("result_subclass")
        # print(result_subclass)
        # print("##-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")

    
        result_overall_print['% Rejection'] = result_overall_print.apply(
            lambda row: f"{((row['amount_reject'] / row['total_output']) * 100):.2f}%", axis=1
        )
        result_subclass['% Rejection'] = result_subclass.apply(
            lambda row: f"{((row['amount_reject'] / row['total_output']) * 100):.2f}%", axis=1
        )

        result_overall_print = result_overall_print[[
        'print_info_id', 'part_name', 'part_code', 'date_printed', 'movement_reason','total_output', 'amount_reject', '% Rejection',
        'dust_mark','under_spray','scratches','dented','bubble', 'dust_paint','sink_mark','white_dot','black_dot','smear',
        'dirty','bulging','short_mould','weldline','incompleted','colour_out','gate_high','over_stamp','ink_mark','banding',
        'shining','overtrim','dprinting','dust_fibre','thiner_mark','adjustment', 'position_out'
        ]]

        result_subclass = result_subclass[[
        'print_info_id', 'part_name', 'part_code', 'date_printed', 'movement_reason','total_output', 'amount_reject', '% Rejection',
        'dust_mark','under_spray','scratches','dented','bubble', 'dust_paint','sink_mark','white_dot','black_dot','smear',
        'dirty','bulging','short_mould','weldline','incompleted','colour_out','gate_high','over_stamp','ink_mark','banding',
        'shining','overtrim','dprinting','dust_fibre','thiner_mark','adjustment', 'position_out'
        ]]

        # Combine the two tables
        combined_result = pd.concat([result_subclass, result_overall_print], ignore_index=True)

        # Sort the combined table by a relevant column if needed (e.g., print_info_id or movement_reason)
        combined_result = combined_result.sort_values(by=['print_info_id', 'movement_reason'], ascending=[True, True])

        # Reset the index after sorting (optional)
        combined_result = combined_result.reset_index(drop=True)
        
        # Filter out columns with all zeros
        non_zero_columns = combined_result.loc[:, (combined_result != 0).any(axis=0)]

                # Define a custom order for 'movement_reason'
        movement_reason_order = ["overall", "secondary process", "new print batch", "100", "200"]

        # Convert 'movement_reason' to a categorical type with the specified order
        non_zero_columns['movement_reason'] = pd.Categorical(non_zero_columns['movement_reason'], categories=movement_reason_order, ordered=True)
        # non_zero_columns['movement_reason'] = pd.Categorical(non_zero_columns['movement_reason'], categories=movement_reason_order, ordered=True)

        # Define a mapping for the values in 'movement_reason' that you want to rename
        movement_reason_mapping = {
            "overall": "Overall",
            "secondary process": "P1/P2",
            "new print batch" : "100%",
            "100": "P3/P4",
            "200": "200%"
        }

        non_zero_columns['movement_reason'] = non_zero_columns['movement_reason'].cat.rename_categories(movement_reason_mapping)

        # Handle NaN or unexpected movement reasons if necessary (optional)
        # Add "Unknown" to the list of categories first before filling NaN
        non_zero_columns['movement_reason'] = non_zero_columns['movement_reason'].cat.add_categories("Unknown")

        # Fill NaN values with 'Unknown'
        non_zero_columns['movement_reason'].fillna("Unknown", inplace=True)

        # Sort the DataFrame based on the custom categorical order
        non_zero_columns = non_zero_columns.sort_values(by='movement_reason')

        metadata_columns = ['print_info_id', 'part_name', 'part_code', 'date_printed', 'movement_reason', 'total_output', 'amount_reject', '% Rejection']
        defect_columns = [col for col in non_zero_columns.columns if col not in metadata_columns]


        # Create the 2x2 subplot layout
        fig = make_subplots(
            rows=2,
            cols=2,
            specs=[[{'type': 'domain'}, {'type': 'domain'}], [{'type': 'domain'}, {'type': 'domain'}]],  # 2x2 grid for pie charts
            subplot_titles=non_zero_columns['movement_reason'].tolist()  # Dynamic titles based on movement reasons
        )

        # Loop through each row in `non_zero_columns` to create a pie chart
        for i, row in enumerate(non_zero_columns.itertuples()):
            # Extract non-zero defect values
            defects = row._asdict()  # Convert row to dictionary
            defect_values = {col: defects[col] for col in defect_columns if defects[col] > 0}

            # Skip if no defect values
            if not defect_values:
                continue

            # Calculate the subplot row and column
            row_pos = i // 2 + 1  # Determine row (0-based index -> 1-based index)
            col_pos = i % 2 + 1  # Determine column (wrap around every 2)

            # Add pie chart trace
            fig.add_trace(
                go.Pie(
                    labels=list(defect_values.keys()),  # Defect types
                    values=list(defect_values.values()),  # Defect values
                    name=row.movement_reason
                ),
                row=row_pos,
                col=col_pos
            )

        # Update layout
        fig.update_traces(hole=0.4, hoverinfo='label+value')  # Donut-style chart with hover info
        fig.update_layout(
            title_text="Secondary Printing Rejection %",
            title_x=0.5,  # Center the title
            height=800,  # Adjust height for better visibility
            width=800,   # Adjust width for better visibility
            showlegend=True)
                
        # Define the columns you want to drop

        columns_to_drop = ['print_info_id', 'part_name', 'part_code', 'date_printed', 'total_output']

        # Check if these columns exist in your DataFrame and drop them if they do
        columns_to_drop = [col for col in columns_to_drop if col in non_zero_columns.columns]

        # Drop the columns
        non_zero_columns_data = non_zero_columns.drop(columns=columns_to_drop)

        table_data_print = non_zero_columns_data.to_dict("records")

        # print(table_data_print)



        return table_data_print, fig
    



    else:
        # print("No rows selected.")
        # Ensure to return empty data and empty figure if no rows are selected
        empty_data = []
        empty_figure = go.Figure(data=[])
        return empty_data, empty_figure