"""
Tests the HDF5 I/O.
"""

import os
from pathlib import Path

import h5py
import numpy as np
import unyt

from pageplot.io.h5py import IOHDF5


def test_io_hdf5():
    # first, create some test data on disk.

    test_file = Path("test.hdf5")

    with h5py.File(test_file, "w") as handle:
        handle.create_dataset("FirstTestDataset", data=np.random.rand(16))
        handle.create_dataset("SecondTestDataset", data=np.random.rand(16))

    io_instance = IOHDF5(filename=test_file)

    read_data = io_instance.calculation_from_string("FirstTestDataset Mpc")

    assert read_data.units == unyt.Mpc

    read_data = io_instance.calculation_from_string(
        r"{FirstTestDataset Mpc} + {SecondTestDataset Mpc}"
    )

    assert read_data.units == unyt.Mpc

    os.remove(test_file)
