import dash_bootstrap_components as dbc
from dash import MATCH, Input, Output, Patch, State, callback, html, callback_context, ALL, dcc
from dash.exceptions import PreventUpdate

from wmb_browser.backend import *

plot_examples = {
    "Gene mCH": ("cemba_cell,continuous_scatter,l1_tsne,gene_mch:Gad1", "primary"),
    "Gene mCG": ("cemba_cell,continuous_scatter,l1_tsne,gene_mcg:Gad1", "primary"),
    "Gene RNA": ("cemba_cell,continuous_scatter,l1_tsne,gene_rna:Gad1", "primary"),
    "Cell Subclass": ("cemba_cell,categorical_scatter,l1_tsne,CellSubClass", "success"),
    "Dissection Region": ("cemba_cell,categorical_scatter,l1_tsne,DissectionRegion", "success"),
    "Cell Subclass MERFISH": ("cemba_cell,categorical_scatter,slice59_merfish,DissectionRegion", "success"),
    "Multi-2D Higlass": (
        "higlass,multi_cell_type_2d,cell_types=CA3 Glut+Sst Gaba,region1=chr1:11000000-12000000",
        "info",
    ),
    "Multi-1D Higlass": (
        "higlass,multi_cell_type_1d,cell_types=CA3 Glut+Sst Gaba,region=chr1:11000000-12000000",
        "info",
    ),
    "Diff Compare Higlass": (
        "higlass,two_cell_type_diff,cell_type_1=CA3 Glut,cell_type_2=Sst Gaba,region1=chr1:10000000-13000000",
        "info",
    ),
    "2D Zoom-in Higlass": (
        (
            "higlass,loop_zoom_in,cell_type=CA3"
            " Glut,region1=chr1:10000000-13000000,zoom_region1=chr1:11550000-11720000,zoom_region2=chr1:12710000-12910000"
        ),
        "info",
    ),
}

# master input card
input_card = dbc.Card(
    [
        dbc.CardHeader("Create your browser layout"),
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Row(
                                    dbc.Button(
                                        "Add Panels",
                                        id="add-btn",
                                        # className="m-1",
                                        color="primary",
                                        n_clicks=0,
                                        size="lg",
                                        style={"width": "70%"},
                                    ),
                                    class_name="m-2",
                                    justify="center",
                                ),
                                dbc.Row(
                                    dbc.Button(
                                        "Open Cell Clipboard",
                                        id="show-clipboard-btn",
                                        # className="m-1",
                                        color="primary",
                                        n_clicks=0,
                                        outline=True,
                                        style={"width": "70%"},
                                    ),
                                    class_name="m-2",
                                    justify="center",
                                ),
                                dbc.Row(
                                    dbc.Button(
                                        "Download Current Layout Config",
                                        id="get-config-btn",
                                        # className="m-1",
                                        color="primary",
                                        n_clicks=0,
                                        outline=True,
                                        style={"width": "70%"},
                                    ),
                                    class_name="m-2",
                                    justify="center",
                                ),
                            ],
                            xxl=2,
                            xl=3,
                            lg=4,
                            md=5,
                            sm=12,
                        ),
                        dbc.Col(
                            [
                                dbc.Row(dbc.Textarea(id="new-item-input", style={"height": 100}), class_name="mb-1"),
                                dbc.Row(
                                    html.Div(
                                        [html.P("Some examples:", className="m-1")]
                                        + [
                                            dbc.Button(
                                                _name,
                                                color=_color,
                                                className="m-1",
                                                outline=True,
                                                size="sm",
                                                id={"index": _name, "type": "example-btn"},
                                            )
                                            for _name, (_, _color) in plot_examples.items()
                                        ]
                                    ),
                                    class_name="mb-1",
                                ),
                            ],
                            xxl=10,
                            xl=9,
                            lg=8,
                            md=7,
                            sm=12,
                        ),
                    ]
                ),
                dbc.Offcanvas(
                    [
                        html.P("These are the most recent cells you clicked on the scatter plots."),
                        dcc.Store(id="cell-clipboard-count", data=[], storage_type="memory"),
                        dbc.Row(id="cell-clipboard-content", children=[]),
                    ],
                    id="offcanvas",
                    title="Cell Metadata Clipboard",
                    style={"width": "40%"},
                    is_open=False,
                ),
            ],
        ),
    ]
)

