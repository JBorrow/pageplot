"""
Basic implementation of the HDF5 I/O.
"""

from typing import Optional

from pageplot.exceptions import PagePlotParserError
from .spec import IOSpecification

import h5py
import unyt
import re

import numpy as np

field_search = re.compile(r"(.*?)(\[.*?\])? (.*)")


class IOHDF5(IOSpecification):
    def data_from_string(self, path: Optional[str]) -> Optional[unyt.unyt_array]:
        """
        Gets data from the specified path. h5py does all the
        caching that you could ever need!

        path: Optional[str]
            Path in dataset with units. Example:
            ``/Coordinates/Gas Mpc``

        Notes
        -----

        When passed ``None``, returns ``None``
        """

        if path is None:
            return None

        match = field_search.match(path)

        if match:
            field = match.group(1)

            if match.group(2) is not None:
                exec(f"selector = {match.group(2)}")
            else:
                selector = np.s_[:]

            unit = match.group(3)

            with h5py.File(self.filename, "r") as handle:
                return unyt.unyt_array(handle[field][selector], unit, name=field)

        else:
            raise PagePlotParserError(
                path,
                "Unable to extract path and units. If units are not available, please enter None.",
            )
