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
    """
    Basic pass-through metadata. Used to show data on
    the webpages.

    Parameters
    ----------

    comment: str, optional
        Internal comment to save out to serialized data. Not shown anywhere.

    title: str, optional
        Title to give the plot on the webpage. This isn't baked into the png.

    caption: str, optional
        Caption for the figure, again for the webpage. Not shown on the figure.

    section: str, optional
        The section to display this figure in on the webpage.
    """
    comment: Optional[str] = attr.ib(
        default=None, converter=attr.converters.default_if_none("")
    )
    title: Optional[str] = attr.ib(
        default=None, converter=attr.converters.default_if_none("")
    )
    caption: Optional[str] = attr.ib(
        default=None, converter=attr.converters.default_if_none("")
    )
    section: Optional[str] = attr.ib(
        default=None, converter=attr.converters.default_if_none("")
    )

    def serialize(self):
        return {
            "comment": self.comment,
            "title": self.title,
            "caption": self.caption,
            "section": self.section,
        }
