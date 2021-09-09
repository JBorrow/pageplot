"""
Basic extension to scale axes.
"""

from pageplot.extensionmodel import PlotExtension

from matplotlib.pyplot import Figure, Axes


class ScaleAxesExtension(PlotExtension):
    """
    Scales the axes, passing through to matplotlib's
    set_xscale and set_yscale.
    """

    # Scale in x (e.g. log) and base
    scale_x: str = "linear"
    base_x: float = 10.0

    # Scale
    scale_y: str = "linear"
    base_y: float = 10.0

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
