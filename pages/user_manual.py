import dash
from dash import html
import dash_bootstrap_components as dbc  # Import Bootstrap components
from dash import dcc
# Initialize the Dash app with a Bootstrap stylesheet


dash.register_page(__name__)

# Define the layout
layout = dbc.Container(
    [
        # Header
        dbc.Row(
            dbc.Col(
                html.H1("User Manual", className="text-center my-4"),
                width=12
            )
        ),

        # Link to the external website
        dbc.Row(
            dbc.Col(
                html.A(
                    "Click here to view the User Manual",
                    href="https://heavenly-wren-d5a.notion.site/User-Manual-1518134358e580afadcad1abd38db7b4",
                    target="_blank",  # Open link in a new tab
                    className="btn btn-primary"  # Bootstrap button styling
                ),
                width=12
            )
        )
    ],
    fluid=True
)