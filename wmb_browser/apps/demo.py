import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Create some sample data
df1 = pd.DataFrame({
    'x': [1, 2, 3, 4],
    'y': [4, 3, 2, 1]
})

df2 = pd.DataFrame({
    'x': [1, 2, 3, 4],
    'y': [1, 2, 3, 4]
})

fig1 = px.scatter(df1, x='x', y='y')
fig2 = px.scatter(df2, x='x', y='y')

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='graph-1', figure=fig1),
    dcc.Graph(id='graph-2', figure=fig2)
])

@app.callback(
    Output('graph-2', 'hoverData'),
    [Input('graph-1', 'hoverData')]
)
def update_hover(data):
    return data


if __name__ == "__main__":
    app.run(debug=True, port=1234)
