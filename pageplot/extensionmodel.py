"""
Model for extensions that perform plotting and
data production duties.
"""

from pageplot.config import GlobalConfig
from pydantic import BaseModel

from typing import Optional, Dict, Any

import unyt
import matplotlib.pyplot as plt


class PlotExtension(BaseModel):
    name: str
    config: GlobalConfig

    x: unyt.unyt_array
    y: Optional[unyt.unyt_array] = None
    z: Optional[unyt.unyt_array] = None

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

    class Config:
        # Required to allow typing for unyt.unyt_array
        arbitrary_types_allowed = True
