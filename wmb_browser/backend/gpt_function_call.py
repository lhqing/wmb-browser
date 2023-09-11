import json
from typing import Tuple

import openai

FUNCTIONS = [
    {
        "name": "categorical_or_continuous_scatter",
        "description": (
            "Making a scatter plot color by an categorical or continous variable with pre-computed coordinates."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "dataset": {
                    "type": "string",
                    "description": "The name of the dataset to be used for the scatter plot.",
                    "enum": ["cemba", "mr"],
                },
                "coord": {
                    "type": "string",
                    "description": "The name of the coordinates to be used for the scatter plot.",
                    "enum": ["l1_tsne", "l1_umap", "mr_tsne", "mr_umap"],
                },
                "color": {
                    "type": "string",
                    "description": (
                        "The name of the categorical or continuous variable to be used for coloring the scatter plot."
                        " The categorical variable can be a cell annotation, such as CellGroup, CEMBARegion, etc, and"
                        " the continuous variable can be continous metadata, such as mCCCFrac, mCGFrac, etc."
                        " It can also be a measurement type in the form of VALUE_TYPE:GENE_NAME, such as gene_mch:Gad1, gene_mcg:Cux1."
                        " The VALUE_TYPE can be gene_mch, gene_mcg, rna, gene_atac, the GENE_NAME are all the gene names"
                    ),
                },
                "sample": {
                    "type": "integer",
                    "description": (
                        "The number of cells to be sampled for the scatter plot. If set to None, all cells will be"
                        " used."
                    ),
                },
            },
            "required": ["coord", "color"],
        },
    },
]


def parse_user_input(user_input: str) -> Tuple[str, str, dict]:
    """Parse user input and return dataset, plot_type, and kwargs."""
    messages = [{"role": "user", "content": user_input}]
    functions = FUNCTIONS
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=functions,
        function_call="auto",  # auto is default, but we'll be explicit
    )

    response_message = response["choices"][0]["message"]

    # Step 2: check if GPT wanted to call a function
    if response_message.get("function_call"):
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        # function_name = response_message["function_call"]["name"]
        function_args = json.loads(response_message["function_call"]["arguments"])
        dataset = function_args.pop("dataset")
        return dataset, "scatter", function_args
