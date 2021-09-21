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
    section: Optional[str] = None

    def serialize(self):
        return {
            "comment": self.comment if self.comment is not None else "",
            "title": self.title if self.comment is not None else "",
            "caption": self.caption if self.caption is not None else "",
            "section": self.section if self.section is not None else "",
        }