"""
Velociraptor comparison data plotting extension.
"""

from velociraptor.observations import load_observations
from velociraptor.observations.objects import ObservationalData

from pageplot.configextension import ConfigExtension
from pageplot.extensionmodel import PlotExtension
from pageplot.exceptions import PagePlotIncompatbleExtension

from matplotlib.pyplot import Figure, Axes

from typing import List
from pathlib import Path

import attr


@attr.s(auto_attribs=True)
class VelociraptorDataConfigExtension(ConfigExtension):
    """
    Configuration extension for the velociraptor data.

    Parameters
    ----------

    data_path: Path, optional
        The data path where the observational data is stored.
        Helpful so you only need one copy of the observational
        data repository.
    """

    data_path: Path = attr.ib(default=Path("."), converter=Path)
    registration_name: str = "velociraptor_data"



@attr.s(auto_attribs=True)
class VelociraptorDataExtension(PlotExtension):
    """
    Plots data from the velociraptor library onto the axes.

    Parameters
    ----------

    files: List[Path]
        Filenames to 
    """
    files: List[Path] = attr.ib(
        default=attr.Factory(list), converter=lambda x: [Path(a) for a in x]
    )
    # Specify a custom scale factor range to load data within
    scale_factor_bracket_width: float = attr.ib(default=0.1, converter=float)

    observations: List[ObservationalData] = attr.ib(init=False)

    def preprocess(self):
        """
        Loads the data files in.
        """

        bracket_high = self.metadata.a - self.scale_factor_bracket_width
        bracket_low = self.metadata.a + self.scale_factor_bracket_width

        redshift_bracket = [1.0 / a - 1.0 for a in [bracket_low, bracket_high]]

        self.observations = load_observations(
            filenames=[
                self.config.velociraptor_data.data_path / file for file in self.files
            ],
            redshift_bracket=redshift_bracket,
        )

        return

    def blit(self, fig: Figure, axes: Axes):
        """
        Plots the data files that were read in preprocess on given axes.
        """

        for observation in self.observations:
            observation.x.convert_to_units(self.x_units)
            observation.y.convert_to_units(self.y_units)
            observation.plot_on_axes(axes=axes)

        return

    def serialize(self):
        return {
            "path": self.config.velociraptor_data.data_path,
            "included_data": [
                {
                    "filename": obs.filename,
                    "bibcode": obs.bibcode,
                }
                for obs in self.observations
            ],
        }
