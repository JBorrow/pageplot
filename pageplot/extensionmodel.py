"""
Model for extensions that perform plotting and
data production duties.
"""

from attr.setters import convert
from pageplot.config import GlobalConfig
from pageplot.io.spec import MetadataSpecification

from typing import Optional, Dict, Any

import attr
import unyt
import matplotlib.pyplot as plt


@attr.s(auto_attribs=True)
class PlotExtension:
    name: str = attr.ib(converter=str)
    config: GlobalConfig
    metadata: MetadataSpecification

    x: unyt.unyt_array
    y: Optional[unyt.unyt_array] = None
    z: Optional[unyt.unyt_array] = None

    # Derived datasets should be converted to these before plotting.
    x_units: unyt.unyt_quantity = unyt.unyt_quantity(1.0, None)
    y_units: unyt.unyt_quantity = unyt.unyt_quantity(1.0, None)
    z_units: unyt.unyt_quantity = unyt.unyt_quantity(1.0, None)

    # You should load the data from your JSON configuration here,
    # for example:
    # nbins: int = 25
    # with the = setting the default.

    def preprocess(self):
        """
        Pre-processing step, using the data passed in that has
        been read from file by the :class:`PlotModel`.

        You must not directly mutate the data passed to you,
        otherwise every other extension downstream will have
        broken data.
        """

        # Example: calculate a binned line.

        return

    def blit(self, fig: plt.Figure, axes: plt.Axes):
        """
        Your (one and only) chance to directly affect the figure.

        fig: plt.Figure
            The figure object associated with this matplotlib plot.

        axes: plt.Axes
            The axes to draw on for this matplotlib plot.
        """

        return

    def serialize(self) -> Optional[Dict[str, Any]]:
        """
        Serializes the data generated in the ``preprocess`` step
        to a dictionary. If there is no data generated, return
        ``None``.
        """

        return None
