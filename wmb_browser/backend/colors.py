"""Centralized color definitions for the application."""
import joblib

_palette_alias = {
    "cellsubclass": "subclass",
    "dissection_region": "cemba_dissection_region",
    "dissectionregion": "cemba_dissection_region",
}


class Color:
    """Color definitions for the application."""

    def __init__(self):
        """Initialize the color definitions."""
        self._alias = {k.lower(): v for k, v in _palette_alias.items()}
        color_file_path = "/browser/metadata/TotalPaletteDict.lib"
        self._color_dict = joblib.load(color_file_path)
        return

    @property
    def palette_names(self):
        """Get the names of the palettes."""
        return list(self._color_dict.keys())

    def get_colors(self, name: str) -> dict:
        """Get the color for a given name."""
        name = name.lower()
        name = _palette_alias.get(name, name)
        try:
            return self._color_dict[name]
        except KeyError:
            raise KeyError(f"Color for '{name}' not found. Use these names: {self.palette_names}")


color_collection = Color()
