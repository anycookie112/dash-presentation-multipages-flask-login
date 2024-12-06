import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table
from dash import Dash, html, dcc, dash_table

import plotly.express as px
import plotly.subplots as sp

import plotly.graph_objects as go
from plotly.graph_objects import Figure
from plotly.subplots import make_subplots

import dash_ag_grid as dag
import pandas as pd
from sqlalchemy import create_engine
from datetime import date

pd.options.display.max_columns = None
pd.options.display.max_rows = None

db_connection_str = 'mysql+pymysql://admin:UL1131@192.168.1.17/production'
db_connection = create_engine(db_connection_str)

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


columns_of_interest = ['dust_mark','under_spray','scratches','dented','bubble', 'dust_paint','sink_mark','white_dot','black_dot','smear',
    'dirty','bulging','short_mould','weldline','incompleted','colour_out','gate_high','over_stamp','ink_mark','banding',
    'shining','overtrim','dprinting','dust_fibre','thiner_mark','adjustment', 'position_out']

defect_data = {col: {'Overall': 0, 'Process 1' : 0, 'Process 2' : 0, '100%': 0, '200%': 0} for col in columns_of_interest}

result_overall_print_filtered = result_overall_print[result_overall_print['print_info_id'] == 86]

# print(result_overall_print)





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

dash.register_page(__name__)

layout = html.Div([

    # Dropdown and Date Picker Range wrapped in their own Div for layout control
    html.Div([
        dcc.Dropdown(
            id='dd1_print',
            options=[],
            placeholder="Select Parts...."
        ),
        dcc.DatePickerRange(id='date_range_print')
    ]),  # Example of styling layout

    # AgGrid
    html.Div(dag.AgGrid(
        id='grid_print',
        rowData=result_overall_print.to_dict('records'),
        dashGridOptions={'rowSelection': 'single', 'defaultSelected': [0]},
        columnDefs=[{"field": i} for i in result_overall_print.columns],
        selectedRows=[],
    )),

    # Pie chart
    html.Div(dcc.Graph(
        id='pie_print',
        figure=go.Figure()
    )),

    html.Div(dash_table.DataTable(
        id='defect_table_print',
        data=[]
    )),

    dcc.Interval(id = 'interval_print', interval= 10 * 1000, n_intervals = 0)

])


##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


@callback(
    Output(component_id='dd1_print', component_property='options'),
    Output(component_id='grid_print', component_property='rowData'),
    Input(component_id='dd1_print', component_property='value'),
    Input(component_id='date_range_print', component_property='start_date'),
    Input(component_id='date_range_print', component_property='end_date'),
    Input(component_id='interval_print', component_property='n_intervals')
)
def update_dropdown(dd1_print, start_date, end_date, n):
    # Fetch distinct part_codes from the database for the dropdown
    df = pd.read_sql('SELECT DISTINCT part_code FROM print_batch_info', con=db_connection)

    # Generate dropdown options from the part_codes
    part_code_list = df['part_code'].tolist()
    options = [{'label': code, 'value': code} for code in part_code_list]

    # Start with all data if no part_code is selected
    if not dd1_print:
        filtered_result_overall = result_overall_print.copy()  # Start with all data
    else:
        # Filter by the selected part_code
        filtered_result_overall = result_overall_print[result_overall_print['part_code'] == dd1_print].copy()

    # Ensure 'date_printed' is in datetime format and handle invalid values
    filtered_result_overall['date_printed'] = pd.to_datetime(
        filtered_result_overall['date_printed'], errors='coerce'
    )
    # Drop rows where 'date_printed' could not be converted
    filtered_result_overall = filtered_result_overall.dropna(subset=['date_printed'])

    # If no date range is provided, use the entire dataset
    if start_date is None or end_date is None:
        filtered_table_print = filtered_result_overall
    else:
        # Convert start_date and end_date to datetime
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # Filter by the date range
        filtered_table_print = filtered_result_overall[
            (filtered_result_overall['date_printed'] >= start_date) & (filtered_result_overall['date_printed'] <= end_date)
        ]

    # Sort by the most recent `date_printed`
    filtered_table_print = filtered_table_print.sort_values(by='date_printed', ascending=False)

    # Format 'date_printed' column to string for display purposes
    filtered_table_print['date_printed'] = filtered_table_print['date_printed'].dt.strftime('%Y-%m-%d')

    # Convert filtered table to dictionary format
    table_data_print = filtered_table_print.to_dict('records')

    return options, table_data_print

##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



@callback(
    Output(component_id= 'defect_table_print', component_property= 'data'),
    Output(component_id = 'pie_print', component_property = 'figure'),
    Input(component_id='grid_print', component_property='selectedRows'),
    Input(component_id='interval_print', component_property='n_intervals')
)
def show_chart(selected_rows,n):
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



