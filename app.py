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

app = Dash(__name__, use_pages=True)

# Set the default page to the home page
app.layout = html.Div([
    html.H1('Secondary Rejection %'),
    html.Div([
        html.Div(
            dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
        ) for page in dash.page_registry.values()
    ]),
    dash.page_container
])



if __name__ == '__main__':
    app.run(debug=True)