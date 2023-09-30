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

app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        <!-- Google tag (gtag.js) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-4CVM3JM834"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-4CVM3JM834');
        </script>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        <!--[if IE]><script>
        alert("Dash v2.7+ does not support Internet Explorer. Please use a newer browser.");
        </script><![endif]-->
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""
server = app.server

# judge which server I am running and change the prefix
host_name = subprocess.run(["hostname"], stdout=subprocess.PIPE, encoding="utf-8").stdout.strip()
print("App is running on host: ", host_name)
