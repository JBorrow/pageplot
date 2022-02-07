"""
Basic scatter plot extension.
"""

import attr
from matplotlib.pyplot import Axes, Figure

from pageplot.exceptions import PagePlotIncompatbleExtension
from pageplot.extensionmodel import PlotExtension


@attr.s(auto_attribs=True)
class ScatterExtension(PlotExtension):
    """
    Include this if you would like the background to be
    a scatter plot. Note that this data is not serialized as
    it is of unpredictable size.
    """

    def blit(self, fig: Figure, axes: Axes):
        """
        Essentially a pass-through for ``axes.scatter``.
        """

        if self.y is None:
            raise PagePlotIncompatbleExtension(
                self.y, "Unable to create a scatter plot without two dimensional data"
            )

        axes.scatter(self.x.to(self.x_units), self.y.to(self.y_units))

        return
