"""
PlotModel conatiner, used to 'create all the plots'.
"""

from pathlib import Path
from typing import Any, Dict

import attr

from pageplot.extensionmodel import PlotExtension
from pageplot.io.spec import IOSpecification
from pageplot.plotmodel import PlotModel


@attr.s(auto_attribs=True)
class PlotContainer:
    """
    Plot container, containing many instances of :cls:`PlotModel`.

    Used to create all of the figures in a uniform way.

    Parameters
    ----------

    data: IOSpecification
        Data conforming to the specification to be passed to all of the
        individual ``plot``s.

    plots: Dict[str, PlotModel]
        Dictionary (with keys the output names) of plots.

    file_extension: str
        File extension to use when writing out the figures.

    output_path: Path
        Where to write the figures. Defaults to the current working directory.

    additional_extensions: Dict[str, PlotExtension]
        Additional plot extensions to use with the given figures.
    """

    data: IOSpecification
    plots: Dict[str, PlotModel]

    file_extension: str = attr.ib(
        default=None, converter=attr.converters.default_if_none("png")
    )
    output_path: Path = attr.ib(default=Path("."), converter=Path)

    additional_extensions: Dict[str, PlotExtension] = attr.ib(
        default=attr.Factory(dict)
    )

    def setup_figures(self):
        """
        Sets up the figures, but does not yet
        perform any calculations.
        """

        for plot in self.plots.values():
            plot.associate_data(data=self.data)
            plot.setup_figures()

    def run_extensions(self):
        """
        Runs all extensions associated with plots.
        """

        for plot in self.plots.values():
            plot.run_extensions(additional_extensions=self.additional_extensions)

    def create_figures(self):
        """
        Creates all figures and saves them to disk.
        """

        for name, plot in self.plots.items():
            plot.perform_blitting()
            plot.save(self.output_path / f"{name}.{self.file_extension}")
            plot.finalize()

    def serialize(self) -> Dict[str, Any]:
        """
        Serializes the data from all figures to a dictionary
        that is returned.
        """

        return {name: plot.serialize() for name, plot in self.plots.items()}
