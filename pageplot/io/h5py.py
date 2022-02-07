"""
Basic implementation of the HDF5 I/O.
"""

import re
from typing import Optional, Type, Union

import attr
import h5py
import numpy as np
import unyt

from pageplot.exceptions import PagePlotParserError

from .spec import IOSpecification, MetadataSpecification

field_search = re.compile(r"(.*?)(\[.*?\])? (.*)")


@attr.s
class MetadataHDF5(MetadataSpecification):
    pass


@attr.s
class IOHDF5(IOSpecification):
    # Specification assocaited with this IOSpecification
    metadata_specification: Type = MetadataHDF5
    # Storage object that is lazy-loaded
    metadata: Optional[MetadataHDF5] = None

    def data_from_string(
        self,
        path: Optional[str],
        mask: Optional[Union[np.array, np.lib.index_tricks.IndexExpression]] = None,
    ) -> Optional[unyt.unyt_array]:
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

        if mask is None:
            mask = np.s_[:]

        match = field_search.match(path)

        if match:
            field = match.group(1)

            if match.group(2) is not None:
                exec(f"selector = {match.group(2)}")
            else:
                selector = np.s_[:]

            unit = match.group(3)

            with h5py.File(self.filename, "r") as handle:
                return unyt.unyt_array(handle[field][selector][mask], unit, name=field)

        else:
            raise PagePlotParserError(
                path,
                "Unable to extract path and units. If units are not available, please enter None.",
            )
