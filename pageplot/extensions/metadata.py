"""
Metadata (basically takes in stuff from the json and puts it out
in the final files).
"""

from typing import Optional, Union

from matplotlib.pyplot import Figure, Axes
from pageplot.extensionmodel import PlotExtension

import attr

@attr.s(auto_attribs=True)
class MetadataExtension(PlotExtension):
    comment: Optional[str] = attr.ib(default=None, converter=attr.converters.default_if_none(""))
    title: Optional[str] = attr.ib(default=None, converter=attr.converters.default_if_none(""))
    caption: Optional[str] = attr.ib(default=None, converter=attr.converters.default_if_none(""))
    section: Optional[str] = attr.ib(default=None, converter=attr.converters.default_if_none(""))

    def serialize(self):
        return {
            "comment": self.comment,
            "title": self.title,
            "caption": self.caption,
            "section": self.section,
        }