layout = html.Div(
    [
        html.Div(id="input-div", children=[input_card]),
        html.Div(id="figure-div", className="row"),
    ]
)


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
    graph = None
    graph_controls = None
    tab_width = 4

    try:
        dataset, plot_type, args, kwargs = _string_to_args_and_kwargs(string)
    except Exception as e:
        print(f"Error when parsing string to args and kwargs: \n{string}. Using chatgpt instead.")
        dataset, plot_type, args, kwargs = _chatgpt_string_to_args_and_kwargs(string)
        print(e)

    _plot_datasets = ["cemba_cell"]
    if dataset in _plot_datasets:
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
            raise e
    elif dataset == "higlass":
        try:
            print("args", args)
            print("kwargs", kwargs)
            graph, graph_controls = higlass.get_higlass_and_control(index=i, layout=plot_type, *args, **kwargs)
        except Exception as e:
            print(f"Error when plotting {plot_type} for dataset {dataset}")
            print(e)
        tab_width = 12
    else:
        print(f"Unknown dataset {dataset}")

    return graph, graph_controls, dataset, plot_type, tab_width


@callback(
    Output("offcanvas", "is_open", allow_duplicate=True),
    Input("show-clipboard-btn", "n_clicks"),
    State("offcanvas", "is_open"),
    prevent_initial_call=True,
)
def toggle_clipboard(n_clicks, is_open):
    if n_clicks > 0:
        return not is_open
    return is_open


@callback(
    Output("cell-clipboard-content", "children"),
    Output("cell-clipboard-count", "data"),
    Input({"index": ALL, "type": "categorical_scatter-graph"}, "clickData"),
    Input({"index": ALL, "type": "continuous_scatter-graph"}, "clickData"),
    State("cell-clipboard-count", "data"),
    prevent_initial_call=True,
)
def update_cell_clipboard(cat_click_data, cont_click_data, curr_cell_clip_ids):
    """
    For each click event on scatter plot,
    add a new card containing cell metadata to the clipboard, and turn on the offcanvas
    """
    # # print all inputs
    # print("cat_click_data", cat_click_data)
    # print("cont_click_data", cont_click_data)
    # print("curr_cell_clip_ids", curr_cell_clip_ids)

    patch = Patch()
    update = False
    for data in cat_click_data + cont_click_data:
        if data is None:
            continue
        cell_num_index = data["points"][0]["customdata"][0]
        if cell_num_index in curr_cell_clip_ids:
            continue
        else:
            curr_cell_clip_ids.append(cell_num_index)
            update = True
            if len(curr_cell_clip_ids) > 6:
                del patch[-1]

        card = cemba_cell.get_cell_metadata_markdown(cell_num_index)
        col = dbc.Col(card, xl=6)
        patch.prepend(col)
    if update:
        return patch, curr_cell_clip_ids
    else:
        raise PreventUpdate


@callback(
    Output("new-item-input", "value", allow_duplicate=True),
    Input({"index": ALL, "type": "example-btn"}, "n_clicks"),
    State("new-item-input", "value"),
    prevent_initial_call=True,
)
def add_example(n_clicks, cur_value):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        trigger_id = callback_context.triggered_id["index"]
        text = plot_examples[trigger_id][0]
        if cur_value is None or cur_value == "":
            return text
        else:
            return cur_value + "\n" + text


# Callback to add new item to list
@callback(
    Output("figure-div", "children", allow_duplicate=True),
    Output("new-item-input", "value", allow_duplicate=True),
    Input("add-btn", "n_clicks"),
    State("new-item-input", "value"),
    prevent_initial_call=True,
)
def add_figure(button_clicked, value):
    if value is None or value == "":
        raise PreventUpdate

    patched_fig_list = Patch()

    def new_figure_item(i, string):
        graph, graph_controls, dataset, plot_type, tab_width = _make_graph_from_string(i, string)

        if dataset == "higlass":
            width = 12
            xl = 12
            lg = 12
        else:
            width = 12
            xl = 4
            lg = 6

        if graph is None:
            return None

        plot_title = plot_type.replace("_", " ").capitalize()
        tabs = dbc.Col(
            dbc.Tabs(
                [
                    dbc.Tab(graph, label=plot_title),
                    dbc.Tab(graph_controls, label="Control"),
                ]
            ),
            width=width,
            xl=xl,
            lg=lg,
            class_name="mt-3",
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
    Output("figure-div", "children", allow_duplicate=True),
    Input({"index": ALL, "type": "delete-figure-btn"}, "n_clicks"),
    prevent_initial_call=True,
)
def delete_fugure(n_clicks):
    if sum(n_clicks) == 0:
        raise PreventUpdate

    patched_list = Patch()
    values_to_remove = []
    # example callback_context.inputs_list
    # [[{'id': {'index': '1-0', 'type': 'delete-figure-btn'}, 'property': 'n_clicks', 'value': 1}]]
    for i, click in enumerate(n_clicks):
        if click > 0:
            # del button is clicked
            values_to_remove.insert(0, i)
    for v in values_to_remove:
        del patched_list[v]
    return patched_list


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


