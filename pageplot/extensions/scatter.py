"""
Basic scatter plot extension.
"""

from pageplot.extensionmodel import PlotExtension
from pageplot.exceptions import PagePlotIncompatbleExtension

from matplotlib.pyplot import Figure, Axes

import attr

@attr.s(auto_attribs=True)
class ScatterExtension(PlotExtension):
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
