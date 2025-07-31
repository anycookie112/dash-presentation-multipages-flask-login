from sqlalchemy import create_engine
from config.config import DB_CONFIG
import pandas as pd
import dash
from dash import dcc, html, dash_table, Output, Input, State, callback
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import datetime
import plotly.express as px
import plotly.graph_objects as go
from flask_login import current_user

page = "print_daily"
dash.register_page(__name__)

db_connection_str = create_engine(
    f"mysql+pymysql://{DB_CONFIG['username']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
)


def get_part_codes():
    query = """
        SELECT DISTINCT part_code FROM print_batch_info
    """
    with db_connection_str.connect() as connection:
        df = pd.read_sql(query, connection)
    return df['part_code'].tolist()


def all_data(print_info_id=None):
    if print_info_id is None:
        print_info_id = 0
    query = f"""
    SELECT print_batch_info.print_info_id , print_batch_info.part_code, print_batch_info.date_printed,
            history_print.date_print, history_print.movement_reason, history_print.amount_inspect, history_print.amount_reject, history_print.checker_name,
            print_defect_list.*
    FROM print_batch_info
    INNER JOIN history_print 
        ON print_batch_info.print_info_id = history_print.print_info_id
    INNER JOIN print_defect_list 
        ON print_defect_list.print_inspection_id = history_print.print_inspection_id
    WHERE print_batch_info.print_info_id = {print_info_id}
    ORDER BY history_print.date_print
"""
    with db_connection_str.connect() as connection:
        df = pd.read_sql(query, connection)
        df_ordered = df.sort_values(by='date_print', ascending=True)
    return df_ordered


def overall_data(print_info_id=None):
        if print_info_id is None:
            print_info_id = 0
        query = f"""
        SELECT print_batch_info.print_info_id , print_batch_info.part_code, print_batch_info.date_printed,
               history_print.date_print, history_print.movement_reason, history_print.amount_inspect, history_print.amount_reject, history_print.checker_name,
               print_defect_list.*
        FROM print_batch_info
        INNER JOIN history_print 
            ON print_batch_info.print_info_id = history_print.print_info_id
        INNER JOIN print_defect_list 
            ON print_defect_list.print_inspection_id = history_print.print_inspection_id
        WHERE print_batch_info.print_info_id = {print_info_id}
        ORDER BY history_print.date_print
    """
        with db_connection_str.connect() as connection:
            df = pd.read_sql(query, connection)


            df_grouped = df.copy()
            df_grouped.drop(columns=['print_inspection_id'], inplace=True)

            group_cols = ['print_info_id', 'movement_reason', 'checker_name']
            group_cols2 = ['print_info_id', 'movement_reason']

            df_ungrouped = df_grouped.drop(columns=['checker_name'])
            df_ungrouped = df_grouped.groupby(group_cols2).sum(numeric_only=True).reset_index()
            # Group and sum all numeric columns
            
            df_result = df_grouped.groupby(group_cols).sum(numeric_only=True).reset_index()
            # group df just groups all related to 1 print_info_id together



        return df_result, df_ungrouped



def fetch_data_print(date_start=None, date_end=None):
    if not date_start or not date_end:
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        if not date_start:
            date_start = yesterday.strftime('%Y-%m-%d')
        if not date_end:
            date_end = today.strftime('%Y-%m-%d')
    query = f"""
        SELECT print_batch_info.print_info_id , print_batch_info.part_code, print_batch_info.date_printed,
               history_print.date_print, history_print.movement_reason, history_print.amount_inspect, history_print.amount_reject, history_print.checker_name,
               print_defect_list.*
        FROM print_batch_info
        INNER JOIN history_print 
            ON print_batch_info.print_info_id = history_print.print_info_id
        INNER JOIN print_defect_list 
            ON print_defect_list.print_inspection_id = history_print.print_inspection_id
        WHERE history_print.date_print >= '{date_start}' AND history_print.date_print < '{date_end}'
        ORDER BY history_print.date_print
    """



    with db_connection_str.connect() as connection:
        df = pd.read_sql(query, connection)


        df_grouped = df.copy()
        df_grouped = df_grouped.drop(columns=['checker_name', 'movement_reason'])
        df_grouped = df_grouped.groupby(['print_info_id'])
        # group df just groups all related to 1 print_info_id together

    return df_grouped




