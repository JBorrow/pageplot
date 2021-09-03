"""
Basic implementation of the HDF5 I/O.
"""

from pageplot.exceptions import PagePlotParserError
from .spec import IOSpecification

import h5py
import unyt


class IOHDF5(IOSpecification):
    def data_from_string(self, path: str) -> unyt.unyt_array:
        """
        Gets data from the specified path. h5py does all the
        caching that you could ever need!

        path: str
            Path in dataset with units. Example:
            ``/Coordinates/Gas Mpc``
        """

        try:
            path_name, units = path.split(" ")
        except ValueError:
            raise PagePlotParserError(
                path,
                "Unable to extract path and units. If units are not available, please enter None.",
            )
        with h5py.File(self.filename, "r") as handle:
            return unyt.unyt_array(handle[path_name], units)
