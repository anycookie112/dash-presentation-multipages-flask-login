# pages/home.py
import dash
from dash import html

dash.register_page(__name__, path='/')

layout = html.Div("This is the home page")

