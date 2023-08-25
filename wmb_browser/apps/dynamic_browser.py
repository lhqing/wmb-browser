from dash import Dash, dcc, html, Input, Output, State, MATCH, ALL, Patch, callback
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from wmb_browser._app import app
from wmb_browser.backend import *

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

layout = html.Div([html.Div(id="input-div", children=[card]), html.Div(id="figure-div", className="row")])


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


def _make_graph_from_string(i, string):
    graph_title = ''
    empty_fig = {
        "data": [],
        "layout": {},
        "frames": [],
    }

    try:
        dataset, plot_type, args, kwargs = _string_to_args_and_kwargs(string)
    except Exception as e:
        print(f"Error when parsing string to args and kwargs: \n{string}")
        print(e)
        fig = empty_fig

    dataset_cls = globals().get(dataset, None)
    if dataset_cls is None:
        print(f"Unknown dataset {dataset}")
        fig =  empty_fig

    plot_func = getattr(dataset_cls, plot_type, None)
    if plot_func is None:
        print(f"Unknown plot type {plot_type} for dataset {dataset}")
        return empty_fig

    try:
        print("args:", args)
        print("kwargs:", kwargs)
        print("plot_func:", plot_func)
        graph_title, fig = plot_func(*args, **kwargs)
    except Exception as e:
        print(f"Error when plotting {plot_type} for dataset {dataset}")
        print(e)
        fig =  empty_fig
    
    g= dcc.Graph(
            id={"type": "graph", "index": i},
            figure=fig,
            style={"height": "80vh", "width": "auto"},
        )
    
    return graph_title, g


# Callback to add new item to list
@callback(
    Output("figure-div", "children", allow_duplicate=True),
    Output("new-item-input", "value"),
    Input("add-btn", "n_clicks"),
    State("new-item-input", "value"),
    prevent_initial_call=True,
)
def add_figure(button_clicked, value):
    print("add_figure", button_clicked, value)
    if value is None or value == "":
        raise PreventUpdate

    patched_fig_list = Patch()

    def new_figure_item(i, string):
        tab1_title, tab1_content = _make_graph_from_string(i, string)

        tab2_content = html.Div()

        tabs = html.Div(
            dbc.Tabs(
                [
                    dbc.Tab(tab1_content, label=tab1_title),
                    dbc.Tab(tab2_content, label="Graph Control"),
                ]
            ),
            className="mt-3 col-4",
        )

        return tabs

    for line in value.split("\n"):
        if line.strip() == "":
            continue
        else:
            tabs = new_figure_item(button_clicked, line)
            patched_fig_list.append(tabs)
    return patched_fig_list, ""


def create_dynamic_browser_layout(*args, **kwargs):
    return layout
