"""
Basic extension to scale axes.
"""

from pageplot.extensionmodel import PlotExtension

from matplotlib.pyplot import Figure, Axes

import attr


@attr.s(auto_attribs=True)
class ScaleAxesExtension(PlotExtension):
    """
    Scales the axes, passing through to matplotlib's
    set_xscale and set_yscale.

    Parameters
    ----------

    scale_x: str, optional
        Scale to use for the x-axis. Will accept anything matplotlib will
        accept.

    base_x: str, optional
        The base to use in the case of a "log" axis.

    scale_y: str, optional
        Scale to use for the y-axis. Will accept anything matplotlib will
        accept.

    base_y: str, optional
        The base to use in the case of a "log" axis.
    """

    # Scale in x (e.g. log) and base
    scale_x: str = "linear"
    base_x: float = attr.ib(default=10.0, converter=float)

    # Scale
    scale_y: str = "linear"
    base_y: float = attr.ib(default=10.0, converter=float)

    def blit(self, fig: Figure, axes: Axes):
        if self.scale_x == "log":
            axes.set_xscale("log", base=self.base_x)
        else:
            axes.set_xscale(self.scale_x)

        if self.scale_y == "log":
            axes.set_yscale("log", base=self.base_y)
        else:
            axes.set_yscale(self.scale_y)

        return

    def serialize(self):
        return {
            "scale_x": self.scale_x,
            "base_x": self.base_x,
            "scale_y": self.scale_y,
            "base_y": self.base_y,
        }