from functools import lru_cache
from typing import Union

import pandas as pd
import xarray as xr


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
        self._var_names = {}

        self._categories = {}

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
        assert name not in self._var_matrices
        assert var_matrix.dims == (self.obs_dim, var_dim)

        if dtype is not None and var_matrix.dtype != dtype:
            var_matrix = var_matrix.astype(dtype)

        if load:
            var_matrix.load()

        self._var_matrices[name] = var_matrix

        return

    def add_category(self, category: pd.Series):
        """
        Add a categorical variable to the dataset.

        Parameters
        ----------
        category : pd.Series with index containing the object ids

        Returns
        -------
        None
        """
        assert category.name not in self._categories

        if category.dtype != "category":
            category = category.astype("category")

        self._categories[category.name] = category

        return

    def add_coords(self, name: str, coords: xr.DataArray, dtype="float16"):
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
        assert name not in self._coords

        assert coords.dims[0] == self.obs_dim
        assert len(coords.dims) == 2

        if coords.dtype != dtype:
            coords = coords.astype(dtype)

        coords = coords.to_pandas()
        coords.columns = [f"{name}_{c}" for c in range(coords.shape[1])]
        self._coords[name] = coords
        return

    @property
    def var_sets(self) -> set:
        """Get the names of the feature sets."""
        return set(self._var_matrices.keys())

    @property
    def categories(self) -> set:
        """Get the names of the categorical variables."""
        return set(self._categories.keys())

    @property
    def coords(self) -> set:
        """Get the names of the coordinates."""
        return set(self._coords.keys())

    @lru_cache(maxsize=128)
    def get_values(self, set_name: str, var_name: str) -> pd.Series:
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
            _data = _da[var_name]
        except KeyError:
            raise KeyError(f"Variable '{var_name}' not found in feature set '{set_name}'.")

        return _data.to_pandas()

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

    def get_category(self, name: str) -> pd.Series:
        """
        Get the category for a given name.

        Parameters
        ----------
        name : the name of the category

        Returns
        -------
        pd.Series
        """
        try:
            return self._categories[name]
        except KeyError:
            raise KeyError(f"Category '{name}' not found.")

    def get_scatter_data(
        self,
        coord: str,
        hue: str,
        size: Union[str, None] = None,
        hue_set_name: Union[str, None] = None,
        size_set_name: Union[str, None] = None,
        use_obs: pd.Index = None,
        missing_value: str = "drop",
    ) -> pd.DataFrame:
        """
        Get the data for scatter plots.

        Parameters
        ----------
        coord : name of the coordinates
        hue : name of the hue variable
        size : name of the size variable
        hue_set_name : name of the feature set containing the hue variable
        size_set_name : name of the feature set containing the size variable
        use_obs : list of object ids to use
        missing_value : how to handle missing values, either 'drop' or 'raise'

        Returns
        -------
        pd.DataFrame
        """
        plot_data = self.get_coords(coord)

        _hue = self.get_category(hue) if hue in self.categories else self.get_values(hue_set_name, hue)
        plot_data["hue"] = _hue

        if size is not None:
            _size = self.get_values(size_set_name, size)
            plot_data["size"] = _size

        if use_obs is not None:
            plot_data = plot_data.loc[use_obs].copy()
        if missing_value == "drop":
            plot_data = plot_data.dropna()
        elif missing_value == "raise":
            assert not plot_data.isnull().any().any()
        else:
            raise ValueError(f"Invalid value for missing_value: '{missing_value}'")
        return plot_data
