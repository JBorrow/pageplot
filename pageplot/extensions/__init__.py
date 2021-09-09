"""
Built in extensions.
"""

from pageplot.extensions.scatter import ScatterExtension
from pageplot.extensions.median_line import MedianLineExtension
from pageplot.extensions.two_dimensional_histogram import (
    TwoDimensionalHistogramExtension,
)
from pageplot.extensions.mass_function import MassFunctionExtension
from pageplot.extensions.scale_axes import ScaleAxesExtension
from pageplot.extensions.axes_limits import AxesLimitsExtension

built_in_extensions = {
    "scatter": ScatterExtension,
    "two_dimensional_histogram": TwoDimensionalHistogramExtension,
    # Ensure that 'background' items are performed before 'foreground'
    # items to avoid zorder clashes.
    "mass_function": MassFunctionExtension,
    "median_line": MedianLineExtension,
    # Finally, put 'global' extensions, like the ones that
    # change plot limits and so on.
    "scale_axes": ScaleAxesExtension,
    "axes_limits": AxesLimitsExtension,
}
