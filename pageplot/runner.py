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
    Highest-level object interface to the library. This is probably
    where to start if you're just looking to make some figures.

    Takes in filenames specifying configuration objects, and allows
    easy serialization, webpage creation, and of course, figure creation.

    Parameters
    ----------

    config_filename: Path
        Filename of the configuration JSON. Used to generate the
        :class:`GlobalConfig` object. Used to specifiy, e.g., the
        stylesheet that you are using.
    
    data: IOSpecification
        Open data file that conforms to the specification. This will be
        handed to the plots down the line. Note that it just has to inherit
        from :class:`IOSpecification` and conform to the spec, not just be
        an instance of :class:`IOSpecification`.

    plot_filenames: List[Path]
        Filenames of the plot specification JSON. These will be concatenated
        and converted into a :class:`PlotContainer` containing individual instances
        of :class:`PlotModel`.

    file_extension: str, optional
        The extension of the resulting plots. Can be anything that
        ``matplotlib`` will output on your machine. By default this is ``png``
    
    output_path: Path, optional
        Where to save the output figures (and html). Should already exist,
        or an error will be raised. By default, this is the current working
        directory.

    additional_plot_extensions: Dict[str, PlotExtension]
        Additional extensions for the plots themselves. Will be shared amongst
        all of the plot models generated. This allows you to hook into the
        library and add custom plotting code. On the specification side,
        these will be read like any of the default extensions from your JSON.

    additional_config_extensions: Dict[str, ConfigExtension]
        Additional configuration extensions. This allows you to surface
        additional global variables (e.g. a fixed value you would like to have
        used to denote a fixed line on a plot). These will then be read from
        the extensions section in the ``config_filename``.
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
        Loads the config from file. Happens automatically on init.
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
        property, and returns the plot container. Happens automatically on init.

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
