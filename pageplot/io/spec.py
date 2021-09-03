"""
IO Structures for PagePlot.

These can be extended by using their pluggy hooks
and iheritence.
"""

import unyt

from pathlib import Path

from pydantic import BaseModel

class IOSpecification(BaseModel):
    filename: Path

    def data_from_string(self, path: str) -> unyt.unyt_array:
        return unyt.unyt_array()

