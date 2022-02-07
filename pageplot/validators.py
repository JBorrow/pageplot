"""
Helpful validators for use throughout extensions.
"""

from typing import Callable, List, Union

import matplotlib.pyplot as plt
import unyt

from pageplot.exceptions import PagePlotParserError


def quantity_list_validator(
    item: List[Union[unyt.unyt_quantity, unyt.unyt_array, str]]
) -> List[unyt.unyt_quantity]:
    """
    Converts a list of either strings (as ``FloatValue UnitX / UnitY``) or unyt quantities
    and arrays to a list of unyt quantities.

    Parameters
    ----------

    item: List[Union[unyt.unyt_quantity, unyt.unyt_array, str]]
        List of values to conver to ``unyt.unyt_quantity``.


    Returns
    -------

    output: List[unyt.unyt_quantity]
        Validated list of unyt quantities.


    Notes
    -----

    Helpful for converting from the easy:

    ..code-block json

        "limits": ["7.0 Mpc / Solar Mass", "10.0 Mpc / Solar Mass"]

    to the appropriate unyt quantities for use in the code.
    """

    output = []

    for x in item:
        if isinstance(x, str):
            value, unit = x.split(" ", 1)
            output.append(unyt.unyt_quantity(float(value), unit))
        else:
            output.append(x)

    return output


def line_display_as_to_function_validator(item: str) -> Callable:
    """
    Validates available "display_as" items, for binned lines, converting
    them to:

    - "default" - uses a basic passthrough call to ``ax.errorbar``
    - "shaded" - uses a shaded background region with ``ax.fill_between``
    - "points" - uses errorbar points with marker ``.``.
    """

    if item == "default":

        def errorbar_basic(
            axes: plt.Axes,
            x: unyt.unyt_array,
            y: unyt.unyt_array,
            yerr: unyt.unyt_array,
            **kwargs
        ):
            """
            Basic pass-through to errorbar.
            """

            axes.errorbar(x=x, y=y, yerr=yerr, **kwargs)

        return errorbar_basic

    elif item == "shaded":

        def errorbar_shaded(
            axes: plt.Axes,
            x: unyt.unyt_array,
            y: unyt.unyt_array,
            yerr: unyt.unyt_array,
            alpha: float = 0.3,
            **kwargs
        ):
            """
            Shaded errorbar. Kwargs go to fill_between. Alpha gives the alpha of the errorbar.
            """

            (line,) = axes.plot(x, y)

            if yerr.ndim > 1:
                yerr_low = y - yerr[0]
                yerr_high = y + yerr[1]
            else:
                yerr_low = y - yerr
                yerr_high = y + yerr

            # Reset names for automagical plotting
            yerr_low.name = y.name
            yerr_high.name = y.name

            shaded = axes.fill_between(
                x=x,
                y1=yerr_low,
                y2=yerr_high,
                alpha=alpha,
                color=line.get_color(),
                linewidth=0.0,
                **kwargs,
            )

        return errorbar_shaded

    elif item == "points":

        def errorbar_points(
            axes: plt.Axes,
            x: unyt.unyt_array,
            y: unyt.unyt_array,
            yerr: unyt.unyt_array,
            **kwargs
        ):
            """
            Errorbar but showing with points instead of a line.
            """

            axes.errorbar(
                x=x,
                y=y,
                yerr=yerr,
                fmt=".",
                linestyle="none",
                **kwargs,
            )

        return errorbar_points

    else:
        raise PagePlotParserError(
            item,
            "Unable to find matching line display. Valid styles are: points, shaded, default.",
        )
