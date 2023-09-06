from .higlass import HiglassBrowser
import dash_bootstrap_components as dbc
from dash import dcc, html


class HiglassDash(HiglassBrowser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        return

    def _get_iframe(self, index, layout, *args, **kwargs):
        html_text, html_height = self.get_higlass_html(layout, *args, **kwargs)
        iframe = html.Iframe(
            srcDoc=html_text,
            style= {"height": f'{html_height}px', "border": "none"},# 
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

        # cell types multi-select
        cell_types_control = dbc.Row(
            [
                dbc.Label("Cell Types", width="auto"),
                dbc.Col(
                    self._generate_cell_type_dropdown(
                        index={"index": index, "type": f"{layout_name}-cell-types-dropdown"},
                        value=kwargs.get("cell_types", []),
                        multi=True,
                    )
                ),
            ]
        )
        # modality 2d single select
        modality_2d_control = dbc.Row(
            [
                dbc.Label("Modality", width="auto"),
                dbc.Col(
                    dcc.Dropdown(
                        options=[{"label": mod, "value": mod} for mod in self.all_modality_2d],
                        id={"index": index, "type": f"{layout_name}-modality-dropdown"},
                        value=kwargs.get("modality", None),
                        multi=False,
                    )
                ),
            ]
        )

        # modality 1d multi-select
        modality_1d_control = dbc.Row(
            [
                dbc.Label("Modality", width="auto"),
                dbc.Col(
                    dcc.Dropdown(
                        options=[{"label": mod, "value": mod} for mod in self.all_modality_1d],
                        id={"index": index, "type": f"{layout_name}-modality-dropdown"},
                        value=kwargs.get("modality", []),
                        multi=True,
                    )
                ),
            ]
        )
        # add genome track boolean switch
        genome_track_control = dbc.Row(
            [
                dbc.Label("Add Genome Track", width="auto"),
                dbc.Col(
                    dbc.Switch(
                        id={"index": index, "type": f"{layout_name}-genome-track-switch"},
                        value=kwargs.get("add_genome_track", True),
                    )
                ),
            ]
        )
        # region1 text input
        region1_control = dbc.Row(
            [
                dbc.Label("Region 1", width="auto"),
                dbc.Col(
                    dbc.Input(
                        id={"index": index, "type": f"{layout_name}-region1-input"},
                        value=kwargs.get("region1", None),
                        type="text",
                    )
                ),
            ]
        )
        # region2 text input
        region2_control = dbc.Row(
            [
                dbc.Label("Region 2", width="auto"),
                dbc.Col(
                    dbc.Input(
                        id={"index": index, "type": f"{layout_name}-region2-input"},
                        value=kwargs.get("region2", None),
                        type="text",
                    )
                ),
            ]
        )

        # put all control components into a form
        form = dbc.Form(
            [
                cell_types_control,
                modality_2d_control,
                modality_1d_control,
                genome_track_control,
                region1_control,
                region2_control,
            ],
            className="col-12",
        )
        return form

    def get_higlass_and_control(self, index, layout, *args, **kwargs):
        iframe = self._get_iframe(index, layout, *args, **kwargs)
        control_form = self._get_layout_control_form(index, layout, *args, **kwargs)
        return (iframe, control_form)


# TODO write a func to auto detect server in debug or production mode
server = "http://localhost:8989/api/v1"

higlass = HiglassDash(server=server)
