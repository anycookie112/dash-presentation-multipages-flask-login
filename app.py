import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.subplots as sp

import plotly.graph_objects as go
from plotly.graph_objects import Figure
from plotly.subplots import make_subplots

import dash_ag_grid as dag
import pandas as pd


app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Set the default page to the home page
app.layout = html.Div([

    html.H1('Secondary Rejection %'),

    # Create Navbar with dynamic page links
    html.Div([

        dbc.NavbarSimple(
            children=[
                # Dynamically generate links from dash.page_registry
                dbc.NavItem(
                    dcc.Link(
                        page['name'],  # Page name
                        href=page["relative_path"],  # Page URL
                        className="nav-link text-light",  # Apply Bootstrap styling
                    )
                ) for page in dash.page_registry.values()
            ],
            brand="My App",  # Navbar brand
            brand_href="/",  # Link to home page
            color="primary",  # Navbar color
            dark=True  # Dark mode styling for the navbar
        ),
    ]),

    # Page content goes here (dash.page_container)
    dash.page_container
])

# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)


"""
do the thing by batch and lot?
get the date range
for batch
get the unique id
filter again to see if any of the batch is exceed 3 % reject

for lot 
just get the top 5 highest reject?
or all the reject that exceeds a certain %


probably need to do one for this week as well




"""