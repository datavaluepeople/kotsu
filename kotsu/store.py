"""Functionality for storing validation results."""
from typing import List
from kotsu.typing import Results

import pandas as pd


def write(results_list: List[Results], results_path: str, to_front_cols: List[str]):
    """Write the results to the store directory."""
    df = pd.DataFrame(results_list)
    df = df[to_front_cols + [col for col in df.columns if col not in to_front_cols]]
    df.to_csv(results_path, index=False)
