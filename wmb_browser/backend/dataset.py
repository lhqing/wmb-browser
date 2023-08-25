from typing import Union

import pandas as pd
import xarray as xr
import joblib
from .genome import mm10

_RESERVED_KEYS = {"metadata", "coords"}


class Dataset:
    """Dataset class for the WMB Browser backend."""

    def __init__(self, name: str, obs_ids: pd.Index, obs_dim: str) -> None:
        self.name = name
        self.obs_ids = obs_ids
        self.obs_dim = obs_dim

        # create a mapping from the original object ids to the internal ids
        self._obs_ids_int_ids = pd.Index(range(len(obs_ids)))
        self._original_id_to_int_id = {_id: int_id for int_id, _id in enumerate(obs_ids)}
        self._int_id_to_original_id = {v: k for k, v in self._original_id_to_int_id.items()}

        self._var_matrices = {}

        self._metadata = pd.DataFrame(index=self.obs_ids)

        self._coords = {}
        return

    def add_var_matrix(
        self, name: str, var_matrix: xr.DataArray, var_dim: str, load: bool = False, dtype: str = None
    ) -> None:
        """
        Add an obj-by-var 2D matrix to the dataset.

        Parameters
        ----------
        name : name of the feature set
        var_matrix : data array with dimensions (obs_dim, var_dim)
        var_dim : name of the variable dimension
        load : whether to load the data into memory
        dtype : data type to cast the data to

        Returns
        -------
        None
        """
        if name in self._var_matrices:
            raise ValueError(f"Feature set '{name}' already exists.")
        if name in _RESERVED_KEYS:
            raise ValueError(f"Feature set name '{name}' is reserved.")

        if var_matrix.dims != (self.obs_dim, var_dim):
            raise ValueError(f"Dimensions of feature set '{name}' do not match.")

        if dtype is not None and var_matrix.dtype != dtype:
            var_matrix = var_matrix.astype(dtype)

        if load:
            var_matrix.load()

        var_matrix = var_matrix.rename({self.obs_dim: "obs", var_dim: "var"})

        self._var_matrices[name] = var_matrix
        return

    def add_metadata(self, metadata: pd.Series):
        """
        Add a metadata variable to the dataset.

        Parameters
        ----------
        metadata : pd.Series with index containing the object ids

        Returns
        -------
        None
        """
        if metadata.name in self._metadata.columns:
            raise ValueError(f"Category '{metadata.name}' already exists.")

        if metadata.dtype == "category":
            metadata = metadata.astype(str).astype("category")

        self._metadata[metadata.name] = metadata
        return

    def add_metadata_df(self, metadata: pd.DataFrame) -> None:
        """
        Add a metadata dataframe to the dataset.

        Parameters
        ----------
        metadata : pd.DataFrame with index containing the object ids

        Returns
        -------
        None
        """
        for col in metadata.columns:
            if col in self._metadata:
                raise ValueError(f"Metadata column '{col}' already exists.")
        self._metadata = pd.concat([self._metadata, metadata], axis=1)
        return

    def add_coords(self, name: str, coords: pd.DataFrame, dtype="float16"):
        """
        Add coordinates to the dataset.

        Parameters
        ----------
        name : name of the coordinates
        coords : data array with dimensions (obs_dim, coord_dim)
        dtype : data type to cast the data to

        Returns
        -------
        None
        """
        _coords = coords.astype(dtype)

        _coords.columns = [f"{name}_{c}" for c in range(_coords.shape[1])]
        self._coords[name] = _coords
        return

    @property
    def var_sets(self) -> set:
        """Get the names of the feature sets."""
        return set(self._var_matrices.keys())

    @property
    def coords(self) -> set:
        """Get the names of the coordinates."""
        return set(self._coords.keys())

    @property
    def metadata_names(self) -> set:
        """Get the names of the metadata columns."""
        return set(self._metadata.columns)

    def get_var_values(self, set_name: str, var_name: str) -> pd.Series:
        """
        Get a series of values for a given variable in a given feature set.

        Parameters
        ----------
        set_name : the name of the feature set
        var_name : the name of the variable

        Returns
        -------
        pd.Series
        """
        try:
            _da = self._var_matrices[set_name]
        except KeyError:
            raise KeyError(f"Feature set '{set_name}' not found.")
        try:
            _data = _da.sel(var=var_name).to_pandas()
        except KeyError:
            raise KeyError(f"Variable '{var_name}' not found in feature set '{set_name}'.")

        return _data

    def get_coords(self, name: str) -> pd.DataFrame:
        """
        Get the coordinates for a given name.

        Parameters
        ----------
        name : the name of the coordinates

        Returns
        -------
        pd.DataFrame
        """
        try:
            return self._coords[name].copy()
        except KeyError:
            raise KeyError(f"Coordinates '{name}' not found.")

    def get_metadata(self, name: str) -> pd.Series:
        """
        Get the metadata for a given name.

        Parameters
        ----------
        name : the name of the metadata

        Returns
        -------
        pd.Series
        """
        try:
            return self._metadata[name].copy()
        except KeyError:
            raise KeyError(f"Metadata '{name}' not found.")

    def get_plot_data(
        self,
        coord: str,
        metadata: Union[str, list] = None,
        var_dict: dict = None,
        use_obs: pd.Index = None,
        missing_value: str = "drop",
        sample: int = None,
    ) -> pd.DataFrame:
        """
        Get the tidy data for plots.

        Parameters
        ----------
        coord : name of the coordinates
        metadata : name of the metadata columns
        var_dict : dictionary of feature sets and variables
        use_obs : list of object ids to use
        missing_value : how to handle missing values, either 'drop' or 'raise'
        sample : number of objects to sample

        Returns
        -------
        pd.DataFrame
        """
        plot_data = self.get_coords(coord)

        if metadata is not None:
            if isinstance(metadata, str):
                _metadata = self._metadata[metadata]
                plot_data[metadata] = _metadata
            else:
                for m in metadata:
                    _metadata = self._metadata[m]
                    plot_data[m] = _metadata

        if var_dict is not None:
            for name, var in var_dict.items():
                if isinstance(var, str):
                    plot_data[f"{name}:{var}"] = self.get_var_values(name, var)
                else:
                    for _v in var:
                        plot_data[f"{name}:{_v}"] = self.get_var_values(name, _v)

        if use_obs is not None:
            plot_data = plot_data.loc[use_obs].copy()
        if missing_value == "drop":
            plot_data = plot_data.dropna()
        elif missing_value == "raise":
            assert not plot_data.isnull().any().any()
        else:
            raise ValueError(f"Invalid value for missing_value: '{missing_value}'")

        if sample is not None and plot_data.shape[0] > sample:
            plot_data = plot_data.sample(sample, random_state=0)
        return plot_data


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
        for arg in args:
            if isinstance(arg, str):
                if arg in self.metadata_names:
                    metadata = arg
                else:
                    dataset, *var = arg.split(":")
                    if dataset in self.var_sets:
                        var_dict[dataset] = self._to_gene_id(var[0])
        if len(metadata) == 0:
            metadata = None
        if len(var_dict) == 0:
            var_dict = None
        return super().get_plot_data(coord, metadata, var_dict, use_obs, missing_value, sample)


cemba = CEMBAsnmCCells()
