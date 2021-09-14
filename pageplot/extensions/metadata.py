"""
Metadata (basically takes in stuff from the json and puts it out
in the final files).
"""

from typing import Optional, Union

from matplotlib.pyplot import Figure, Axes
from pageplot.extensionmodel import PlotExtension


class MetadataExtension(PlotExtension):
    comment: Optional[str] = None
    title: Optional[str] = None
    caption: Optional[str] = None

    def serialize(self):
        return {
            "comment": self.comment,
            "title": self.title,
            "caption": self.caption,
        }