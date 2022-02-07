"""
Basic median line extension.
"""

import math
from typing import Any, Callable, Dict, List, Union

import attr
import numpy as np
import unyt
from matplotlib.pyplot import Axes, Figure

from pageplot.exceptions import PagePlotIncompatbleExtension
from pageplot.extensionmodel import PlotExtension
from pageplot.validators import (
    line_display_as_to_function_validator,
    quantity_list_validator,
)


@attr.s(auto_attribs=True)
class MeanLineExtension(PlotExtension):
    """
    Mean line that shows standard deviation ranges.

    Parameters
    ----------

    limits: List[str]
        The edge limits for the mean line calculation. Should be
        given using the usual syntax of e.g. ``["1e0 Msun", "1e10 Msun"]``.

    bins: int, optional
        Number of bins to use in the line. Usually we suggest
        using around 0.2 dex wide bins. Default: 10.

    spacing: str, optional
        How to space the bins ("linear" or "log"). Defaults to "linear".

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

        means = []
        deviations = []
        centers = []

        hist = np.digitize(self.x, self.edges.to(self.x.units))

        for bin in range(1, self.bins):
            indices_in_this_bin = hist == bin
            number_of_items_in_bin = indices_in_this_bin.sum()

            if number_of_items_in_bin >= 1:
                y_values_in_this_bin = self.y[indices_in_this_bin].value

                means.append(np.mean(y_values_in_this_bin))
                deviations.append(np.std(y_values_in_this_bin))

                # Bin center is computed as the median of the X values of the data points
                # in the bin
                centers.append(np.mean(self.x[indices_in_this_bin].value))

        self.values = unyt.unyt_array(means, units=self.y.units, name=self.y.name)
        self.errors = unyt.unyt_array(
            abs(np.array(deviations) - self.values.value),
            units=self.y.units,
            name=self.y.name,
        )

        self.centers = unyt.unyt_array(centers, units=self.x.units, name=self.x.name)

        self.centers.convert_to_units(self.x_units)
        self.errors.convert_to_units(self.y_units)
        self.values.convert_to_units(self.y_units)

    def blit(self, fig: Figure, axes: Axes):
        """
        Displays the mean line on the figure.
        """

        self.display_as(
            axes=axes, x=self.centers, y=self.values, yerr=self.errors, label="Mean"
        )

        return

    def serialize(self) -> Dict[str, Any]:
        return {
            "centers": self.centers,
            "values": self.values,
            "errors": self.errors,
            "edges": self.edges,
            "metadata": {
                "comment": "Errors represent one standard deviation.",
                "bins": self.bins,
            },
        }
