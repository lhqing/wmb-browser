"""Centralized color definitions for the application."""
import joblib


class Color:
    """Color definitions for the application."""

    def __init__(self, color_file_path):
        self._color_dict = joblib.load(color_file_path)
        return

    def get_colors(self, dataset: str, category: str) -> dict:
        """Get the color for a given dataset and category."""
        try:
            return self._color_dict[f"{dataset}.{category}"]
        except KeyError:
            raise KeyError(f"Color for '{dataset}.{category}' not found.")

    def has_colors(self, dataset, category):
        """Check if a given dataset and category has colors."""
        return f"{dataset}.{category}" in self._color_dict
