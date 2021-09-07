"""
IO Structures for PagePlot.

These can be extended by using their pluggy hooks
and iheritence.
"""

from typing import Optional, Type
import unyt

from pathlib import Path

from pydantic import BaseModel, validator


class MetadataSpecification(BaseModel):
    """
    Specification for adding additional metadata to the I/O specification.
    """

    filename: Path

    # Suggested Additions:
    # - For Cosmology
    #   + box_volume, the volume of the box used (for mass functions)
    #   + a, the current scale factor (if appropriate)
    #   + z, the current redshift (if appropriate)


class IOSpecification(BaseModel):
    """
    Base required specification for I/O extensions.
    """

    filename: Path

    # Specification assocaited with this IOSpecification
    _metadata_specification: Type = MetadataSpecification
    # Storage object that is lazy-loaded
    _metadata: MetadataSpecification = None

    @property
    def metadata(self):
        if self._metadata is None:
            # This must be done this way because private variables are
            # class variables in pydantic.
            # https://github.com/samuelcolvin/pydantic/issues/655
            object.__setattr__(
                self, "_metadata", self._metadata_specification(filename=self.filename)
            )

        return self._metadata

    def data_from_string(self, path: Optional[str]) -> Optional[unyt.unyt_array]:
        """
        Return a ``unyt`` array containing data assocaited with the
        given input string. If passed ``None``, this function must return
        ``None``.
        """
        return unyt.unyt_array()
