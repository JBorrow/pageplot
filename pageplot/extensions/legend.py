"""
Styling of the legend. Overwrites stylesheet behaviours.
"""

from typing import Optional, Union

import attr
from matplotlib.pyplot import Axes, Figure

from pageplot.extensionmodel import PlotExtension


@attr.s(auto_attribs=True)
class LegendExtension(PlotExtension):
    """
    Adds a legend to the plot, with basic styling
    options.
    """

    on: bool = True
    frame_on: Optional[bool] = None
    loc: Union[str, int] = "best"

    def blit(self, fig: Figure, axes: Axes):
        if self.on:
            axes.legend(
                frameon=self.frame_on,
                loc=self.loc,
            )
