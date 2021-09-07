"""
Built in extensions.
"""

from pageplot.extensions.scatter import ScatterExtension
from pageplot.extensions.median_line import MedianLineExtension
from pageplot.extensions.two_dimensional_histogram import (
    TwoDimensionalHistogramExtension,
)

built_in_extensions = {
    "scatter": ScatterExtension,
    "two_dimensional_histogram": TwoDimensionalHistogramExtension,

    # Ensure that 'background' items are performed before 'foreground'
    # items to avoid zorder clashes.
    "median_line": MedianLineExtension,
}
