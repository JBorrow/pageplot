"""
Plot limits extension that sets the x and y limits,
as well as being used to set the units on those
axes.
"""

from pageplot.exceptions import PagePlotParserError
from pydantic import validator
from pageplot.validators import quantity_list_validator
from pageplot.extensionmodel import PlotExtension
from typing import List, Union


from matplotlib.pyplot import Figure, Axes

import unyt


class AxesLimitsExtension(PlotExtension):
    """
    Sets the axes limits and units that the final
    figure will be displayed in.
    """

    limits_x: List[Union[str, unyt.unyt_quantity, unyt.unyt_array, None]] = [None, None]
    limits_y: List[Union[str, unyt.unyt_quantity, unyt.unyt_array, None]] = [None, None]

    # Validators
    _convert_limits = validator("limits_x", "limits_y", allow_reuse=True)(
        quantity_list_validator
    )

    def blit(self, fig: Figure, axes: Axes):
        try:
            axes.set_xlim(*self.limits_x)
            axes.set_ylim(*self.limits_y)
        except AttributeError:
            raise PagePlotParserError(
                self.limits_x + self.limits_y,
                "Unable to set plot limits. It is likely that the plot is empty "
                + "and an internal matplotlib call is failing. You should set the "
                + "limits at the end of your JSON, and verify that your data is not "
                + "empty.",
            )