def filter_print_data(print_info_id=None, date_start=None, date_end=None):
    if not print_info_id:
        print_info_id = 641  # Default value if not provided
    if not date_start or not date_end:
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        if not date_start:
            date_start = yesterday.strftime('%Y-%m-%d')
        if not date_end:
            date_end = today.strftime('%Y-%m-%d')
    query = f"""
        SELECT print_batch_info.print_info_id , print_batch_info.part_code, print_batch_info.date_printed,
            history_print.date_print, history_print.movement_reason, history_print.amount_inspect, history_print.amount_reject, history_print.checker_name,
            print_defect_list.*
        FROM print_batch_info
        INNER JOIN history_print 
            ON print_batch_info.print_info_id = history_print.print_info_id
        INNER JOIN print_defect_list 
            ON print_defect_list.print_inspection_id = history_print.print_inspection_id
        WHERE history_print.date_print >= '{date_start}' AND history_print.date_print < '{date_end}' AND history_print.print_info_id = {print_info_id}
    """
    # if action is not None:
    #     query += f" AND history_print.movement_reason = '{action}'"
    # query += " ORDER BY history_print.date_print"

    with db_connection_str.connect() as connection:
        df = pd.read_sql(query, connection)
        # print(df.head())
        df_grouped = df.copy()
        df_grouped.drop(columns=['print_inspection_id'], inplace=True)
        group_cols = ['print_info_id', 'movement_reason', 'checker_name']

        # # Group and sum all numeric columns
        # df_result = df_grouped.groupby(group_cols).sum(numeric_only=True).reset_index()
        df_result = df.groupby(group_cols).sum(numeric_only=True).reset_index()



        # df_result = df_grouped.agg({'amount_inspect': 'sum','dust_fibre': 'sum'}).reset_index()

    return df_result



def sunburt_chart(chart_data):
    # Step 1: Melt defect columns into rows
    # defect_cols = [
    #     'dust_mark', 'under_spray', 'scratches', 'dented', 'bubble',
    #     'smear', 'dirty', 'bulging', 'short_mould', 'weldline', 'incompleted',
    #     'colour_out', 'gate_high', 'over_stamp', 'ink_mark', 'banding',
    #     'shining', 'overtrim', 'dprinting', 'dust_fibre', 'thiner_mark',
    #     'adjustment', 'position_out', 'parting_line'
    # ]

    # print("Chart data columns:", chart_data.columns.tolist())

    # df_melted = chart_data.melt(
    #     id_vars=['movement_reason', 'checker_name'],
    #     value_vars=defect_cols,
    #     var_name='defect_type',
    #     value_name='count'
    # )

    # # Step 2: Filter out 0-counts
    # df_melted = df_melted[df_melted['count'] > 0]

    non_defect_cols = ['print_info_id', 'movement_reason', 'checker_name', 'amount_inspect', 'amount_reject']
    
    # Dynamically infer defect columns
    defect_cols = [col for col in chart_data.columns if col not in non_defect_cols]

    df_melted = chart_data.melt(
        id_vars=['movement_reason', 'checker_name'],
        value_vars=defect_cols,
        var_name='defect_type',
        value_name='count'
    )
    df_melted = df_melted[df_melted['count'] > 0]

    # ...rest of sunburst chart code...


    # Step 3: Plot sunburst chart
    fig = px.sunburst(
        df_melted,
        path=['defect_type', 'movement_reason', 'checker_name'],
        values='count',
        color='defect_type',  # optional: color by defect type
        title='Defects Breakdown by Type → Movement Reason → Checker'
    )
    fig.update_traces(insidetextorientation='radial')

    # fig.show()
    return fig




grouped = fetch_data_print()
grouped_df = grouped.first().reset_index() 
df = filter_print_data()
df_chart, df_table = overall_data(880)
sunburt_chart(df_chart)

unique_part_codes = get_part_codes()
print(df)





# rowData = df.first().reset_index()

