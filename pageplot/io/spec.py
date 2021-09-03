"""
IO Structures for PagePlot.

These can be extended by using their pluggy hooks
and iheritence.
"""

from typing import Optional
import unyt

from pathlib import Path

from pydantic import BaseModel


class IOSpecification(BaseModel):
    filename: Path

    def data_from_string(self, path: Optional[str]) -> Optional[unyt.unyt_array]:
        """
        Return a ``unyt`` array containing data assocaited with the
        given input string. If passed ``None``, this function must return
        ``None``.
        """
        return unyt.unyt_array()
