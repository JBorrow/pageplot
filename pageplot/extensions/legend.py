"""
Styling of the legend. Overwrites stylesheet behaviours.
"""

from typing import Optional, Union

from matplotlib.pyplot import Figure, Axes
from pageplot.extensionmodel import PlotExtension

import attr


@attr.s(auto_attribs=True)
class LegendExtension(PlotExtension):
    on: bool = True
    frame_on: Optional[bool] = None
    loc: Union[str, int] = "best"

    def blit(self, fig: Figure, axes: Axes):
        if self.on:
            axes.legend(
                frameon=self.frame_on,
                loc=self.loc,
            )
