"""
Global configuration and settings for a
full run of PlotPage.
"""

from typing import Any, Dict, Optional

import attr
import unyt
from matplotlib.pyplot import style

from pageplot.configextension import ConfigExtension


@attr.s(auto_attribs=True)
class GlobalConfig:
    stylesheet: Optional[str] = None

    unyt_matplotlib_support_enable: bool = True
    unyt_label_style: str = attr.ib(default="[]")

    extensions: Dict[str, Dict[str, Any]] = {}

    def __attrs_post_init__(self):
        # Use the stylesheet
        if self.stylesheet is not None:
            style.use(self.stylesheet)

        # Should we be using unyt support?
        if self.unyt_matplotlib_support_enable:
            unyt.matplotlib_support.enable()
            unyt.matplotlib_support.label_style = self.unyt_label_style
        else:
            unyt.matplotlib_support.disable()

    @unyt_label_style.validator
    def _check_valid_label_style(self, _, value):
        if value not in ["[]", "()", "/"]:
            raise ValueError("You must choose one of [], (), or / for the unyt style.")

    def run_extensions(
        self, additional_extensions: Optional[Dict[str, ConfigExtension]] = None
    ):
        """
        Sets up the internal extensions and affixes them to the
        object.
        """

        from pageplot.extensions import built_in_config_extensions

        if additional_extensions is None:
            additional_extensions = {}

        combined_extensions = {**built_in_config_extensions, **additional_extensions}

        for name, Extension in combined_extensions.items():
            setattr(self, name, Extension(**self.extensions.get(name, {})))

        return
