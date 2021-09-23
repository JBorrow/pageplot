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
    """
    Plot extension, used to calculate properties and apply them
    to the plots. You should provide overrides for the relevant
    functions:

    ``preprocess``, which loads and processes data. For instance,
    when creating a binned median line, this bins the data and stores
    it in the object.

    ``blit``, which uses the given figure and axes to plot the
    derived data from ``preprocess``.

    ``serialize``, which serializes the data to a dictionary for
    writing to disk.

    Parameters
    ----------

    name: str
        The name of this plot.
    
    config: GlobalConfig
        The global configuration object.

    metadata: MetadataSpecification
        The i/o metadata for the data which will be applied to the
        figure.

    x, y, z: unyt.unyt_array, optional
        The x, y, and z data. Apart from x, these are optional
        (depending on your extension, they may not be. This may raise
        ``PagePlotIncompatbleExtension``).

    x_units, y_units, z_units: unyt.unyt_quantity, optional
        The output units for the three dimensions.


    Notes
    -----

    Additional parameters will be added by implementers.
    """
    name: str = attr.ib(converter=str)
    config: GlobalConfig
    metadata: MetadataSpecification

    x: unyt.unyt_array
    y: Optional[unyt.unyt_array] = None
    z: Optional[unyt.unyt_array] = None

    # Derived datasets should be converted to these before plotting.
    x_units: unyt.unyt_quantity = unyt.dimensionless
    y_units: unyt.unyt_quantity = unyt.dimensionless
    z_units: unyt.unyt_quantity = unyt.dimensionless

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
