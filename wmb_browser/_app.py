"""Main Dash apps."""

import subprocess

import dash
import dash_bootstrap_components as dbc

APP_ROOT_NAME = ""

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width"},
    ],
    routes_pathname_prefix=f"/{APP_ROOT_NAME}",
    requests_pathname_prefix=f"/{APP_ROOT_NAME}",
)
app.title = "WMB Browser"

server = app.server

# judge which server I am running and change the prefix
host_name = subprocess.run(["hostname"], stdout=subprocess.PIPE, encoding="utf-8").stdout.strip()
print("App is running on host: ", host_name)
