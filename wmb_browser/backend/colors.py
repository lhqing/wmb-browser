"""Centralized color definitions for the application."""
import joblib


class Color:
    """Color definitions for the application."""

    def __init__(self):
        """Initialize the color definitions."""
        color_file_path = '/browser/metadata/TotalPaletteDict.lib'
        self._color_dict = joblib.load(color_file_path)
        return

    @property
    def palette_names(self):
        """Get the names of the palettes."""
        return list(self._color_dict.keys())

    def get_colors(self, name: str) -> dict:
        """Get the color for a given name."""
        try:
            return self._color_dict[name]
        except KeyError:
            raise KeyError(f"Color for '{name}' not found. Use these names: {self.palette_names}")
        return

color = Color()