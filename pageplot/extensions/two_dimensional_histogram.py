"""
Basic histogram plot extension.
"""

from pageplot.validators import quantity_list_validator
from typing import List, Union, Optional
from pageplot.extensionmodel import PlotExtension
from pageplot.exceptions import PagePlotIncompatbleExtension

from matplotlib.pyplot import Figure, Axes
from matplotlib.colors import LogNorm, Normalize

import unyt
import numpy as np
import math

import attr


@attr.s(auto_attribs=True)
class TwoDimensionalHistogramExtension(PlotExtension):
    """
    A two dimensional background histogram for the figure. Note that this rasterises
    the output from matplotlib's pcolormesh function, as generally the non-raster
    versions are not sustainable.

    Parameters
    ----------

    limits_x: List[str]
        The edge limits for the histogram calculation (along x axis). Should be
        given using the usual syntax of e.g. ``["1e0 Msun", "1e10 Msun"]``.

    limits_y: List[str]
        The edge limits for the histogram calculation (along y axis). Should be
        given using the usual syntax of e.g. ``["1e0 Msun", "1e10 Msun"]``.

    bins: int, optional
        The number of bins in each dimension to use (always the same in both
        dimensions)

    spacing_x: str, optional
        Spacing between bins in the x-direction. Can be linear, or log. Defaults
        to linear.

    spacing_y: str, optional
        Spacing between bins in the y-direction. Can be linear, or log. Defaults
        to linear.

    norm: str, optional
        Normalisation to use for the colour map. Can be linear or log. Defaults
        to linear.

    cmap: str, optional
        Override for the choice of colour map used in the stylesheet.

    """

    limits_x: List[Union[unyt.unyt_quantity, unyt.unyt_array]] = attr.ib(
        default=None, converter=quantity_list_validator
    )
    limits_y: List[Union[unyt.unyt_quantity, unyt.unyt_array]] = attr.ib(
        default=None, converter=quantity_list_validator
    )
    bins: int = attr.ib(default=10, converter=int)
    spacing_x: str = attr.ib(
        default="linear", validator=attr.validators.in_(["linear", "log"])
    )
    spacing_y: str = attr.ib(
        default="linear", validator=attr.validators.in_(["linear", "log"])
    )
    norm: str = attr.ib(
        default="linear", validator=attr.validators.in_(["linear", "log"])
    )
    cmap: Optional[str] = None

    # Internals
    x_edges: unyt.unyt_array = attr.ib(init=False)
    y_edges: unyt.unyt_array = attr.ib(init=False)
    grid: unyt.unyt_array = attr.ib(init=False)

    def preprocess(self):
        """
        Pre-process data to enable saving out.
        """

        if self.spacing_x == "linear":
            raw_bin_edges_x = np.linspace(*self.limits_x[:2], self.bins)
        else:
            raw_bin_edges_x = np.logspace(
                *[math.log10(x) for x in self.limits_x[:2]], self.bins
            )

        if self.spacing_y == "linear":
            raw_bin_edges_y = np.linspace(*self.limits_y[:2], self.bins)
        else:
            raw_bin_edges_y = np.logspace(
                *[math.log10(y) for y in self.limits_y[:2]], self.bins
            )

        self.x_edges = unyt.unyt_array(
            raw_bin_edges_x, self.limits_x[0].units, name=self.x.name
        )
        self.y_edges = unyt.unyt_array(
            raw_bin_edges_y, self.limits_y[0].units, name=self.y.name
        )

        H, *_ = np.histogram2d(
            x=self.x,
            y=self.y,
            bins=[self.x_edges.to(self.x.units), self.y_edges.to(self.y.units)],
        )

        self.grid = unyt.unyt_array(H.T, None)

        return

    def blit(self, fig: Figure, axes: Axes):
        """
        Essentially a pass-through for ``axes.scatter``.
        """

        if self.y is None:
            raise PagePlotIncompatbleExtension(
                self.y,
                "Unable to create a hsistogram plot without two dimensional data",
            )

        norm = Normalize() if self.norm == "linear" else LogNorm()

        axes.pcolormesh(
            self.x_edges.to(self.x_units),
            self.y_edges.to(self.y_units),
            self.grid.to(self.z_units),
            norm=norm,
            cmap=self.cmap,
            rasterized=True,
        )

        return

    def serialize(self):
        return {
            "x_edges": self.x_edges,
            "y_edges": self.y_edges,
            "grid": self.grid,
            "norm": self.norm,
            "metadata": {
                "comment": "Edges and grid can be directly plotted with pcolormesh."
            },
        }
