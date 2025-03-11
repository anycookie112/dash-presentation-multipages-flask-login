# import dash
# from dash import html
# import dash_bootstrap_components as dbc
# from flask_login import current_user

# # Register the page
# dash.register_page(__name__)

# def layout():
#     # If the user is not logged in, show login prompt
#     if not current_user.is_authenticated:
#         print("User is not authenticated")
#         return dbc.Container(
#             dbc.Alert(
#                 [
#                     html.H4("Access Denied", className="alert-heading"),
#                     html.P("You must be logged in to view this page."),
#                     html.A("Login here", href="/", className="alert-link")
#                 ],
#                 color="danger",
#                 className="text-center mt-5"
#             ),
#             className="vh-100 d-flex align-items-center justify-content-center"
#         )

#     print(f"Current User: {repr(current_user.id)}, Role: {getattr(current_user, 'role', 'No role')}")

#     if not hasattr(current_user, "role") or current_user.role != "admin": 
#         print("Permission Denied")
#         return dbc.Container(
#             dbc.Alert(
#                 [
#                     html.H4("Permission Denied", className="alert-heading"),
#                     html.P("You do not have permission to view this page."),
#                     html.A("Go to Home", href="/", className="alert-link")
#                 ],
#                 color="warning",
#                 className="text-center mt-5"
#             ),
#             className="vh-100 d-flex align-items-center justify-content-center"
#         )
    
#     return html.Div([
#     html.H1('This is our Home page'),
#     html.Div('This is our Home page content.'),
# ])