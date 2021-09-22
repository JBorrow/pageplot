"""
Basic mass function extension.
"""

from pageplot.validators import (
    quantity_list_validator,
    line_display_as_to_function_validator,
)
from pageplot.extensionmodel import PlotExtension
from pageplot.exceptions import (
    PagePlotIncompatbleExtension,
    PagePlotMissingMetadataError,
)

from typing import List, Optional, Union, Callable, Dict, Any

from matplotlib.pyplot import Figure, Axes
from pydantic import validator

# This should be removed in later versions as this dependency is _not_ necessary
# as the code should be moved over to this library anyway.

from velociraptor.tools.mass_functions import (
    create_mass_function,
    create_adaptive_mass_function,
)

import unyt
import numpy as np

import attr


@attr.s(auto_attribs=True)
class MassFunctionExtension(PlotExtension):
    """
    Basic & Adaptive mass functions.

    Note that you cannot choose a linear bin width as bins are
    always logrithmic in mass functions anyway.
    """

    limits: List[Union[str, unyt.unyt_quantity, unyt.unyt_array]] = attr.ib(
        default=[None, None], converter=quantity_list_validator
    )
    bins: int = attr.ib(default=10, converter=int)
    display_as: Union[str, Callable] = attr.ib(
        default="default", converter=line_display_as_to_function_validator
    )
    adaptive: bool = attr.ib(default=False, converter=bool)
    minimum_in_bin: int = attr.ib(default=3, converter=int)
    box_volume: Union[unyt.unyt_quantity, str, None] = None

    # Internals
    edges: unyt.unyt_array = attr.ib(init=False)
    centers: unyt.unyt_array = attr.ib(init=False)
    values: unyt.unyt_array = attr.ib(init=False)
    errors: unyt.unyt_array = attr.ib(init=False)

    def __attrs_post_init__(self):
        if self.box_volume is None:
            try:
                self.box_volume = self.metadata.box_volume
            except AttributeError:
                raise PagePlotMissingMetadataError(
                    self,
                    "Missing box_volume from I/O metadata and as such cannot create "
                    + "mass function. This can additionally be supplied as part of "
                    + "the extension by using the box_volume key with appropriate "
                    + "units, but it is not recommended.",
                )
        else:
            if not isinstance(self.box_volume, unyt.unyt_quantity):
                num, unit = self.box_volume.split(" ", 1)
                self.box_volume = unyt.unyt_quantity(float(num), unit)

    def preprocess(self):
        """
        Pre-processes by creating the mass function line.
        """

        if self.y is not None:
            raise PagePlotIncompatbleExtension(
                self.name,
                "It is not possible to have a 'y' input for mass functions as they "
                + "calculate their own y values (essentially a renormalised histogram). ",
            )

        common = dict(
            masses=self.x,
            lowest_mass=self.limits[0].to(self.x.units),
            highest_mass=self.limits[1].to(self.x.units),
            box_volume=self.box_volume,
            minimum_in_bin=self.minimum_in_bin,
            return_bin_edges=True,
        )

        func = create_adaptive_mass_function if self.adaptive else create_mass_function

        if self.adaptive:
            attrs = {**common, "base_n_bins": self.bins}
        else:
            attrs = {**common, "n_bins": self.bins}

        self.centers, self.values, self.errors, self.edges = func(**attrs)

        self.centers.convert_to_units(self.x_units)
        self.edges.convert_to_units(self.x_units)

        self.values.convert_to_units(self.y_units)
        self.errors.convert_to_units(self.y_units)

        return

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
                "comment": "Errors represent one sigma expected Poissson sampling "
                + "error. Centers are the median mass in the bin.",
                "box_volume": self.box_volume,
                "bins": self.bins,
            },
        }
