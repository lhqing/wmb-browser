from .dataset import Dataset
import pandas as pd
import xarray as xr
import joblib
from .genome import mm10
from plotly import express as px
from .utilities import *
from .colors import color_collection


class CEMBAsnmCCells(Dataset):
    def __init__(self) -> None:
        name = "cemba_snmc_cells"
        obs_dim = "cell"
        metadata_path = "/browser/metadata/CEMBA_snmC.cell_metadata.pickle"
        coords_path = "/browser/metadata/CEMBA_snmC.cell_coords.lib"
        cell_by_gene_mc_frac_zarr_path = "/cemba/wmb/GeneChunks/CEMBA.snmC/"

        cell_meta = pd.read_pickle(metadata_path)

        super().__init__(name=name, obs_ids=cell_meta.index, obs_dim=obs_dim)

        # add metadata
        self.add_metadata_df(cell_meta)

        # add coords
        coords = joblib.load(coords_path)
        for name, coord_df in coords.items():
            self.add_coords(name, coord_df)

        # add gene matrices
        ds = xr.open_zarr(cell_by_gene_mc_frac_zarr_path)
        ds = ds.rename({"geneslop2k-vm23": "gene"})
        gene_mch_frac_da = ds["geneslop2k-vm23_da_frac_fc"].sel(mc_type="CHN")
        gene_mcg_frac_da = ds["geneslop2k-vm23_da_frac_fc"].sel(mc_type="CGN")
        self.add_var_matrix("gene_mch", gene_mch_frac_da, var_dim="gene")
        self.add_var_matrix("gene_mcg", gene_mcg_frac_da, var_dim="gene")

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
        )

    def continuous_scatter(self, coord, color, sample=10000):
        sample = int(sample)
        plot_data = self.get_plot_data(coord, color, sample=sample)

        fig = px.scatter(
            plot_data,
            x=f"{coord}_0",
            y=f"{coord}_1",
            color=color,
            hover_data=None,
            color_continuous_scale="viridis",
            range_color=(0.5, 2),
        )

        fig.update_traces(marker=dict(size=auto_size(plot_data.shape[0])))
        fig.update_layout(coloraxis_colorbar=dict(thickness=10, len=0.2, y=0.5, title=None))
        self._common_fig_layout(fig)

        graph_title = color.replace(":", " ")
        return graph_title, fig

    def categorical_scatter(self, coord, color, sample=10000):
        sample = int(sample)
        plot_data = self.get_plot_data(coord, color, sample=sample)

        plot_data[color] = plot_data[color].astype(str)

        fig = px.scatter(
            plot_data,
            x=f"{coord}_0",
            y=f"{coord}_1",
            color=color,
            hover_data=None,
            color_discrete_map=color_collection.get_colors(color),
        )

        fig.update_traces(marker=dict(size=auto_size(plot_data.shape[0])), showlegend=False)
        self._common_fig_layout(fig)

        graph_title = color
        return graph_title, fig


cemba_cell = CEMBAsnmCCells()
