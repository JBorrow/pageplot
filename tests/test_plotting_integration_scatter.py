"""
Integration test that ensures that we are able to run through
from data loading to plot output without crashing.

Creates a basic scatter plot.
"""

from pageplot.plotmodel import PlotModel
from pageplot.config import GlobalConfig
from pageplot.io.h5py import IOHDF5
from pathlib import Path

import h5py
import numpy as np

import os

def test_integration_basic(show_plot=False):
    # First generate some test data
    data_file = Path("test.hdf5")

    with h5py.File(data_file, "w") as handle:
        handle.create_dataset("XDataset", data=np.random.rand(128))
        handle.create_dataset("YDataset", data=np.random.rand(128))

    data = IOHDF5(filename=data_file)

    # Set up various objects
    config = GlobalConfig()
    plot = PlotModel(
        name="test",
        config=config,
        plot_spec={
            "scatter": {}
        },
        x="XDataset Solar_Mass / kpc**2",
        y="YDataset kpc",
    )

    plot.associate_data(data=data)

    plot.setup_figures()

    plot.run_extensions()

    output_path = Path("test.png")

    plot.save(filename=output_path)

    os.remove(data_file)

    if not show_plot:
        os.remove(output_path)