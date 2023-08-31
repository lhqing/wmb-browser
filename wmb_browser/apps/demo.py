import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, callback, dcc, html

df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv")

app = Dash(__name__)
html_str = """<!DOCTYPE html><html>  <head>    <link rel="stylesheet" href="https://esm.sh/higlass@1.12/dist/hglib.css">    <script src="https://unpkg.com/requirejs-toggle"></script>        <script src="https://unpkg.com/requirejs-toggle"></script>  </head>  <body>    <div id="jupyter-hg-af228e44a1ef496aba68439ae755a3a0"></div>  </body>  <script type="module">    import hglib from "https://esm.sh/higlass@1.12?deps=react@17,react-dom@17,pixi.js@6";    hglib.viewer(      document.getElementById('jupyter-hg-af228e44a1ef496aba68439ae755a3a0'),      {"editable": true, "viewEditable": true, "tracksEditable": true, "views": [{"layout": {"x": 0, "y": 0, "w": 6, "h": 6}, "tracks": {"center": [{"tilesetUid": "CQMd6V_cRw6iCI_-Unl3PQ", "server": "https://higlass.io/api/v1/", "type": "heatmap", "uid": "d7e21b98-9f64-40e7-a974-c875e4740833", "options": {"name": "Rao et al. (2014) GM12878 MboI (allreps) 1kb"}}]}, "uid": "e11be3a3-7d19-44f3-a8cc-cffa69f74bbc", "zoomLimits": [1.0, null]}, {"layout": {"x": 6, "y": 0, "w": 6, "h": 6}, "tracks": {"center": [{"tilesetUid": "QvdMEvccQuOxKTEjrVL3wA", "server": "https://higlass.io/api/v1/", "type": "heatmap", "uid": "ee6d1f91-eec5-4b01-b23e-32b90ae5f178", "options": {"name": "Rao et al. (2014) K562 MboI (allreps) 1kb"}}]}, "uid": "0fb1e8dc-2578-4fdd-84af-eae8cca9dab8", "zoomLimits": [1.0, null]}], "zoomLocks": {"locksByViewUid": {"e11be3a3-7d19-44f3-a8cc-cffa69f74bbc": "3d3b7bea-fb4b-44bf-96b0-f4414d30da65", "0fb1e8dc-2578-4fdd-84af-eae8cca9dab8": "3d3b7bea-fb4b-44bf-96b0-f4414d30da65"}, "locksDict": {"3d3b7bea-fb4b-44bf-96b0-f4414d30da65": {"uid": "3d3b7bea-fb4b-44bf-96b0-f4414d30da65", "e11be3a3-7d19-44f3-a8cc-cffa69f74bbc": [1.0, 1.0, 1.0], "0fb1e8dc-2578-4fdd-84af-eae8cca9dab8": [1.0, 1.0, 1.0]}}}, "locationLocks": {"locksByViewUid": {"e11be3a3-7d19-44f3-a8cc-cffa69f74bbc": "3d3b7bea-fb4b-44bf-96b0-f4414d30da65", "0fb1e8dc-2578-4fdd-84af-eae8cca9dab8": "3d3b7bea-fb4b-44bf-96b0-f4414d30da65"}, "locksDict": {"3d3b7bea-fb4b-44bf-96b0-f4414d30da65": {"uid": "3d3b7bea-fb4b-44bf-96b0-f4414d30da65", "e11be3a3-7d19-44f3-a8cc-cffa69f74bbc": [1.0, 1.0, 1.0], "0fb1e8dc-2578-4fdd-84af-eae8cca9dab8": [1.0, 1.0, 1.0]}}}, "valueScaleLocks": {"locksByViewUid": {}, "locksDict": {}}},    );    </script></html>"""
app.layout = html.Div(
    [
        html.H1(children="Title of Dash App", style={"textAlign": "center"}),
        dcc.Dropdown(df.country.unique(), "Canada", id="dropdown-selection"),
        dcc.Graph(id="graph-content"),
        html.Iframe(id="output", src=f"data:text/html;charset=utf-8,{html_str}"),
    ]
)


@callback(Output("graph-content", "figure"), Input("dropdown-selection", "value"))
def update_graph(value):
    dff = df[df.country == value]
    return px.line(dff, x="year", y="pop")


if __name__ == "__main__":
    app.run(debug=True, port=1234)