@callback(
    Output({"index": ALL, "type": "continuous_scatter-graph"}, "figure", allow_duplicate=True),
    Output({"index": ALL, "type": "categorical_scatter-graph"}, "figure", allow_duplicate=True),
    Input({"index": ALL, "type": "continuous_scatter-graph"}, "relayoutData"),
    Input({"index": ALL, "type": "categorical_scatter-graph"}, "relayoutData"),
    State({"index": ALL, "type": "coord_input"}, "value"),
    prevent_initial_call=True,
)
def update_scatter_graph_relayout_data(cont_args, cat_args, coords):
    trigger = callback_context.triggered[0]
    trigger_layout = trigger["value"]

    if "autosize" in trigger_layout:
        raise PreventUpdate
    else:
        try:
            xaxis_min = trigger_layout["xaxis.range[0]"]
            xaxis_max = trigger_layout["xaxis.range[1]"]
            yaxis_min = trigger_layout["yaxis.range[0]"]
            yaxis_max = trigger_layout["yaxis.range[1]"]
        except KeyError:
            raise PreventUpdate

    # get coord for each index
    idx_to_coord = {}
    for state_dict in callback_context.states_list[0]:
        idx = state_dict["id"]["index"]
        coord = state_dict["value"]
        idx_to_coord[idx] = coord
    trigger_coord = idx_to_coord[callback_context.triggered_id["index"]]

    cont_inputs, cat_inputs = callback_context.inputs_list
    cont_outputs, cat_outputs = [], []

    # print all states
    # print("cont_args", cont_args)
    # print("cat_args", cat_args)
    # print("coords", coords)
    # print("trigger", trigger)
    # print("trigger_layout", trigger_layout)

    for input in cont_inputs:
        _p = Patch()
        coord = idx_to_coord[input["id"]["index"]]
        if coord == trigger_coord:
            _p["layout"]["xaxis"]["range"] = [xaxis_min, xaxis_max]
            _p["layout"]["yaxis"]["range"] = [yaxis_min, yaxis_max]
        cont_outputs.append(_p)

    for input in cat_inputs:
        _p = Patch()
        coord = idx_to_coord[input["id"]["index"]]
        if coord == trigger_coord:
            _p["layout"]["xaxis"]["range"] = [xaxis_min, xaxis_max]
            _p["layout"]["yaxis"]["range"] = [yaxis_min, yaxis_max]
        cat_outputs.append(_p)

    return cont_outputs, cat_outputs


# TODO click and select event callback for categorical scatter


@callback(
    Output({"index": MATCH, "type": "higlass-multi_cell_type_2d-iframe"}, "srcDoc"),
    Output({"index": MATCH, "type": "higlass-multi_cell_type_2d-iframe"}, "style"),
    Input({"index": MATCH, "type": "multi_cell_type_2d-update-btn"}, "n_clicks"),
    State({"index": MATCH, "type": "multi_cell_type_2d-cell-types-dropdown"}, "value"),
    State({"index": MATCH, "type": "multi_cell_type_2d-modality_2d-dropdown"}, "value"),
    State({"index": MATCH, "type": "multi_cell_type_2d-modality_1d-dropdown"}, "value"),
    State({"index": MATCH, "type": "multi_cell_type_2d-region1-input"}, "value"),
    State({"index": MATCH, "type": "multi_cell_type_2d-region2-input"}, "value"),
    prevent_initial_call=True,
)
def update_multi_cell_type_2d_graph(n_clicks, cell_types, modality_2d, modality_1d, region1, region2):
    layout = "multi_cell_type_2d"
    if cell_types is None:
        raise PreventUpdate
    html, html_height = higlass.get_higlass_html(
        layout,
        cell_types=cell_types,
        modality_2d=modality_2d,
        modality_1d=modality_1d,
        region1=region1,
        region2=region2,
    )

    _style = {"height": f"{html_height}px", "border": "none"}
    return html, _style


