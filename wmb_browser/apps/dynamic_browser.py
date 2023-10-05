import dash_bootstrap_components as dbc
from dash import MATCH, Input, Output, Patch, State, callback, html, callback_context, ALL, dcc
from dash.exceptions import PreventUpdate
import base64
from wmb_browser.backend import *
import re

MAX_FIGURE_NUM = 8

plot_examples = {
    "Gene mCH": ("cemba_cell,continuous_scatter,mc_all_tsne,gene_mch:Gad1", "primary"),
    "Gene mCG": ("cemba_cell,continuous_scatter,mc_all_tsne,gene_mcg:Gad1", "primary"),
    "Gene RNA": ("cemba_cell,continuous_scatter,mc_all_tsne,gene_rna:Gad1", "primary"),
    "Cell Subclass": ("cemba_cell,categorical_scatter,mc_all_tsne,CellSubClass", "success"),
    "Dissection Region": ("cemba_cell,categorical_scatter,mc_all_tsne,DissectionRegion", "success"),
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

gpt_plot_examples = {
    "Gene mCH": ("Make a scatter plot for Gad1 gene body mCH", "primary"),
    "Gene mCG": ("Show me a scatter plot for Gad1 gene body mCG, using the umap coords", "primary"),
    "Gene RNA": ("What is the Gad1 gene body RNA level looks like on Isocortex umap scatter plot?", "primary"),
    "Cell Subclass": ("Give me a scatter plot of whole brain cells colored by subclass", "success"),
    "Dissection Region": ("A scatter plot colored by dissection regions", "success"),
    "Cell Subclass MERFISH": ("Plot dissection regions on a merfish slice", "success"),
    "Multi-2D Higlass": (
        (
            "Show me a multi 2D higlass browser with three cell types: CA3 Glut, Sst Gaba, STR D2 Gaba, plot at the"
            " Nfia gene locus"
        ),
        "info",
    ),
    "Multi-1D Higlass": (
        (
            "Make a multi 1D higlass browser with three cell types: CA3 Glut, Sst Gaba, STR D2 Gaba, and plot mCH, mCG,"
            " ATAC, Domain boundary tracks. Plot at the Nrxn3 gene locus."
        ),
        "info",
    ),
    "Diff Compare Higlass": (
        (
            "Compare the mCH, mCG and chrom 10K 3C matrix difference between CA3 Glut and Sst Gaba, plot at region"
            " chr1:10000000-13000000"
        ),
        "info",
    ),
    "2D Zoom-in Higlass": (
        (
            "Make a higlass zoom in layout for cell type CA3 Glut, at region chr1:10000000-13000000, add mCH, mCG and"
            " ATAC tracks"
        ),
        "info",
    ),
}

ALL_DATASETS = ["cemba_cell", "higlass"]
ALL_PLOT_TYPES = [
    "continuous_scatter",
    "categorical_scatter",
    "multi_cell_type_2d",
    "multi_cell_type_1d",
    "two_cell_type_diff",
    "loop_zoom_in",
]


layout_buttons = [
    dbc.Row(
        dbc.Button(
            "Add Panels",
            id="add-btn",
            # className="m-1",
            color="primary",
            n_clicks=0,
            size="lg",
            style={"width": "100%"},
        ),
        class_name="m-2",
        justify="center",
    ),
    dbc.Row(
        dbc.Col(
            dbc.Checklist(
                options=[
                    {"label": "Use ChatGPT", "value": 1},
                ],
                value=[],
                id="chatgpt_switch",
                switch=True,
            ),
            width={"size": 6, "offset": 3},
        ),
        class_name="mt-1 mb-2",
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
            style={"width": "100%"},
        ),
        class_name="m-2",
        justify="center",
    ),
    dbc.Row(
        dbc.Button(
            "Download Current Layout Config",
            id="download-config-btn",
            # className="m-1",
            color="primary",
            n_clicks=0,
            outline=True,
            style={"width": "100%"},
        ),
        class_name="m-2",
        justify="center",
    ),
]

layout_inputs = dbc.Row(
    [
        dbc.Col(
            dbc.Textarea(id="new-item-input", style={"height": 100}),
            className="mb-1",
            width=12,
            xxl=10,
            xl=10,
            lg=8,
            md=6,
            sm=12,
        ),
        dbc.Col(
            dcc.Upload(
                id="upload-area",
                children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
                style={
                    "width": "100%",
                    "height": 100,
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                },
                className="d-flex align-items-center",
                max_size=1024 * 1024 * 5,
            ),
            className="mb-1",
            width=12,
            xxl=2,
            xl=2,
            lg=4,
            md=6,
            sm=12,
        ),
    ],
    class_name="my-2",
)
layout_example_btns = dbc.Row(
    html.Div(
        [html.P("Some formatted examples:", className="my-1")]
        + [
            dbc.Button(
                _name,
                color=_color,
                className="my-1 mr-2",
                outline=True,
                size="sm",
                id={"index": _name, "type": "example-btn"},
            )
            for _name, (_, _color) in plot_examples.items()
        ]
    ),
)

