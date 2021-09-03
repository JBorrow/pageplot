"""
Built in extensions.
"""

from pageplot.extensions.scatter import ScatterExtension
from pageplot.extensions.median_line import MedianLineExtension

built_in_extensions = {
    "scatter": ScatterExtension,
    "median_line": MedianLineExtension,
}
