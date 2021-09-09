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
from pydantic import validator

import unyt
import numpy as np
import math


class MedianLineExtension(PlotExtension):
    limits: List[Union[str, unyt.unyt_quantity, unyt.unyt_array]]
    bins: int = 10
    spacing: str = "linear"
    percentiles: List[float] = [10.0, 90.0]
    display_as: Union[str, Callable] = "default"

    # Internals
    edges: unyt.unyt_array = None
    centers: unyt.unyt_array = None
    values: unyt.unyt_array = None
    errors: unyt.unyt_array = None

    # Validators
    _convert_limits = validator("limits", allow_reuse=True)(quantity_list_validator)
    _convert_display_as = validator("display_as", always=True, allow_reuse=True)(
        line_display_as_to_function_validator
    )

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

        self.values = unyt.unyt_array(medians, units=self.y.units, name=self.y.name).to(
            self.y_units
        )
        # Percentiles actually gives us the values - we want to be able to use
        # matplotlib's errorbar function
        self.errors = unyt.unyt_array(
            abs(np.array(deviations).T - self.values.value),
            units=self.y.units,
            name=f"{self.y.name} {self.percentiles} percentiles",
        ).to(self.y_units)

        self.centers = unyt.unyt_array(
            centers, units=self.x.units, name=self.x.name
        ).to(self.x_units)

    def blit(self, fig: Figure, axes: Axes):
        """
        Essentially a pass-through for ``axes.scatter``.
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
