from dash import Dash, dcc, html, Input, Output, State, MATCH, ALL, Patch, callback

app = Dash(__name__)

app.layout = html.Div(
    [
        html.Div("Dash To-Do list"),
        dcc.Input(id="new-item-input"),
        html.Button("Add", id="add-btn"),
        html.Button("Clear Done", id="clear-done-btn"),
        html.Div(id="list-container-div"),
        html.Div(id="totals-div"),
    ]
)

# Callback to add new item to list
@callback(
    Output("list-container-div", "children", allow_duplicate=True),
    Output("new-item-input", "value"),
    Input("add-btn", "n_clicks"),
    State("new-item-input", "value"),
    prevent_initial_call=True,
)
def add_item(button_clicked, value):
    patched_list = Patch()

    def new_checklist_item(i):
        return html.Div(
            [
                dcc.Checklist(
                    options=[{"label": "", "value": "done"}],
                    id={"index": i, "type": "done"},
                    style={"display": "inline"},
                    labelStyle={"display": "inline"},
                ),
                html.Div(
                    [value],
                    id={"index": i, "type": "output-str"},
                    style={"display": "inline", "margin": "10px"},
                ),
            ]
        )

    patched_list.append(new_checklist_item(button_clicked))
    patched_list.append(new_checklist_item(button_clicked+100))
    return patched_list, ""


# Callback to update item styling
@callback(
    Output({"index": MATCH, "type": "output-str"}, "style"),
    Input({"index": MATCH, "type": "done"}, "value"),
    prevent_initial_call=True,
)
def item_selected(input):
    if not input:
        style = {"display": "inline", "margin": "10px"}
    else:
        style = {
            "display": "inline",
            "margin": "10px",
            "textDecoration": "line-through",
            "color": "#888",
        }
    return style


# Callback to delete items marked as done
@callback(
    Output("list-container-div", "children", allow_duplicate=True),
    Input("clear-done-btn", "n_clicks"),
    State({"index": ALL, "type": "done"}, "value"),
    prevent_initial_call=True,
)
def delete_items(n_clicks, state):
    patched_list = Patch()
    values_to_remove = []
    for i, val in enumerate(state):
        if val:
            values_to_remove.insert(0, i)
    for v in values_to_remove:
        del patched_list[v]
    return patched_list


# Callback to update totals
@callback(
    Output("totals-div", "children"), Input({"index": ALL, "type": "done"}, "value")
)
def show_totals(done):
    count_all = len(done)
    count_done = len([d for d in done if d])
    result = f"{count_done} of {count_all} items completed"
    if count_all:
        result += f" - {int(100 * count_done / count_all)}%"
    return result


if __name__ == "__main__":
    app.run(debug=True, port=1234)
