"""Functionality for storing validation results."""
from typing import List
from kotsu.typing import Results

import os.path

import pandas as pd


def write(results_list: List[Results], store_directory: str, to_front_cols: List[str]):
    """Write the results to the store directory."""
    df = pd.DataFrame(results_list)

    df = df[to_front_cols + [col for col in df.columns if col not in to_front_cols]]

    results_file_path = os.path.join(store_directory, "validation_results.csv")
    df.to_csv(results_file_path, index=False)
