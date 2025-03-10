import dash
import os
import dash_bootstrap_components as dbc

from dash import html, dcc
from flask import Flask, session
from flask_login import LoginManager, UserMixin

from datetime import timedelta


server = Flask(__name__)
server.config.update(SECRET_KEY=os.getenv('SECRET_KEY'))
server.config["SESSION_TYPE"] = "filesystem"
server.config["SESSION_PERMANENT"] = False

server.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=1)
app = dash.Dash(__name__, server=server,
                title='Example Dash login',
                update_title='Loading...',
                use_pages=True, 
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = "/"

    
class User(UserMixin):
    def __init__(self, username, role="user"):  # Default role is "user"
        self.id = username
        self.role = role  # Add role attribute

@login_manager.user_loader
def load_user(user_id):
    if user_id:
        role = session.get("role", "user")  # Default to "user" if missing
        return User(user_id, role)
    return None

excluded_pages = {"/", "/logout", "/register"}  # Add any pages you want to exclude

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Location(id='redirect', refresh=True),

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
                  if page["relative_path"] not in excluded_pages  # Exclude specified pages

            ],
            brand="Login",  # Navbar brand
            brand_href="/",  # Link to home page
            color="primary",  # Navbar color
            dark=True  # Dark mode styling for the navbar
        ),
    ]),

    # Page content goes here (dash.page_container)
    dash.page_container
])





if __name__ == "__main__":
    app.run(debug=True)
