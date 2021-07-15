"""Functionality for storing validation results."""
from typing import List

import os.path

import pandas as pd


def write(results_list: List[dict], store_directory: str, to_front_cols: List[str]):
    """Write the results to the store directory."""
    df = pd.DataFrame(results_list)

    cols = list(df)
    for col in reversed(to_front_cols):
        cols.insert(0, cols.pop(cols.index(col)))
    df = df.loc[:, cols]

    results_file_path = os.path.join(store_directory, "validation_results.csv")
    df.to_csv(results_file_path, index=False)
