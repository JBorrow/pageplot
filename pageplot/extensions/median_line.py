"""
Basic median line extension.
"""

from pageplot.validators import (
    quantity_list_validator,
    line_display_as_to_function_validator,
)
from pageplot.extensionmodel import PlotExtension
from pageplot.exceptions import PagePlotIncompatbleExtension

from typing import List, Union, Callable, Dict, Any

from matplotlib.pyplot import Figure, Axes


import attr
import unyt
import numpy as np
import math


@attr.s(auto_attribs=True)
class MedianLineExtension(PlotExtension):
    """
    Median line that shows percentile ranges.

    Parameters
    ----------

    limits: List[str]
        The edge limits for the median line calculation. Should be
        given using the usual syntax of e.g. ``["1e0 Msun", "1e10 Msun"]``.

    bins: int, optional
        Number of bins to use in the mass function. Usually we suggest
        using around 0.2 dex wide bins. Default: 10.

    spacing: str, optional
        How to space the bins ("linear" or "log"). Defaults to "linear".

    percentiles: List[float], optional
        Which percentiles to display as the error bounds. Defaults to
        10, 90.

    display_as: str, optional
        How to display the mass function line. There are three options,
        ``default``, using the basic errorbar, ``shaded`` which shows the
        error region as a shaded region, and ``points`` that does
        not include a line at all. See :func:`line_display_as_to_function_validator`
        for more details. Default: ... default.
    """

    limits: List[Union[str, unyt.unyt_quantity, unyt.unyt_array]] = attr.ib(
        default=None, converter=quantity_list_validator
    )
    bins: int = attr.ib(default=10, converter=int)
    spacing: str = attr.ib(
        default=None,
        converter=attr.converters.default_if_none("linear"),
        validator=attr.validators.in_(["linear", "log"]),
    )
    percentiles: List[float] = attr.ib(
        default=[10.0, 90.0], converter=lambda x: [float(a) for a in x]
    )
    display_as: Union[str, Callable] = attr.ib(
        default="default", converter=line_display_as_to_function_validator
    )

    # Internals
    edges: unyt.unyt_array = None
    centers: unyt.unyt_array = None
    values: unyt.unyt_array = None
    errors: unyt.unyt_array = None

    def preprocess(self):
        """
        Pre-processes by creating the binned median line.
        """

        if self.y is None:
            raise PagePlotIncompatbleExtension(
                self.y, "Unable to create a scatter plot without two dimensional data"
            )

        if self.spacing == "linear":
            raw_bin_edges = np.linspace(*self.limits, self.bins)
        else:
            raw_bin_edges = np.logspace(
                *[math.log10(x) for x in self.limits], self.bins
            )

        self.edges = unyt.unyt_array(raw_bin_edges, self.limits[0].units)

        medians = []
        deviations = []
        centers = []

        hist = np.digitize(self.x, self.edges.to(self.x.units))

        for bin in range(1, self.bins):
            indices_in_this_bin = hist == bin
            number_of_items_in_bin = indices_in_this_bin.sum()

            if number_of_items_in_bin >= 1:
                y_values_in_this_bin = self.y[indices_in_this_bin].value

                medians.append(np.median(y_values_in_this_bin))
                deviations.append(np.percentile(y_values_in_this_bin, self.percentiles))

                # Bin center is computed as the median of the X values of the data points
                # in the bin
                centers.append(np.median(self.x[indices_in_this_bin].value))

        self.values = unyt.unyt_array(medians, units=self.y.units, name=self.y.name)
        # Percentiles actually gives us the values - we want to be able to use
        # matplotlib's errorbar function
        self.errors = unyt.unyt_array(
            abs(np.array(deviations).T - self.values.value),
            units=self.y.units,
            name=f"{self.y.name} {self.percentiles} percentiles",
        )

        self.centers = unyt.unyt_array(centers, units=self.x.units, name=self.x.name)

        self.centers.convert_to_units(self.x_units)
        self.errors.convert_to_units(self.y_units)
        self.values.convert_to_units(self.y_units)

    def blit(self, fig: Figure, axes: Axes):
        """
        Displays the median line on the figure.
        """

        self.display_as(axes=axes, x=self.centers, y=self.values, yerr=self.errors)

        return

    def serialize(self) -> Dict[str, Any]:
        return {
            "centers": self.centers,
            "values": self.values,
            "errors": self.errors,
            "edges": self.edges,
            "metadata": {
                "comment": "Errors represent the requested percentile range.",
                "percentiles": self.percentiles,
                "bins": self.bins,
            },
        }