# Dash app
# app = dash.Dash(__name__)

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
    return html.Div([html.Div([
    html.H1('Daily Print Inspection Daily Report'),
    html.Div(
        [
            dcc.DatePickerRange(
                id=f'date-range-daily-report-{page}',
                display_format='YYYY-MM-DD',
                style={"margin-left": "20px"}  # Add space between controls
            ),

            dbc.Select(
                id= f'select-part-{page}',
                options= unique_part_codes
            )


        ],
        style={
            "display": "flex",
            "alignItems": "center",
            "gap": "20px",  # Space between controls
            "marginBottom": "20px"
        }
    ),
    dag.AgGrid(
        id=f'daily_overall-{page}',
        rowData=grouped_df.to_dict('records'),
        dashGridOptions={'rowSelection': 'single', 'defaultSelected': [0]},
        columnDefs=[
            {"field": i, "filter": "agTextColumnFilter"} if i != "% rejection" else
            {
                "field": i,
                "filter": "agNumberColumnFilter",
                "floatingFilter": True,
                "type": "numericColumn",
                "sortable": True,
                "valueFormatter": {"function": "params.value + '%' if params.value else ''"}
            }
            for i in grouped_df.columns
        ],
        selectedRows=[],
        style={'height': '400px', 'width': '100%'}
    ),
    html.H2('Daily Rejection Rate'),

        #ag_grid.AgGrid for lots that are accumulated
        html.Div(
        [
            dash_table.DataTable(
                id=f'lot-table-{page}',
                data=[]
            ),
        ]
    ),

    html.H2('Overall Rejection Rate'),
    # pie chart overall rejection rate when clicked on the grid 
    html.Div(
        [
            dcc.Graph(
                id=f'sunburst-chart-{page}',
                figure=go.Figure()
            ),
            dash_table.DataTable(
                id=f'summary-table-{page}',
                data=[],
                style_table={'height': '400px', 'overflowY': 'auto', 'width': '100%'},
                style_cell={'textAlign': 'left'},
            ),
        ],
        style={
            "display": "flex",
            "gap": "20px",  # space between graph and table
            "alignItems": "flex-start"
        }
    ),

            html.Div(
        [
            dash_table.DataTable(
                id=f'overall-lot-table-{page}',
                data=[]
            ),
        ]
    ),


])])


@callback(
    Output(f'daily_overall-{page}', 'rowData'),
    Input(f'date-range-daily-report-{page}', 'start_date'),
    Input(f'date-range-daily-report-{page}', 'end_date'),
    Input(f'select-part-{page}', 'value'),
    )
def update_table_overall(start_date, end_date, part_code):
    if not start_date or not end_date:
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        start_date = yesterday.strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')

    df_grouped = fetch_data_print(start_date, end_date)

    if part_code is None:
        data = df_grouped.first().reset_index().to_dict('records')
    else: 
        df_first = df_grouped.first().reset_index()
        df_filtered = df_first[df_first['part_code'] == part_code]
        data = df_filtered.to_dict('records')

    return data



@callback(
    Output(f'sunburst-chart-{page}', 'figure'),
    Output(f'summary-table-{page}', 'data'),
    Output(f'lot-table-{page}', 'data'),
    Output(f'overall-lot-table-{page}', 'data'),
    Input(f'daily_overall-{page}', 'selectedRows'),
    Input(f'date-range-daily-report-{page}', 'start_date'),
    Input(f'date-range-daily-report-{page}', 'end_date'),
)
def get_lot_data(rowdata, date_start, date_end):
    if not rowdata:
        return go.Figure(), [], [], []

    selected_row = rowdata[0]
    if 'print_info_id' in selected_row:
        print_info_id = selected_row['print_info_id']
        df = filter_print_data(print_info_id=print_info_id, date_start = date_start, date_end = date_end)

        

        df_lot = df.copy()
        df_lot['% rejection'] = (df_lot['amount_reject'] / df_lot['amount_inspect'] * 100).fillna(0).round(2)
        df_lot = df_lot.loc[:, (df_lot != 0).any(axis=0)]
        df_lot_dict = df_lot.to_dict('records')

        chart_data, table_data = overall_data(print_info_id)
        fig = sunburt_chart(chart_data)
        fig_dict = fig.to_dict()

        table = table_data.copy()
        table['% rejection'] = (table['amount_reject'] / table['amount_inspect'] * 100).fillna(0).round(2)
        table = table.loc[:, (table != 0).any(axis=0)]

        df_all = all_data(print_info_id)
        df_all['% rejection'] = (df_all['amount_reject'] / df_all['amount_inspect'] * 100).fillna(0).round(2)
        df_all = df_all.loc[:, (df_all != 0).any(axis=0)]
            
        table_dict = table.to_dict('records')

        df_all_dict = df_all.to_dict('records')



        return fig_dict, table_dict, df_lot_dict, df_all_dict
    


    else:
        return go.Figure(), [], [], []
    


# if __name__ == "__main__":
#     app.run_server(debug=True)

# print(overall_data(880))

