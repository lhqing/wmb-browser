from typing import Tuple, Union

import dash_bootstrap_components as dbc
import joblib
import pandas as pd
import xarray as xr
from dash import dcc, html
from plotly import express as px

from .colors import color_collection
from .dataset import Dataset
from .genome import mm10
from .utilities import *

CELL_META_CLIP_INFO = """
**Cell ID**: {CellID} ({Technology})

**Brain Sample**:
- **Anatomy**: {MajorRegion} | {SubRegion} | {DissectionRegion}
- **Slice & Dissection ID**: Slice {Slice} | {CEMBARegion} | {Sample}
- **CCF**: {CCF_broad} | {CCF_acronym}

**Cell Annotation**:
- **Cell Class**: {CellClass}
- **Cell SubClass**: {CellSubClass}
- **Cell Group**: {CellGroup}
"""


def _get_x_y_lim(df, coord, delta=0, sync=True):
    xmin, xmax = df[f"{coord}_0"].quantile([delta, 1 - delta]).values
    ymin, ymax = df[f"{coord}_1"].quantile([delta, 1 - delta]).values
    if sync:
        xmin = min(xmin, ymin)
        xmax = max(xmax, ymax)
        ymin = xmin
        ymax = xmax
    return xmin, xmax, ymin, ymax


