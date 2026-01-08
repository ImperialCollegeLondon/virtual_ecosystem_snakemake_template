"""Tests for the VEExperiment class."""

from itertools import product
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pytest

from snakemake_helper import VEExperiment
from snakemake_helper.ve_experiment import _get_outpath_with_wildcards

PARAMS: dict = {
    "b": {"c": {"param": range(2, 4)}},
    "a": {"param": range(2)},
}
"""Parameters to vary between runs.

NB: Deliberately not in alphabetical order, as params should be sorted.
"""


def test_get_outpath_with_wildcards() -> None:
    """Test the _get_outpath_with_wildcards() function."""
    assert Path(
        _get_outpath_with_wildcards("out", ("core.param1", "core.param2"))
    ) == Path("out/core.param1_{core_param1}/core.param2_{core_param2}")


@pytest.fixture
def ve_exp():
    """Return a VEExperiment."""
    return VEExperiment("out", PARAMS)


def test_outpath(ve_exp: VEExperiment) -> None:
    """Test the outpath property."""
    assert Path(ve_exp.outpath) == Path("out/a.param_{a_param}/b.c.param_{b_c_param}")


def test_output(ve_exp: VEExperiment) -> None:
    """Test the output property."""
    assert Path(ve_exp.output) == Path("out/a.param_{a_param}/b.c.param_{b_c_param}")


def test_all_outputs(ve_exp: VEExperiment) -> None:
    """Test the all_outputs property."""
    expected = sorted(
        Path(f"out/a.param_{a}/b.c.param_{b}")
        for a, b in product(PARAMS["a"]["param"], PARAMS["b"]["c"]["param"])
    )
    actual = sorted(map(Path, ve_exp.all_outputs))
    assert expected == actual


@patch("snakemake_helper.ve_experiment.sp")
def test_run(sp_mock: Mock, tmp_path: Path) -> None:
    """Test the run() method launches `ve_run` correctly."""
    ve_exp = VEExperiment(str(tmp_path), PARAMS)
    params: dict[str, dict[str, Any]] = {
        "a": {"param": 1},
        "b": {"c": {"param": 2}},
    }
    outpath = (
        tmp_path
        / f"a.param_{params['a']['param']}"
        / f"b.c.param_{params['b']['c']['param']}"
    )

    input = ("dataset",)
    output = (str(outpath),)
    ve_exp.run(input, output)
    sp_mock.run.assert_called_once_with(
        ["ve_run", "-o", output[0], "-c", "a.param=1", "-c", "b.c.param=2", input[0]],
        check=True,
    )
