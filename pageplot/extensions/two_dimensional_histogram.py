"""
Basic histogram plot extension.
"""

from pydantic import validator
from pageplot.validators import quantity_list_validator
from typing import List, Union, Optional
from pageplot.extensionmodel import PlotExtension
from pageplot.exceptions import PagePlotIncompatbleExtension

from matplotlib.pyplot import Figure, Axes
from matplotlib.colors import LogNorm, Normalize

import unyt
import numpy as np


class TwoDimensionalHistogramExtension(PlotExtension):
    """
    A two dimensional background histogram for the figure. Note that this rasterises
    the output from matplotlib's pcolormesh function, as generally the non-raster
    versions are not sustainable.
    """

    limits_x: List[Union[str, unyt.unyt_quantity, unyt.unyt_array]]
    limits_y: List[Union[str, unyt.unyt_quantity, unyt.unyt_array]]
    bins: int = 10
    spacing_x: str = "linear"
    spacing_y: str = "linear"
    norm: str = "linear"
    cmap: Optional[str] = None

    # Internals
    x_edges: unyt.unyt_array = None
    y_edges: unyt.unyt_array = None
    grid: unyt.unyt_array = None

    # Validators
    _convert_limits_x = validator("limits_x", allow_reuse=True)(quantity_list_validator)
    _convert_limits_y = validator("limits_y", allow_reuse=True)(quantity_list_validator)

    def preprocess(self):
        """
        Pre-process data to enable saving out.
        """

        if self.spacing_x == "linear":
            raw_bin_edges_x = np.linspace(*self.limits_x, self.bins)
        else:
            raw_bin_edges_x = np.logspace(*self.limits_x, self.bins)

        if self.spacing_y == "linear":
            raw_bin_edges_y = np.linspace(*self.limits_y, self.bins)
        else:
            raw_bin_edges_y = np.logspace(*self.limits_y, self.bins)

        self.x_edges = unyt.unyt_array(raw_bin_edges_x, self.limits_x[0].units, self.x.name)
        self.y_edges = unyt.unyt_array(raw_bin_edges_y, self.limits_y[1].units, self.y.name)

        H, *_ = np.histogram2d(
            x=self.x,
            y=self.y,
            bins=[self.x_edges.to(self.x.units), self.y_edges.to(self.y.units)],
        )

        self.grid = unyt.unyt_array(H, None)

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
            self.x_edges,
            self.y_edges,
            self.grid,
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
            "metadata": {
                "comment": "Edges and grid can be directly plotted with pcolormesh."
            },
        }