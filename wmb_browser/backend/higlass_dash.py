from .higlass import HiglassBrowser
from dash_html_components import IFrame
import dash_bootstrap_components as dbc


class HiglassDash(HiglassBrowser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        return

    def _get_iframe(self, index, layout, *args, **kwargs):
        html = self.get_higlass_html(layout, *args, **kwargs)
        iframe = IFrame(
            srcDoc=html,
            style={"width": "100%", "height": "100%", "border": "none"},
            id={"index": index, "type": f"higlass-{layout}-iframe"},
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

    def get_higlass_and_control(self, index, layout, *args, **kwargs):
        iframe = self._get_iframe(index, layout, *args, **kwargs)
        control_form = self._get_layout_control_form(index, layout, *args, **kwargs)
        return (iframe, control_form)