class CEMBAsnmCCells(Dataset):
    def __init__(self) -> None:
        name = "cemba_snmc_cells"
        obs_dim = "cell"
        metadata_path = "/browser/metadata/CEMBA_snmC.cell_metadata.pickle"
        coords_path = "/browser/metadata/CEMBA_snmC.cell_coords.lib"
        cell_by_gene_mc_frac_zarr_path = "/cemba/wmb/GeneChunks/CEMBA.snmC/"
        cell_group_by_gene_rna_zarr_path = "/browser/matrix/CEMBA.snmC.L4Region.AIBS_TENX.log1pCPM.zarr"

        cell_meta = pd.read_pickle(metadata_path)

        super().__init__(name=name, obs_ids=cell_meta.index, obs_dim=obs_dim)

        # add metadata
        self.add_metadata_df(cell_meta)

        # add coords
        coords = joblib.load(coords_path)
        for name, coord_df in coords.items():
            self.add_coords(name, coord_df)

        # add cell-by-gene matrices
        ds = xr.open_zarr(cell_by_gene_mc_frac_zarr_path)
        ds = ds.rename({"geneslop2k-vm23": "gene"})
        gene_mch_frac_da = ds["geneslop2k-vm23_da_frac_fc"].sel(mc_type="CHN")
        gene_mcg_frac_da = ds["geneslop2k-vm23_da_frac_fc"].sel(mc_type="CGN")
        self.add_var_matrix("gene_mch", gene_mch_frac_da, var_dim="gene")
        self.add_var_matrix("gene_mcg", gene_mcg_frac_da, var_dim="gene")

        # add cell-group-by-gene matrices
        ds = xr.open_zarr(cell_group_by_gene_rna_zarr_path)
        rna_da = ds["rna_da"]
        self.add_var_matrix("gene_rna", rna_da, var_dim="gene", obs_dim="CellGroup")

        # plot default
        self._graph_style = {"height": "70vh", "width": "auto"}
        self._default_graph_config = {
            "scrollZoom": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": ["select", "select2d", "autoScale"],
            "toImageButtonOptions": {
                "format": "png",  # one of png, svg, jpeg, webp
                "filename": "custom_image",
                "scale": 4,  # Multiply title/legend/axis/canvas sizes by this factor
            },
        }

    def get_cell_metadata_markdown(self, cell_int_id):
        cell_id = self._int_id_to_original_id[cell_int_id]
        use_meta_names = [
            "CEMBARegion",
            "CellClass",
            "CellSubClass",
            "CellGroup",
            "MajorRegion",
            "SubRegion",
            "DissectionRegion",
            "Slice",
            "Sample",
            "Technology",
            "CCF_broad",
            "CCF_acronym",
        ]
        meta_dict = {k: self.get_metadata(k).loc[cell_id] for k in use_meta_names}
        meta_dict["CellID"] = cell_id

        card = dbc.Card(
            [
                dbc.CardHeader(meta_dict["CellSubClass"]),
                dbc.CardBody([dcc.Markdown(CELL_META_CLIP_INFO.format(**meta_dict), className="small m-0")]),
            ],
            className="mt-3",
        )
        return card

    @staticmethod
    def _to_gene_id(name):
        if name.startswith("ENSMUSG"):
            return name
        else:
            return mm10.gene_name_to_id(name)

    @staticmethod
    def _to_gene_name(gene_id):
        if gene_id.startswith("ENSMUSG"):
            return mm10.gene_id_to_name(gene_id)
        else:
            return gene_id

    def get_gene_mch_frac(self, gene: str) -> pd.Series:
        """Get the mCH fraction for a given gene."""
        gene = self._to_gene_id(gene)
        return self.get_var_values("gene_mch", gene)

    def get_gene_mcg_frac(self, gene: str) -> pd.Series:
        """Get the mCG fraction for a given gene."""
        gene = self._to_gene_id(gene)
        return self.get_var_values("gene_mcg", gene)

    def get_plot_data(
        self, coord: str, *args, use_obs: pd.Index = None, missing_value: str = "drop", sample: int = None
    ) -> pd.DataFrame:
        metadata = []
        var_dict = {}

        rename_dict = {}
        for arg in args:
            if isinstance(arg, str):
                if arg in self.metadata_names:
                    metadata = arg
                else:
                    dataset, *var = arg.split(":")
                    if dataset in self.var_sets:
                        gene_id = self._to_gene_id(var[0])
                        var_dict[dataset] = gene_id
                        rename_dict[f"{dataset}:{gene_id}"] = arg

        if len(metadata) == 0:
            metadata = None
        if len(var_dict) == 0:
            var_dict = None

        _df = super().get_plot_data(coord, metadata, var_dict, use_obs, missing_value, sample)
        _df = _df.rename(columns=rename_dict)
        return _df

    @staticmethod
    def _common_fig_layout(fig):
        fig.update_layout(
            xaxis_title="",
            yaxis_title="",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="white",
            paper_bgcolor="white",
            dragmode="pan",
        )

    def continuous_scatter_figure(self, coord, color, color_range, marker_size="auto", sample=50000):
        plot_data = self.get_plot_data(coord, color, sample=sample)

        fig = px.scatter(
            plot_data,
            x=f"{coord}_0",
            y=f"{coord}_1",
            color=color,
            custom_data=[plot_data.index.astype("uint32")],
            hover_data=None,
            color_continuous_scale="viridis",
            range_color=color_range,
        )

        if marker_size == "auto":
            _scale = 1.5 if "merfish" in coord else 3
            marker_size = auto_size(plot_data.shape[0], scale=_scale)
        else:
            marker_size = float(marker_size)

        fig.update_traces(marker=dict(size=marker_size), hovertemplate=f"{color}=%{{marker.color:.2f}}<extra></extra>")
        if "merfish" in coord:
            xmin, xmax, ymin, ymax = _get_x_y_lim(plot_data, coord)
        else:
            xmin, xmax, ymin, ymax = _get_x_y_lim(plot_data, coord, delta=0)
        fig.update_layout(
            coloraxis_colorbar=dict(thickness=10, len=0.2, y=0.5, title=None),
            xaxis=dict(range=[xmin, xmax]),
            yaxis=dict(range=[ymin, ymax]),
        ),
        self._common_fig_layout(fig)

        return fig

    @staticmethod
    def _get_color_range_by_color(color, color_range, max_color_range):
        if color_range == "auto":
            if color.startswith("gene_mch"):
                color_range = (0.7, 1.5)
                max_color_range = (0, 4.5)
            elif color.startswith("gene_mcg"):
                color_range = (0.5, 0.9)
                max_color_range = (0, 4.5)
            elif color.startswith("gene_rna"):
                color_range = (1.5, 6)
                max_color_range = (0, 12)
            else:
                color_range = (1, 3)
                max_color_range = (0, 12)
        else:
            if max_color_range == "auto":
                vmin, vmax = color_range
                max_color_range = (vmin / 3, vmax * 3)
        return color_range, max_color_range

    def continuous_scatter(
        self,
        index: Union[str, int],
        coord: str,
        color: str,
        sample: int = 50000,
        color_range="auto",
        max_color_range="auto",
    ) -> Tuple[dcc.Graph, dbc.Form]:
        """
        Making a scatter plot color by an continuous variable with pre-computed coordinates.

        Parameters
        ----------
        index
            The internal React component index of the graph. This is created automatically by the callback function, not needed to be specified by the user.
        coord
            The name of the coordinates to be used for the scatter plot.
        color
            The name of the continuous variable to be used for coloring the scatter plot.
        sample
            The number of cells to be sampled for plotting. If set to None, all cells will be used.
        color_range
            The range of the color bar.
        max_color_range
            The min and max range of the color control slider.

        Returns
        -------
        dcc.Graph
            The scatter plot graph.
        dbc.Form
            The control panel for the scatter plot.
        """
        sample = int(sample)

        color_range, max_color_range = self._get_color_range_by_color(color, color_range, max_color_range)

        fig = self.continuous_scatter_figure(coord, color, color_range, sample=sample)

        graph = dcc.Graph(
            id={"index": index, "type": "continuous_scatter-graph"},
            figure=fig,
            style=self._graph_style,
            config=self._default_graph_config,
        )

        graph_control = self._scatter_control(
            index,
            "continuous_scatter",
            coord=coord,
            color=color,
            sample=sample,
            color_range=color_range,
            max_color_range=max_color_range,
        )
        return graph, graph_control

    def categorical_scatter_figure(self, coord, color, marker_size="auto", sample=50000):
        plot_data = self.get_plot_data(coord, color, sample=sample)

        plot_data[color] = plot_data[color].astype(str)
        palette = color_collection.get_colors(color)

        fig = px.scatter(
            plot_data,
            x=f"{coord}_0",
            y=f"{coord}_1",
            color=color,
            hover_data=None,
            custom_data=[plot_data.index.astype("uint32")],
            color_discrete_map=palette,
        )

        if marker_size == "auto":
            _scale = 1.5 if "merfish" in coord else 3
            marker_size = auto_size(plot_data.shape[0], scale=_scale)
        else:
            marker_size = float(marker_size)

        if "merfish" in coord:
            xmin, xmax, ymin, ymax = _get_x_y_lim(plot_data, coord)
        else:
            xmin, xmax, ymin, ymax = _get_x_y_lim(plot_data, coord, delta=0)

        fig.update_traces(
            marker=dict(size=marker_size),
            showlegend=False,
            # hovertemplate=f'{color}=%{{marker.color:.2f}}<extra></extra>'
        )
        fig.update_layout(
            xaxis=dict(range=[xmin, xmax]),
            yaxis=dict(range=[ymin, ymax]),
        )
        self._common_fig_layout(fig)
        return fig

    def categorical_scatter(
        self, index: Union[int, str], coord: str, color: str, sample: int = 50000
    ) -> Tuple[dcc.Graph, dbc.Form]:
        """
        Making a scatter plot color by an categorical variable with pre-computed coordinates.

        Parameters
        ----------
        index
            The internal React component index of the graph. This is created automatically by the callback function, not needed to be specified by the user.
        coord
            The name of the coordinates to be used for the scatter plot.
        color
            The name of the categorical variable to be used for coloring the scatter plot.
        sample
            The number of cells to be sampled for plotting. If set to None, all cells will be used.

        Returns
        -------
        dcc.Graph
            The scatter plot graph.
        dbc.Form
            The control panel for the scatter plot.
        """
        sample = int(sample)

        fig = self.categorical_scatter_figure(coord, color, sample=sample)

        graph = dcc.Graph(
            id={"index": index, "type": "categorical_scatter-graph"},
            figure=fig,
            style=self._graph_style,
            config=self._default_graph_config,
        )

        graph_control = self._scatter_control(
            index,
            "categorical_scatter",
            coord=coord,
            color=color,
            sample=sample,
        )
        return graph, graph_control

    def _scatter_control(
        self,
        index,
        scatter_type,
        coord,
        color,
        sample,
        color_range=None,
        max_color_range=None,
    ):
        # color control
        color_control = dbc.Row(
            [
                dbc.Label("Color by", width="auto"),
                dbc.Col(
                    dbc.Input(
                        id={"index": index, "type": "color_input"},
                        type="text",
                        value=color,
                        placeholder="Enter color variable",
                    ),
                    className="me-3",
                ),
            ],
            className="g-2 mb-3 mt-3",
        )
        # color range for continuous scatter
        if scatter_type.startswith("continuous"):
            if color_range is None:
                raise ValueError("color_range must be provided for continuous scatter")

            if max_color_range is not None:
                cmin, cmax = max_color_range
            else:
                cmin, cmax = (min(0, color_range[0]), max(3, color_range[1]))

            range_slider = dbc.Row(
                [
                    dbc.Label("Color Range", width="auto"),
                    dbc.Col(
                        dcc.RangeSlider(
                            id={"index": index, "type": "color_range"}, min=cmin, max=cmax, value=color_range
                        ),
                        className="me-3",
                    ),
                ],
                className="g-2 mb-3",
            )
            color_control = html.Div([color_control, range_slider], className="mb-3")

        # coord control
        coord_control = dbc.Row(
            [
                dbc.Label("Scatter coordinates", width="auto"),
                dbc.Col(
                    dcc.Dropdown(
                        id={"index": index, "type": "coord_input"},
                        options=[{"label": c, "value": c} for c in sorted(self.coords)],
                        value=coord,
                    ),
                    className="me-3",
                ),
            ],
            className="g-2 mb-3",
        )

        # sample control
        sample_control = dbc.Row(
            [
                dbc.Label("Downsample to", width="auto"),
                dbc.Col(
                    dbc.Input(
                        type="number",
                        min=0,
                        max=self.total_obs,
                        step=5000,
                        value=sample,
                        id={"index": index, "type": "sample_input"},
                    ),
                    className="me-3",
                ),
            ],
            className="g-2 mb-3",
        )

        # final update button
        if scatter_type.startswith("continuous"):
            btn_type = "continuous_scatter_update-btn"
        else:
            btn_type = "categorical_scatter_update-btn"
        update_button = dbc.Button(
            "Update",
            id={"index": index, "type": btn_type},
            outline=True,
            color="primary",
            n_clicks=0,
        )

        # delete figure button
        delete_button = dbc.Button(
            "Delete",
            id={"index": index, "type": "delete-figure-btn"},
            outline=True,
            color="danger",
            n_clicks=0,
            class_name="m-3",
        )

        form = dbc.Form([color_control, coord_control, sample_control, update_button, delete_button])
        return form


cemba_cell = CEMBAsnmCCells()
