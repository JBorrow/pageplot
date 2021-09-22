"""
IO Structures for PagePlot.

These can be extended by using their pluggy hooks
and iheritence.
"""

from typing import Optional, Type, Union
import unyt
import numpy as np

from pathlib import Path

import attr


@attr.s(auto_attribs=True)
class MetadataSpecification:
    """
    Specification for adding additional metadata to the I/O specification.
    """

    filename: Path = attr.ib(converter=Path)

    # Suggested Additions:
    # - For Cosmology
    #   + box_volume, the volume of the box used (for mass functions)
    #   + a, the current scale factor (if appropriate)
    #   + z, the current redshift (if appropriate)


@attr.s(auto_attribs=True)
class IOSpecification:
    """
    Base required specification for I/O extensions.
    """

    filename: Path = attr.ib(converter=Path)

    # Specification assocaited with this IOSpecification
    metadata_specification: Type = MetadataSpecification
    # Storage object that is lazy-loaded
    metadata: MetadataSpecification = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.metadata = self.metadata_specification(filename=self.filename)

    def data_from_string(
        self,
        path: Optional[str],
        mask: Optional[Union[np.array, np.lib.index_tricks.IndexExpression]] = None,
    ) -> Optional[unyt.unyt_array]:
        """
        Return a ``unyt`` array containing data assocaited with the
        given input string. If passed ``None``, this function must return
        ``None``.

        A mask may optionally be provided to select data. This can
        be handled by the individual plugin creators for lazy-loading.
        """
        return unyt.unyt_array()
