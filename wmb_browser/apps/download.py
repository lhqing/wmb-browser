import dash_bootstrap_components as dbc
from dash import html, dcc

import pathlib
package_dir = pathlib.Path(__file__).parent.parent.absolute()
with open(f'{package_dir}/assets/download_content.md', 'r') as f:
    md_text = f.read()

jumbotron = html.Div(
    dbc.Container(
        [
            html.H1("Download Data", className="display-4"),
            html.Hr(className="my-2"),
            dcc.Markdown(md_text),
        ],
        fluid=True,
        className="py-3",
    ),
    className="p-3 bg-light rounded-3",
)

download_layout = html.Div(
    [
        jumbotron,
    ]
)
