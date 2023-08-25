from dash import Dash, dcc, html, Input, Output, State, MATCH, ALL, Patch, callback
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

# master input card
card = dbc.Card(
    [
        dbc.CardHeader("Create your own browser layout"),
        dbc.CardBody(
            [
                dbc.Textarea(id="new-item-input"),
                html.P(
                    "Some quick example and url to detail documentation.",
                    className="card-text",
                ),
                dbc.Button("Add", id="add-btn", outline=True, color="primary", n_clicks=0),
            ]
        ),
    ]
)

layout = html.Div(
    [
        html.Div(id="input-div", children=[card]),
        html.Div([html.P('fig')], id="figure-div"),
        html.Div([html.P('control')], id="control-div"),
    ]
)


# Callback to add new item to list
@callback(
    Output("figure-div", "children", allow_duplicate=True),
    Output("control-div", "children", allow_duplicate=True),
    Output("new-item-input", "value"),
    Input("add-btn", "n_clicks"),
    State("new-item-input", "value"),
    prevent_initial_call=True,
)
def add_figure(button_clicked, value):
    if value is None or value == "":
        raise PreventUpdate
    
    patched_fig_list = Patch()
    patched_control_list = Patch()

    def new_figure_item(i):
        graph = html.Div(
            [
                html.P(f"figure {i}, {value}"),
                dcc.Graph(
                    id={"index": i, "type": "graph"},
                ),
            ]
        )

        graph_control = html.Div(
            html.P(f"control {i}"),
            id={"index": i, "type": "graph-control"},
        )

        return graph, graph_control

    graph, graph_control = new_figure_item(button_clicked)
    patched_fig_list.append(graph)
    patched_control_list.append(graph_control)
    return patched_fig_list, patched_control_list, ""


def create_dynamic_browser_layout(*args, **kwargs):
    return layout
