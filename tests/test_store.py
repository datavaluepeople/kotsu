import pandas as pd
import pytest

from kotsu import store


@pytest.mark.parametrize(
    "to_front_cols",
    [
        [],
        ["result_b", "result_c"],
    ],
)
def test_write(to_front_cols, tmpdir):
    results = [
        {"id": "v1", "result_b": 2, "result_c": 3},
        {"id": "v2", "result_b": 20, "result_c": 30},
    ]
    store.write(results, tmpdir, to_front_cols)

    df = pd.read_csv(tmpdir / "validation_results.csv")
    assert len(df) == 2
    assert len(df.columns) == 3
    assert df.loc[0, "id"] == "v1"
    if to_front_cols:
        assert (df.columns[: len(to_front_cols)] == to_front_cols).all()
