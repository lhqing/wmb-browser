"""Main app entry point and routing control."""
import dash_bootstrap_components as dbc
from _app import APP_ROOT_NAME, app, server
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate


def get_header():
    """Add header to the app."""
    logo_img_url = "https://raw.githubusercontent.com/lhqing/wmb-browser/master/wmb_browser/files/navbar_icon.gif"
    nav = dbc.Row(
        [
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Home", href=f"/{APP_ROOT_NAME}home")),
                ],
                className="mr-5",
                navbar=True,
                style={"font-size": "1.4em"},
            )
        ],
        className="ml-2 flex-nowrap mt-3 mt-md-0",
        align="center",
    )

    navbar = dbc.Navbar(
        [
            html.A(
                dbc.Row([dbc.Col(html.Img(src=logo_img_url, height="50px"))], align="left", className="g-0"),
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


# make sure pycharm do not remove the import line...
# because server need to be imported by wsgi.py from index.py
# all orders matters here
type(server)


app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        get_header(),  # nav bar
        html.Div(
            id="page-content",
            # Global style of all APPs
            className="page-content",
        ),
    ]
)


@app.callback(
    Output("page-content", "children"), [Input("url", "pathname")], [State("url", "search"), State("url", "href")]
)
def display_page(pathname, search, total_url):
    """Routing control."""
    app_layout = []
    # search_dict = search_to_dict(search)

    if pathname is None:
        # init callback url is None
        raise PreventUpdate
    elif (pathname == f"/{APP_ROOT_NAME}home") or (pathname == f"/{APP_ROOT_NAME}"):
        layout = []  # home_layout
    else:
        return "404"

    # final validate, if any parameter does not found, layout is None
    if layout is None:
        return "404"
    else:
        app_layout.append(layout)
    return app_layout


if __name__ == "__main__":
    app.run_server(debug=True, port="1234")
