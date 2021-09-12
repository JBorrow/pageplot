"""
The base top-level plot model class.

From this all data and plotting flow.
"""

from operator import truediv

from pydantic.class_validators import validator
from pageplot.exceptions import PagePlotParserError
from pathlib import Path
from typing import Any, Optional, Dict, List, Union
from pydantic import BaseModel

from pageplot.extensionmodel import PlotExtension
from pageplot.extensions import built_in_extensions
from pageplot.io.spec import IOSpecification
from pageplot.config import GlobalConfig
from pageplot.mask import get_mask

import matplotlib.pyplot as plt
import numpy as np
import unyt


class PlotModel(BaseModel):
    name: str
    config: GlobalConfig
    plot_spec: Dict[str, Any]

    x: str
    y: Optional[str] = None
    z: Optional[str] = None

    # Output units for the plot.
    x_units: Union[str, None, unyt.unyt_quantity] = None
    y_units: Union[str, None, unyt.unyt_quantity] = None
    z_units: Union[str, None, unyt.unyt_quantity] = None

    mask: Optional[str] = None

    data: IOSpecification = None
    fig: plt.Figure = None
    axes: plt.Axes = None
    extensions: Dict[str, PlotExtension] = None

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

    def run_extensions(
        self, additional_extensions: Optional[Dict[str, PlotExtension]] = None
    ):
        """
        Run the figure extensions (these provide all data for the figures,
        excluding the plotting). Internal extensions are performed
        first, then any additional extensions are executed.

        additional_extensions: Dict[str, PlotExtension]
            Any additional extensions conforming to the specification.
        """

        # First, sort out units and masking
        units = {
            "x_units": self.x_units,
            "y_units": self.y_units,
            "z_units": self.z_units,
        }

        for name, value in units.items():
            if value is None:
                if (associated_data := getattr(self, name[0])) is None:
                    units[name] = unyt.unyt_quantity(1.0, None)
                else:
                    units[name] = associated_data.units
            else:
                units[name] = unyt.unyt_quantity(1.0, value)

        mask = get_mask(data=self.data, mask_text=self.mask)

        self.extensions = {}

        if additional_extensions is None:
            additional_extensions = {}

        combined_extensions = {**built_in_extensions, **additional_extensions}

        for name in self.plot_spec.keys():
            try:
                Extension = combined_extensions[name]
            except KeyError:
                raise PagePlotParserError(
                    name, "Unable to find matching extension for configuration value."
                )

            extension = Extension(
                name=name,
                config=self.config,
                metadata=self.data.metadata,
                x=self.data.data_from_string(self.x, mask=mask),
                y=self.data.data_from_string(self.y, mask=mask),
                z=self.data.data_from_string(self.z, mask=mask),
                **units,
                **self.plot_spec.get(name, {}),
            )

            extension.preprocess()

            self.extensions[name] = extension

        return

    def perform_blitting(self):
        """
        Performs the blitting (creating the figure).

        Without this, the extensions are just 'created' and pre-processed
        without affecting or creating the figure.
        """

        for extension in self.extensions.values():
            extension.blit(fig=self.fig, axes=self.axes)

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

    def serialize(self) -> Dict[str, Any]:
        """
        Serializes the contents of the extensions to a dictionary.

        Note that you do not have to have 'created' the figure to run this,
        if you just want the data you should be able to just request
        the serialized data.
        """

        serialized = {name: ext.serialize() for name, ext in self.extensions.items()}

        return serialized


    def finalize(self):
        """
        Closes figures and cleans up.
        """

        plt.close(self.fig)

    class Config:
        arbitrary_types_allowed = True