@callback(
    Output({"index": MATCH, "type": "higlass-multi_cell_type_1d-iframe"}, "srcDoc"),
    Output({"index": MATCH, "type": "higlass-multi_cell_type_1d-iframe"}, "style"),
    Input({"index": MATCH, "type": "multi_cell_type_1d-update-btn"}, "n_clicks"),
    State({"index": MATCH, "type": "multi_cell_type_1d-cell-types-dropdown"}, "value"),
    State({"index": MATCH, "type": "multi_cell_type_1d-modalities-dropdown"}, "value"),
    State({"index": MATCH, "type": "multi_cell_type_1d-region-input"}, "value"),
    State({"index": MATCH, "type": "multi_cell_type_1d-colorby-sel"}, "value"),
    State({"index": MATCH, "type": "multi_cell_type_1d-groupby-sel"}, "value"),
    prevent_initial_call=True,
)
def update_multi_cell_type_1d_graph(n_clicks, cell_types, modalities, region, colorby, groupby):
    layout = "multi_cell_type_1d"
    if cell_types is None:
        raise PreventUpdate
    html, html_height = higlass.get_higlass_html(
        layout,
        cell_types=cell_types,
        modalities=modalities,
        region=region,
        colorby=colorby,
        groupby=groupby,
    )
    _style = {"height": f"{html_height}px", "border": "none"}
    return html, _style


@callback(
    Output({"index": MATCH, "type": "higlass-two_cell_type_diff-iframe"}, "srcDoc"),
    Output({"index": MATCH, "type": "higlass-two_cell_type_diff-iframe"}, "style"),
    Input({"index": MATCH, "type": "two_cell_type_diff-update-btn"}, "n_clicks"),
    State({"index": MATCH, "type": "two_cell_type_diff-cell-type-1-dropdown"}, "value"),
    State({"index": MATCH, "type": "two_cell_type_diff-cell-type-2-dropdown"}, "value"),
    State({"index": MATCH, "type": "two_cell_type_diff-modality_2d-dropdown"}, "value"),
    State({"index": MATCH, "type": "two_cell_type_diff-modality_1d-dropdown"}, "value"),
    State({"index": MATCH, "type": "two_cell_type_diff-region1-input"}, "value"),
    State({"index": MATCH, "type": "two_cell_type_diff-region2-input"}, "value"),
    prevent_initial_call=True,
)
def update_two_cell_type_diff_graph(n_clicks, cell_type_1, cell_type_2, modality_2d, modality_1d, region1, region2):
    layout = "two_cell_type_diff"

    if cell_type_1 is None or cell_type_2 is None:
        raise PreventUpdate

    html, html_height = higlass.get_higlass_html(
        layout,
        cell_type_1=cell_type_1,
        cell_type_2=cell_type_2,
        modality_2d=modality_2d,
        modality_1d=modality_1d,
        region1=region1,
        region2=region2,
    )
    _style = {"height": f"{html_height}px", "border": "none"}
    return html, _style


@callback(
    Output({"index": MATCH, "type": "higlass-loop_zoom_in-iframe"}, "srcDoc"),
    Output({"index": MATCH, "type": "higlass-loop_zoom_in-iframe"}, "style"),
    Input({"index": MATCH, "type": "loop_zoom_in-update-btn"}, "n_clicks"),
    State({"index": MATCH, "type": "loop_zoom_in-cell-type-dropdown"}, "value"),
    State({"index": MATCH, "type": "loop_zoom_in-modality_2d-dropdown"}, "value"),
    State({"index": MATCH, "type": "loop_zoom_in-modality_1d-dropdown"}, "value"),
    State({"index": MATCH, "type": "loop_zoom_in-region1-input"}, "value"),
    State({"index": MATCH, "type": "loop_zoom_in-region2-input"}, "value"),
    State({"index": MATCH, "type": "loop_zoom_in-zoom-region1-input"}, "value"),
    State({"index": MATCH, "type": "loop_zoom_in-zoom-region2-input"}, "value"),
    prevent_initial_call=True,
)
def update_loop_zoom_in_graph(
    n_clicks, cell_type, modality_2d, modality_1d, region1, region2, zoom_region1, zoom_region2
):
    layout = "loop_zoom_in"

    if cell_type is None:
        raise PreventUpdate

    html, html_height = higlass.get_higlass_html(
        layout,
        cell_type=cell_type,
        modality_2d=modality_2d,
        modality_1d=modality_1d,
        region1=region1,
        region2=region2,
        zoom_region1=zoom_region1,
        zoom_region2=zoom_region2,
    )
    _style = {"height": f"{html_height}px", "border": "none"}
    return html, _style


def create_dynamic_browser_layout(*args, **kwargs):
    return layout
