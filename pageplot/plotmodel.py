"""
The base top-level plot model class.

From this all data and plotting flow.
"""

from operator import truediv
from pathlib import Path
from typing import Any, Optional, Dict, List
from pydantic import BaseModel

from pageplot.extensionmodel import PlotExtension
from pageplot.extensions import built_in_extensions
from pageplot.io.spec import IOSpecification
from pageplot.config import GlobalConfig

import matplotlib.pyplot as plt


class PlotModel(BaseModel):
    name: str
    config: GlobalConfig
    plot_spec: Dict[str, Any]

    x: str
    y: Optional[str] = None
    z: Optional[str] = None

    data: IOSpecification = None
    fig: plt.Figure = None
    axes: plt.Axes = None
    extensions: List[PlotExtension] = None

    def associate_data(self, data: IOSpecification):
        """
        Associates the data file (which conforms to the
        ``IOSpecification``) with the plot.

        data: IOSpecification
            Any data file that conforms to the specification.
        """

        self.data = data

    def setup_figures(self):
        """
        Sets up the internal figure and axes.
        """

        self.fig, self.axes = plt.subplots()

        return

    def run_extensions(self, additional_extensions: Optional[Dict[str, PlotExtension]] = None):
        """
        Run the figure extensions (these provide all data to the figures,
        including the basic plotting). Internal extensions are performed
        first, then any additional extensions are executed.

        additional_extensions: Dict[str, PlotExtension]
            Any additional extensions conforming to the specification.
        """

        self.extensions = []

        if additional_extensions is None:
            additional_extensions = {}

        for name, Extension in {**built_in_extensions, **additional_extensions}.items():
            extension = Extension(
                name=name,
                config=self.config,
                x=self.data.data_from_string(self.x),
                y=self.data.data_from_string(self.y),
                z=self.data.data_from_string(self.z),
                **self.plot_spec.get(name, {}),
            )

            extension.preprocess()
            extension.blit(fig=self.fig, axes=self.axes)

            self.extensions.append(extension)

        return

    def save(self, filename: Path):
        """
        Saves the figure to file.

        filename: Path
            Filename that you would like to save the figure to. Can have
            any matplotlib-compatible file extension.

        Notes
        -----

        It's suggested that you run finalzie() after this function, otherwise
        there will be lots of figures open at one time causing potential slowdowns.
        """

        self.fig.savefig(filename)

        return

    def finalize(self):
        """
        Closes figures and cleans up.
        """

        plt.close(self.fig)

    class Config:
        arbitrary_types_allowed = True
