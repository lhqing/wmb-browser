import inspect

import dash_bootstrap_components as dbc
from dash import dcc, html

from .higlass import HiglassBrowser, string_to_list


class HiglassDash(HiglassBrowser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        return

    def _get_iframe(self, index, layout, *args, **kwargs):
        html_text, html_height = self.get_higlass_html(layout, *args, **kwargs)
        iframe = html.Iframe(
            srcDoc=html_text,
            style={"height": f"{html_height}px", "border": "none"},  #
            id={"index": index, "type": f"higlass-{layout}-iframe"},
            className="col-12",
        )
        return iframe

    def _get_layout_control_form(self, index, layout, *args, **kwargs):
        try:
            control_func = getattr(self, f"_get_{layout}_control")
        except AttributeError:
            print(f"Layout {layout} does not have control form.")
            return dbc.Form()
        control_form = control_func(index, *args, **kwargs)
        return control_form

    def _generate_cell_type_dropdown(self, index, value, multi=False):
        comp = dcc.Dropdown(
            options=[{"label": ct, "value": ct} for ct in self.subclass_list], id=index, value=value, multi=multi
        )
        return comp

    def _get_multi_cell_type_2d_control(self, index, *args, **kwargs):
        layout_name = "multi_cell_type_2d"

        viewconf_func = getattr(self, f"{layout_name}_viewconf")
        default_kwargs = {k: v.default for k, v in inspect.signature(viewconf_func).parameters.items()}
        kwargs = {**default_kwargs, **kwargs}

        # cell types multi-select
        cell_types = kwargs.get("cell_types", "")
        cell_types = string_to_list(cell_types)
        cell_types_control = dbc.Row(
            [
                dbc.Label("Cell Types", width="auto"),
                dbc.Col(
                    self._generate_cell_type_dropdown(
                        index={"index": index, "type": f"{layout_name}-cell-types-dropdown"},
                        value=cell_types,
                        multi=True,
                    )
                ),
            ], class_name='mb-3 mt-3'
        )
        # modality 2d single select
        modality_2d = kwargs.get("modality_2d", None)
        if modality_2d is None:
            modality_2d = self.default_modality_2d
        modality_2d_control = dbc.Row(
            [
                dbc.Label("Modality", width="auto"),
                dbc.Col(
                    dcc.Dropdown(
                        options=[{"label": mod, "value": mod} for mod in self.all_modality_2d],
                        id={"index": index, "type": f"{layout_name}-modality_2d-dropdown"},
                        value=modality_2d,
                        multi=False,
                    )
                ),
            ], class_name='mb-3'
        )

        # modality 1d multi-select
        modality_1d = kwargs.get("modality_1d", None)
        if modality_1d is None:
            modality_1d = self.default_modality_1d
        modality_1d_control = dbc.Row(
            [
                dbc.Label("Modality", width="auto"),
                dbc.Col(
                    dcc.Dropdown(
                        options=[{"label": mod, "value": mod} for mod in self.all_modality_1d],
                        id={"index": index, "type": f"{layout_name}-modality_1d-dropdown"},
                        value=modality_1d,
                        multi=True,
                    )
                ),
            ], class_name='mb-3'
        )
        # region1 text input
        region1 = kwargs.get("region1", None)
        region1_control = dbc.Row(
            [
                dbc.Label("Region 1", width="auto"),
                dbc.Col(
                    dbc.Input(
                        id={"index": index, "type": f"{layout_name}-region1-input"},
                        value=region1,
                        type="text",
                    )
                ),
            ], class_name='mb-3'
        )
        # region2 text input
        region2 = kwargs.get("region2", None)
        region2_control = dbc.Row(
            [
                dbc.Label("Region 2", width="auto"),
                dbc.Col(
                    dbc.Input(
                        id={"index": index, "type": f"{layout_name}-region2-input"},
                        value=region2,
                        type="text",
                    )
                ),
            ], class_name='mb-3'
        )

        # final update button
        update_button = dbc.Button(
            "Update",
            id={"index": index, "type": f"{layout_name}-update-btn"},
            outline=True,
            color="primary",
            n_clicks=0,
            class_name='m-3',
        )

        # put all control components into a form
        form = dbc.Form(
            [
                cell_types_control,
                modality_2d_control,
                modality_1d_control,
                region1_control,
                region2_control,
                update_button,
            ],
            className="col-12",
        )
        return form

    def _get_multi_cell_type_1d_control(self, index, *args, **kwargs):
        layout_name = "multi_cell_type_1d"

        viewconf_func = getattr(self, f"{layout_name}_viewconf")
        default_kwargs = {k: v.default for k, v in inspect.signature(viewconf_func).parameters.items()}
        kwargs = {**default_kwargs, **kwargs}

        # cell types multi-select
        cell_types = kwargs.get("cell_types", "")
        cell_types = string_to_list(cell_types)
        cell_types_control = dbc.Row(
            [
                dbc.Label("Cell Types", width="auto"),
                dbc.Col(
                    self._generate_cell_type_dropdown(
                        index={"index": index, "type": f"{layout_name}-cell-types-dropdown"},
                        value=cell_types,
                        multi=True,
                    )
                ),
            ], class_name='mb-3 mt-3'
        )

        # modalities multi-select
        modalities = kwargs.get("modalities", None)
        modalities = string_to_list(modalities)
        if modalities is None:
            modalities = self.default_modality_1d
        modalities_control = dbc.Row(
            [
                dbc.Label("Modalities", width="auto"),
                dbc.Col(
                    dcc.Dropdown(
                        options=[{"label": mod, "value": mod} for mod in self.all_modality_1d],
                        id={"index": index, "type": f"{layout_name}-modalities-dropdown"},
                        value=modalities,
                        multi=True,
                    )
                ),
            ], class_name='mb-3'
        )

        # text input for region
        region = kwargs.get("region", None)
        region_control = dbc.Row(
            [
                dbc.Label("Region", width="auto"),
                dbc.Col(
                    dbc.Input(
                        id={"index": index, "type": f"{layout_name}-region-input"},
                        value=region,
                        type="text",
                    )
                ),
            ], class_name='mb-3'
        )
        # select for track colorby
        kwargs.get("colorby", None)
        colorby_control = dbc.Row(
            [
                dbc.Label("Colorby", width="auto"),
                dbc.Col(
                    dbc.RadioItems(
                        options=[
                            {"label": "Modality", "value": "modality"},
                            {"label": "Cell SubClass", "value": "subclass"},
                        ],
                        value="modality",
                        id={"index": index, "type": f"{layout_name}-colorby-sel"},
                    )
                ),
            ], class_name='mb-3'
        )
        # select for track groupby
        kwargs.get("groupby", None)
        groupby_control = dbc.Row(
            [
                dbc.Label("Groupby", width="auto"),
                dbc.Col(
                    dbc.RadioItems(
                        options=[
                            {"label": "Modality", "value": "modality"},
                            {"label": "Cell Subclass", "value": "subclass"},
                        ],
                        value="modality",
                        id={"index": index, "type": f"{layout_name}-groupby-sel"},
                    )
                ),
            ], class_name='mb-3'
        )
        # final update button
        update_button = dbc.Button(
            "Update",
            id={"index": index, "type": f"{layout_name}-update-btn"},
            outline=True,
            color="primary",
            n_clicks=0,
            class_name='m-3',
        )
        # put all control components into a form
        form = dbc.Form(
            [
                cell_types_control,
                modalities_control,
                region_control,
                colorby_control,
                groupby_control,
                update_button,
            ],
            className="col-12",
        )
        return form

    def _get_two_cell_type_diff_control(self, index, *args, **kwargs):
        layout_name = "two_cell_type_diff"

        viewconf_func = getattr(self, f"{layout_name}_viewconf")
        default_kwargs = {k: v.default for k, v in inspect.signature(viewconf_func).parameters.items()}
        kwargs = {**default_kwargs, **kwargs}

        # cell type 1 single select
        cell_type_1 = kwargs.get("cell_type_1", None)
        cell_type_1_control = dbc.Row(
            [
                dbc.Label("Cell Type 1", width="auto"),
                dbc.Col(
                    self._generate_cell_type_dropdown(
                        index={"index": index, "type": f"{layout_name}-cell-type-1-dropdown"},
                        value=cell_type_1,
                        multi=False,
                    )
                ),
            ], class_name='mb-3 mt-3'
        )

        # cell type 2 single select
        cell_type_2 = kwargs.get("cell_type_2", None)
        cell_type_2_control = dbc.Row(
            [
                dbc.Label("Cell Type 2", width="auto"),
                dbc.Col(
                    self._generate_cell_type_dropdown(
                        index={"index": index, "type": f"{layout_name}-cell-type-2-dropdown"},
                        value=cell_type_2,
                        multi=False,
                    )
                ),
            ], class_name='mb-3'
        )

        # modality 2d single select
        modality_2d = kwargs.get("modality_2d", None)
        if modality_2d is None:
            modality_2d = self.default_modality_2d
        modality_2d_control = dbc.Row(
            [
                dbc.Label("Modality", width="auto"),
                dbc.Col(
                    dcc.Dropdown(
                        options=[{"label": mod, "value": mod} for mod in self.all_modality_2d],
                        id={"index": index, "type": f"{layout_name}-modality_2d-dropdown"},
                        value=modality_2d,
                        multi=False,
                    )
                ),
            ], class_name='mb-3'
        )

        # modality 1d multi-select
        modality_1d = kwargs.get("modality_1d", None)
        if modality_1d is None:
            modality_1d = self.default_modality_1d
        modality_1d_control = dbc.Row(
            [
                dbc.Label("Modality", width="auto"),
                dbc.Col(
                    dcc.Dropdown(
                        options=[{"label": mod, "value": mod} for mod in self.all_modality_1d],
                        id={"index": index, "type": f"{layout_name}-modality_1d-dropdown"},
                        value=modality_1d,
                        multi=True,
                    )
                ),
            ], class_name='mb-3'
        )
        # region1 text input
        region1 = kwargs.get("region1", None)
        region1_control = dbc.Row(
            [
                dbc.Label("Region 1", width="auto"),
                dbc.Col(
                    dbc.Input(
                        id={"index": index, "type": f"{layout_name}-region1-input"},
                        value=region1,
                        type="text",
                    )
                ),
            ], class_name='mb-3'
        )
        # region2 text input
        region2 = kwargs.get("region2", None)
        region2_control = dbc.Row(
            [
                dbc.Label("Region 2", width="auto"),
                dbc.Col(
                    dbc.Input(
                        id={"index": index, "type": f"{layout_name}-region2-input"},
                        value=region2,
                        type="text",
                    )
                ),
            ], class_name='mb-3'
        )

        # final update button
        update_button = dbc.Button(
            "Update",
            id={"index": index, "type": f"{layout_name}-update-btn"},
            outline=True,
            color="primary",
            n_clicks=0,
            class_name='m-3',
        )

        # put all control components into a form
        form = dbc.Form(
            [
                cell_type_1_control,
                cell_type_2_control,
                modality_2d_control,
                modality_1d_control,
                region1_control,
                region2_control,
                update_button,
            ],
            className="col-12",
        )
        return form

    def _get_loop_zoom_in_control(self, index, *args, **kwargs):
        layout_name = "loop_zoom_in"

        viewconf_func = getattr(self, f"{layout_name}_viewconf")
        default_kwargs = {k: v.default for k, v in inspect.signature(viewconf_func).parameters.items()}
        kwargs = {**default_kwargs, **kwargs}

        # cell type single select
        cell_type = kwargs.get("cell_type", None)
        cell_type_control = dbc.Row(
            [
                dbc.Label("Cell Type", width="auto"),
                dbc.Col(
                    self._generate_cell_type_dropdown(
                        index={"index": index, "type": f"{layout_name}-cell-type-dropdown"},
                        value=cell_type,
                        multi=False,
                    )
                ),
            ],
            class_name='mb-3 mt-3'
        )

        # modality 2d single select
        modality_2d = kwargs.get("modality_2d", None)
        if modality_2d is None:
            modality_2d = self.default_modality_2d
        modality_2d_control = dbc.Row(
            [
                dbc.Label("Modality", width="auto"),
                dbc.Col(
                    dcc.Dropdown(
                        options=[{"label": mod, "value": mod} for mod in self.all_modality_2d],
                        id={"index": index, "type": f"{layout_name}-modality_2d-dropdown"},
                        value=modality_2d,
                        multi=False,
                    )
                ),
            ],
            class_name='mb-3'
        )

        # modality 1d multi-select
        modality_1d = kwargs.get("modality_1d", None)
        if modality_1d is None:
            modality_1d = self.default_modality_1d
        modality_1d_control = dbc.Row(
            [
                dbc.Label("Modality", width="auto"),
                dbc.Col(
                    dcc.Dropdown(
                        options=[{"label": mod, "value": mod} for mod in self.all_modality_1d],
                        id={"index": index, "type": f"{layout_name}-modality_1d-dropdown"},
                        value=modality_1d,
                        multi=True,
                    )
                ),
            ],
            class_name='mb-3'
        )
        # region1 text input
        region1 = kwargs.get("region1", None)
        region1_control = dbc.Row(
            [
                dbc.Label("Region 1", width="auto"),
                dbc.Col(
                    dbc.Input(
                        id={"index": index, "type": f"{layout_name}-region1-input"},
                        value=region1,
                        type="text",
                    )
                ),
            ],
            class_name='mb-3'
        )
        # region2 text input
        region2 = kwargs.get("region2", None)
        region2_control = dbc.Row(
            [
                dbc.Label("Region 2", width="auto"),
                dbc.Col(
                    dbc.Input(
                        id={"index": index, "type": f"{layout_name}-region2-input"},
                        value=region2,
                        type="text",
                    )
                ),
            ],
            class_name='mb-3'
        )
        # zoom region1 text input
        zoom_region1 = kwargs.get("zoom_region1", None)
        zoom_region1_control = dbc.Row(
            [
                dbc.Label("Zoom Region 1", width="auto"),
                dbc.Col(
                    dbc.Input(
                        id={"index": index, "type": f"{layout_name}-zoom-region1-input"},
                        value=zoom_region1,
                        type="text",
                    )
                ),
            ],
            class_name='mb-3'
        )
        # zoom region2 text input
        zoom_region2 = kwargs.get("zoom_region2", None)
        zoom_region2_control = dbc.Row(
            [
                dbc.Label("Zoom Region 2", width="auto"),
                dbc.Col(
                    dbc.Input(
                        id={"index": index, "type": f"{layout_name}-zoom-region2-input"},
                        value=zoom_region2,
                        type="text",
                    )
                ),
            ],
            class_name='mb-3'
        )

        # final update button
        update_button = dbc.Button(
            "Update",
            id={"index": index, "type": f"{layout_name}-update-btn"},
            outline=True,
            color="primary",
            n_clicks=0,
            class_name='m-3',
        )

        # put all control components into a form
        form = dbc.Form(
            [
                cell_type_control,
                modality_2d_control,
                modality_1d_control,
                region1_control,
                region2_control,
                zoom_region1_control,
                zoom_region2_control,
                update_button,
            ],
            className="col-6",
        )
        return form

    def get_higlass_and_control(self, index, layout, *args, **kwargs):
        iframe = self._get_iframe(index, layout, *args, **kwargs)
        control_form = self._get_layout_control_form(index, layout, *args, **kwargs)

        # add delete button
        delete_button = dbc.Button(
            "Delete",
            id={"index": index, "type": "delete-figure-btn"},
            outline=True,
            color="danger",
            n_clicks=0,
            class_name='m-3',
        )
        control_form.children.append(delete_button)
        return (iframe, control_form)


# TODO write a func to auto detect server in debug or production mode
server = "http://localhost:8989/api/v1"

higlass = HiglassDash(server=server)
