"""
Main runner for the plots. Takes in filenames and spits out plots.
"""


import json
from pageplot.configextension import ConfigExtension
from pageplot.extensionmodel import PlotExtension
from pageplot.config import GlobalConfig
from pageplot.exceptions import PagePlotParserError
from pageplot.plotmodel import PlotModel
from pageplot.io.spec import IOSpecification
from pageplot.plotcontainer import PlotContainer
from pageplot.webpage.html import WebpageCreator
from pathlib import Path
from typing import Dict, List, Optional
import attr


@attr.s(auto_attribs=True)
class PagePlotRunner:
    """
    Main runner class for the page plot library.

    This takes in filenames and spits out plots.
    """

    config_filename: Path = attr.ib(converter=Path)
    data: IOSpecification
    plot_filenames: List[Path] = attr.ib(
        factory=list, converter=lambda x: [Path(a) for a in x]
    )

    file_extension: str = attr.ib(
        default=None, converter=attr.converters.default_if_none("png")
    )
    output_path: Path = attr.ib(default=Path("."), converter=Path)

    additional_plot_extensions: Optional[Dict[str, PlotExtension]] = attr.ib(
        factory=dict
    )
    additional_config_extensions: Optional[Dict[str, ConfigExtension]] = attr.ib(
        factory=dict
    )

    config: GlobalConfig = attr.ib(init=False)
    plot_container: PlotContainer = attr.ib(init=False)

    def load_config(self) -> GlobalConfig:
        """
        Loads the config from file.
        """

        with open(self.config_filename, "r") as handle:
            self.config = GlobalConfig(
                **json.load(handle),
                extensions=self.additional_config_extensions,
            )

        self.config.run_extensions()

        return self.config

    def load_plots(self) -> PlotContainer:
        """
        Loads the figures from the plot filenames. Sets the internal ``plot_container``
        property, and returns the plot container.

        May raise the ``PagePlotParserError`` if there are duplicate names.

        Returns
        -------

        plot_container: PlotContainer
            The filled ``PlotContainer`` ready for use.
        """

        plots: Dict[str, PlotModel] = {}

        for plot_filename in self.plot_filenames:
            with open(plot_filename, "r") as handle:
                raw_json = json.load(handle)

            for name, plot in raw_json.items():
                if name in plots:
                    raise PagePlotParserError(
                        name, f"Duplicate plot name {name} found."
                    )
                else:
                    kwargs = {
                        name: plot.pop(name, None)
                        for name in [
                            "x",
                            "y",
                            "z",
                            "x_units",
                            "y_units",
                            "z_units",
                            "mask",
                        ]
                    }

                    plot_model = PlotModel(
                        name=name,
                        config=self.config,
                        plot_spec=plot,
                        **kwargs,
                    )

                    plots[name] = plot_model

        self.plot_container = PlotContainer(
            data=self.data,
            plots=plots,
            file_extension=self.file_extension,
            output_path=self.output_path,
        )

        return self.plot_container

    def __attrs_post_init__(self):
        self.load_config()
        self.load_plots()

    def create_figures(self):
        """
        Makes the plots, and saves them out to disk.
        """

        self.plot_container.setup_figures()
        self.plot_container.run_extensions()
        self.plot_container.create_figures()

    def create_webpage(self, webpage_filename: Path = Path("index.html")):
        """
        Webpage output, links the plots together.

        Parameters
        ----------

        webpage_filename: Path
            Defaults to index.html. Releative to the plot output path.
        """

        webpage = WebpageCreator()
        webpage.add_metadata("PagePlot")
        webpage.add_plots(plot_container=self.plot_container)
        webpage.render_webpage()
        webpage.save_html(self.output_path / webpage_filename)

    def serialize(self, serialized_data_filename: Path):
        """
        Serializes all of the data, and saves it to disk.

        Parameters
        ----------

        serialized_data_filename: Path
            Path to the output JSON file.
        """

        with open(serialized_data_filename, "w") as handle:
            json.dump(self.plot_container.serialize(), handle)
