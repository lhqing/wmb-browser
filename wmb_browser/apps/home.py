import dash_bootstrap_components as dbc
from dash import html

INTRODUCTION_TEXT = (
    "Cytosine DNA methylation is essential in brain development and has been implicated in various neurological"
    " disorders. A comprehensive understanding of DNA methylation diversity across the entire brain in the context of"
    " the brain's 3D spatial organization is essential for building a complete molecular atlas of brain cell types and"
    " understanding their gene regulatory landscapes. To this end, we employed optimized single-nucleus methylome"
    " (snmC-seq3) and multi-omic (snm3C-seq) sequencing technologies to generate 301,626 methylomes and 176,003"
    " chromatin conformation/methylome joint profiles from 117 dissected regions throughout the adult mouse brain. Our"
    " study establishes the first brain-wide, single-cell resolution DNA methylome and 3D multi-omic atlas, providing"
    " an unparalleled resource for comprehending the mouse brain's cellular-spatial and regulatory genome diversity."
)

EXAMPLE_TEXT = "Show me the mCH methylation level of Gad1 gene."

jumbotron = html.Div(
    dbc.Container(
        [
            html.H1("Whole Mouse Brain Cell & Genome Atlas", className="display-4"),
            html.P(
                "Single-cell DNA Methylome and 3D Multi-omic Atlas of  the Adult Mouse Brain",
                className="lead",
            ),
            html.Hr(className="my-2"),
            html.P(
                INTRODUCTION_TEXT,
            ),
            html.Hr(className="my-2"),
            dbc.Row(
                [
                    html.P(
                        dbc.Button(
                            html.A("Launch Button", href="https://mousebrain.salk.edu/dynamic_browser"),
                            color="primary",
                            className="m-2",
                            id="home-launch-btn",
                        ),
                        className="lead",
                    ),
                ]
            ),
        ],
        fluid=True,
        className="py-3",
    ),
    className="p-3 bg-light rounded-3",
)

home_layout = html.Div(
    [
        jumbotron,
    ]
)