layout_gpt_example_btns = dbc.Row(
    html.Div(
        [html.P("Some ChatGPT examples:", className="my-1")]
        + [
            dbc.Button(
                _name,
                color=_color,
                className="my-1 mr-2",
                outline=True,
                size="sm",
                id={"index": _name + "_gpt", "type": "example-btn"},
            )
            for _name, (_, _color) in gpt_plot_examples.items()
        ]
    ),
)
gpt_tips_and_warnings = dbc.Row(
    [
        dbc.Alert(
             "Tips: You can click above buttons to get a sense of what you can ask ChatGPT to do. Only talk about one panel at each line, be sure to say its a 'scatter plot' or a 'higlass browser'.",
            className="m-2",
            dismissable=True,
            color="info",
            style={"width": "90%"},
        ),
        dbc.Alert(
            [
                "The ChatGPT model cost additional money to run (see ",
                html.A("Pricing", href="https://openai.com/pricing", target="_blank"),
                "). Please be mindful when using it, thank you and enjoy!",
            ],
            className="m-2",
            dismissable=True,
            color="warning",
            style={"width": "90%"},
        ),
    ]
)

# master input card
input_card = dbc.Card(
    [
        dbc.CardHeader("Create your browser layout"),
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            layout_buttons,
                            xxl=3,
                            xl=3,
                            lg=5,
                            md=5,
                            sm=12,
                        ),
                        dbc.Col(
                            [
                                layout_inputs,
                                layout_example_btns,
                                dbc.Row(
                                    dbc.Collapse(
                                        [layout_gpt_example_btns, gpt_tips_and_warnings],
                                        id="gpt_example_collapse",
                                        is_open=False,
                                    )
                                ),
                            ],
                            xxl=9,
                            xl=9,
                            lg=7,
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


def _string_to_args_and_kwargs(string):

    # convert "%20" to " " using regex
    print(string)
    string = re.sub(r"%20", " ", string)
    print(string)

    string = string.strip(" ?,")
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

    if dataset not in ALL_DATASETS:
        raise ValueError(f"Unknown dataset {dataset}")
    if plot_type not in ALL_PLOT_TYPES:
        raise ValueError(f"Unknown plot type {plot_type} for dataset {dataset}")

    return dataset, plot_type, args, kwargs


def _make_graph_from_string(i, string, use_gpt=False):
    graph = None
    graph_controls = None

    try:
        dataset, plot_type, args, kwargs = _string_to_args_and_kwargs(string)
    except Exception as e:
        if use_gpt:
            print(f"Error when parsing string to args and kwargs directly. Using chatgpt instead.")
            try:
                dataset, plot_type, args, kwargs = chatgpt_string_to_args_and_kwargs(string)
            except Exception as e:
                print(f"Error when parsing string to args and kwargs using chatgpt: {string}")
                print(e)
                return None, None, None, None, None
        else:
            print(f"Error when parsing string to args and kwargs: \n{string}")
            print(e)
            return None, None, None, None, None

    print("dataset", dataset)
    print("plot_type", plot_type)
    print("args", args)
    print("kwargs", kwargs)

    final_string = f"{dataset},{plot_type}"
    if len(args) > 0:
        final_string += f",{','.join(args)}"
    if len(kwargs) > 0:
        final_string += f",{','.join([f'{k}={v}' for k, v in kwargs.items()])}"

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
            graph, graph_controls = higlass.get_higlass_and_control(index=i, layout=plot_type, *args, **kwargs)
        except Exception as e:
            print(f"Error when plotting {plot_type} for dataset {dataset}")
            print(e)
    else:
        print(f"Unknown dataset {dataset}")

    return graph, graph_controls, dataset, plot_type, final_string


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
        if trigger_id.endswith("_gpt"):
            text = gpt_plot_examples[trigger_id[:-4]][0]
        else:
            text = plot_examples[trigger_id][0]
        if cur_value is None or cur_value == "":
            return text
        else:
            return cur_value + "\n" + text


def _new_figure_item(i, string, use_gpt=False):
    graph, graph_controls, dataset, plot_type, final_string = _make_graph_from_string(i, string, use_gpt=use_gpt)
    if graph is None:
        return None, None

    if dataset == "higlass":
        width = 12
        xl = 12
        lg = 12
    else:
        width = 12
        xl = 4
        lg = 6

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
    return tabs, final_string


# Callback to add new item to list
@callback(
    Output("figure-div", "children", allow_duplicate=True),
    Output("new-item-input", "value", allow_duplicate=True),
    Output("layout-config", "data", allow_duplicate=True),
    Output("too-many-fig-alert", "is_open"),
    Input("add-btn", "n_clicks"),
    State("new-item-input", "value"),
    State("layout-config", "data"),
    State("chatgpt_switch", "value"),
    prevent_initial_call=True,
)
def add_figure(button_clicked, value, layout_config, use_gpt):
    use_gpt = len(use_gpt) > 0

    if value is None or value == "":
        raise PreventUpdate

    cur_figs = len(layout_config)
    show_alert = True

    patched_fig_list = Patch()
    patched_layout_config = Patch()

    if cur_figs >= MAX_FIGURE_NUM:
        return patched_fig_list, value, patched_layout_config, show_alert

    for line_idx, line in enumerate(value.split("\n")):
        if line.strip() == "":
            continue
        else:
            index = f"{button_clicked}-{line_idx}"
            tabs, final_string = _new_figure_item(index, line, use_gpt=use_gpt)
            if tabs is None:
                print("Error when creating new figure item with string: ", line)
                # TODO add error message
                continue
            patched_fig_list.append(tabs)
            patched_layout_config[index] = {"string": final_string}
            cur_figs += 1
            if cur_figs >= MAX_FIGURE_NUM:
                break
    else:
        show_alert = False
    return patched_fig_list, "", patched_layout_config, show_alert


@callback(
    Output("figure-div", "children", allow_duplicate=True),
    Output("layout-config", "data", allow_duplicate=True),
    Input({"index": ALL, "type": "delete-figure-btn"}, "n_clicks"),
    prevent_initial_call=True,
)
def delete_fugure(n_clicks):
    if sum(n_clicks) == 0:
        raise PreventUpdate

    patched_layout_config = Patch()
    trigger_id = callback_context.triggered_id["index"]
    del patched_layout_config[trigger_id]

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
    return patched_list, patched_layout_config


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


@callback(
    Output("download-layout-config", "data"),
    Input("download-config-btn", "n_clicks"),
    State("layout-config", "data"),
    prevent_initial_call=True,
)
def download_layout_config(n_clicks, layout_config):
    if n_clicks == 0:
        raise PreventUpdate

    content = "\n".join([v["string"] for v in layout_config.values()])
    file_name = "layout_config.txt"
    download_dict = dict(content=content, filename=file_name)
    return download_dict


@callback(
    Output("gpt_example_collapse", "is_open"),
    Input("chatgpt_switch", "value"),
)
def toggle_gpt_example_collapse(value):
    if len(value) > 0:
        return True
    else:
        return False


@callback(
    Output("new-item-input", "value"),
    Output("add-btn", "n_clicks"),
    Input("upload-area", "contents"),
    State("add-btn", "n_clicks"),
)
def upload_layout_config(contents, n_clicks):
    if contents is None:
        raise PreventUpdate

    data = contents.split(",")[1]
    # from base64 to utf-8
    data = base64.b64decode(data).decode("utf-8")
    return data, n_clicks + 1


def create_dynamic_browser_layout(search: str):
    fig_list = []
    layout_config = {}

    if search is None:
        search == ""
    search = search.strip("\n? ")

    button_clicked = 0
    fig_count = 0
    show_alert = True
    for line_idx, line in enumerate(search.split("?")):
        if line.strip() == "":
            continue
        else:
            index = f"{button_clicked}-{line_idx}"
            tabs, final_string = _new_figure_item(index, line, use_gpt=False)
            if tabs is None:
                print("Error when creating new figure item with string: ", line)
                # TODO add error message
                continue
            fig_list.append(tabs)
            layout_config[index] = {"string": final_string}
            fig_count += 1
            if fig_count >= MAX_FIGURE_NUM:
                break
    else:
        show_alert = False

    too_many_fig_alert = dbc.Row(
        dbc.Alert(
            f"Too many panels created, only the first {MAX_FIGURE_NUM} panels are shown.",
            id="too-many-fig-alert",
            color="danger",
            dismissable=True,
            is_open=show_alert,
            duration=8000,
        )
    )

    layout = html.Div(
        [
            html.Div(id="input-div", children=[input_card] + [too_many_fig_alert]),
            html.Div(id="figure-div", children=fig_list, className="row"),
            dcc.Store(id="layout-config", data=layout_config, storage_type="memory"),
            dcc.Download(id="download-layout-config"),
        ]
    )
    return layout
