from dash import Dash, dcc, html, Input, Output, State, MATCH, ALL, Patch, callback
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from wmb_browser.backend import *
import re

plot_examples = """
cemba_cell,continuous_scatter,l1_tsne,gene_mch:Gad1 
cemba_cell,categorical_scatter,l1_tsne,CellSubClass 
cemba_cell,categorical_scatter,l1_tsne,DissectionRegion
"""

# master input card
input_card = dbc.Card(
    [
        dbc.CardHeader("Create your own browser layout"),
        dbc.CardBody(
            [
                dbc.Textarea(id="new-item-input"),
                html.P(
                    f"Some quick examples: {plot_examples}",
                    className="card-text",
                ),
                dbc.Button("Add", id="add-btn", outline=True, color="primary", n_clicks=0),
            ]
        ),
    ]
)

layout = html.Div([html.Div(id="input-div", children=[input_card]), html.Div(id="figure-div", className="row")])


def _string_to_args_and_kwargs(string):
    args = []
    kwargs = {}
    for text in string.split(","):
        text = text.strip()
        kv = text.split("=")
        if len(kv) == 1:
            args.append(text)
        elif len(kv) == 2:
            kwargs[kv[0]] = kv[1]
        else:
            raise ValueError(f"Cannot parse {text}")

    # assume the first arg is dataset
    dataset, plot_type, *args = args
    return dataset, plot_type, args, kwargs

def _chatgpt_string_to_args_and_kwargs(string):
    dataset, plot_type, kwargs = gpt_function_call.parse_user_input(string)
    return dataset, plot_type, [], kwargs


def _make_graph_from_string(i, string):
    graph_title = ""
    graph = None
    graph_controls = None

    try:
        dataset, plot_type, args, kwargs = _string_to_args_and_kwargs(string)
    except Exception as e:
        print(f"Error when parsing string to args and kwargs: \n{string}")
        print(e)

    dataset_cls = globals().get(dataset, None)
    if dataset_cls is None:
        print(f"Unknown dataset {dataset}")

    plot_func = getattr(dataset_cls, plot_type, None)
    if plot_func is None:
        print(f"Unknown plot type {plot_type} for dataset {dataset}")

    try:
        graph, graph_controls = plot_func(i, *args, **kwargs)
    except Exception as e:
        print(f"Error when plotting {plot_type} for dataset {dataset}")
        print(e)

    return graph, graph_controls, plot_type


# Callback to add new item to list
@callback(
    Output("figure-div", "children", allow_duplicate=True),
    Output("new-item-input", "value"),
    Input("add-btn", "n_clicks"),
    State("new-item-input", "value"),
    prevent_initial_call=True,
)
def add_figure(button_clicked, value):
    if value is None or value == "":
        raise PreventUpdate

    patched_fig_list = Patch()

    def new_figure_item(i, string):
        graph, graph_controls, plot_type = _make_graph_from_string(i, string)

        if graph is None:
            return None

        plot_title = plot_type.replace("_", " ").capitalize()
        tabs = html.Div(
            dbc.Tabs([dbc.Tab(graph, label=plot_title), dbc.Tab(graph_controls, label="Control")]),
            className="mt-3 col-4",
        )
        return tabs

    for line_idx, line in enumerate(value.split("\n")):
        if line.strip() == "":
            continue
        else:
            tabs = new_figure_item(f"{button_clicked}-{line_idx}", line)
            if tabs is None:
                print("Error when creating new figure item with string: ", line)
                # TODO add error message
                continue
            patched_fig_list.append(tabs)
    return patched_fig_list, ""


@callback(
    Output({"index": MATCH, "type": "continuous_scatter-graph"}, "figure"),
    Input({"index": MATCH, "type": "continuous_scatter_update-btn"}, "n_clicks"),
    State({"index": MATCH, "type": "color_input"}, "value"),
    State({"index": MATCH, "type": "color_range"}, "value"),
    State({"index": MATCH, "type": "coord_input"}, "value"),
    State({"index": MATCH, "type": "sample_input"}, "value"),
    prevent_initial_call=True,
)
def update_continous_scatter_graph(n_clicks, color, color_range, coord, sample):
    fig = cemba_cell.continuous_scatter_figure(
        color=color,
        color_range=color_range,
        coord=coord,
        sample=sample,
        marker_size="auto",
    )
    return fig


@callback(
    Output({"index": MATCH, "type": "categorical_scatter-graph"}, "figure"),
    Input({"index": MATCH, "type": "categorical_scatter_update-btn"}, "n_clicks"),
    State({"index": MATCH, "type": "color_input"}, "value"),
    State({"index": MATCH, "type": "coord_input"}, "value"),
    State({"index": MATCH, "type": "sample_input"}, "value"),
    prevent_initial_call=True,
)
def update_categorical_scatter_graph(n_clicks, color, coord, sample):
    fig = cemba_cell.categorical_scatter_figure(
        color=color,
        coord=coord,
        sample=sample,
        marker_size="auto",
    )
    return fig


def create_dynamic_browser_layout(*args, **kwargs):
    return layout
