"""Main app entry point and routing control."""

import dash_bootstrap_components as dbc
from _app import APP_ROOT_NAME, app, server
from dash import callback, dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from wmb_browser.apps.download import download_layout
from wmb_browser.apps.dynamic_browser import create_dynamic_browser_layout
from wmb_browser.apps.home import home_layout

LOGO_IMG_URL = (
    "https://raw.githubusercontent.com/lhqing/wmb-browser/master/"
    "wmb_browser/assets/dissection_region_img/navbar_icon.gif"
)

TUTORIAL_URL = "https://docs.google.com/document/d/11wUCcsdObf3XcRx3CwNBHGmfnqeSyT_wn0_c503Vxsk/edit?usp=sharing"


def get_header():
    """Add header to the app."""
    nav = dbc.Row(
        [
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Home", href=f"/{APP_ROOT_NAME}home")),
                    dbc.NavItem(dbc.NavLink("Browser", href=f"/{APP_ROOT_NAME}dynamic_browser")),
                    dbc.NavItem(dbc.NavLink("Download", href=f"/{APP_ROOT_NAME}download")),
                    dbc.NavItem(
                        dbc.NavLink(
                            "Tutorial",
                            href=TUTORIAL_URL,
                        )
                    ),
                ],
                className="mr-5",
                navbar=True,
                style={"font-size": "1.4em"},
            )
        ],
        className="ml-2 mt-3 mt-md-0",
        align="center",
    )

    navbar = dbc.Navbar(
        [
            html.A(
                dbc.Row([dbc.Col(html.Img(src=LOGO_IMG_URL, height="50px"))], align="left", className="g-0"),
                href=f"/{APP_ROOT_NAME}",
                className="mx-3",
            ),
            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.Collapse(nav, id="navbar-collapse", navbar=True),
        ],
        color="light",
        className="fixed-top mb-2 p-2",
    )
    return navbar

def get_footer():
    """Add footer to the app."""
    footer = dbc.Row(
        dbc.Col(
            html.P(
                html.A(
                "<Powered by SkyPilot>",
                href="https://github.com/skypilot-org/skypilot",
                target="_blank",  
                style={"color": "grey", "font-size": "0.8em"}),
            ),
            className="text-center",
            width={"size": 6, "offset": 3},
        ),
        align="center",
        className="fixed-bottom mb-2 p-2",
    )
    return footer


# make sure IDE do not remove the import line...
# because server need to be imported by wsgi.py from index.py
# all orders matters here
type(server)

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    get_header(),  # nav bar
    html.Div(
        id="page-content",
        # Global style of all APPs
        className="page-content",
    ),
    get_footer(),  # footer
])


@callback(
    Output("page-content", "children"), [Input("url", "pathname")], [State("url", "search"), State("url", "href")]
)
def display_page(pathname, search, total_url):
    """Routing control."""
    app_layout = []
    if pathname is None:
        # init callback url is None
        raise PreventUpdate
    elif (pathname == f"/{APP_ROOT_NAME}home") or (pathname == f"/{APP_ROOT_NAME}"):
        layout = home_layout
    elif pathname == f"/{APP_ROOT_NAME}dynamic_browser":
        layout = create_dynamic_browser_layout(search)
    elif pathname == f"/{APP_ROOT_NAME}download":
        layout = download_layout
    # add layout functions here based on pathname
    # elif pathname == f"/{APP_ROOT_NAME}app1":
    #     layout = app1_layout(search_dict)
    else:
        layout = None

    # final validate, if any parameter does not found, layout is None
    if layout is None:
        return "404"
    else:
        app_layout.append(layout)
    return app_layout


if __name__ == "__main__":
    app.run(debug=True, port="1234")

# pip install gunicorn
# gunicorn -w 4 -b 127.0.0.1:8000 index:server
