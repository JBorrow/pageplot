"""
Global configuration and settings for a
full run of PlotPage.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, validator

import unyt
from matplotlib.pyplot import style

from pageplot.configextension import ConfigExtension



class GlobalConfig(BaseModel):
    stylesheet: Optional[str] = None

    unyt_matplotlib_support_enable: bool = True
    unyt_label_style: str = "[]"

    extensions: Dict[str, Dict[str, Any]] = {}

    @validator("stylesheet")
    def load_stylesheet(cls, v):
        style.use(v)

    @validator("unyt_matplotlib_support_enable", always=True)
    def enable_unyt_matplotlib_support(cls, v):
        if v:
            unyt.matplotlib_support.enable()
        else:
            unyt.matplotlib_support.disable()

        return

    @validator("unyt_label_style", always=True)
    def set_unyt_label_style(cls, v):
        if v not in ["[]", "()", "/"]:
            raise ValueError("You must choose one of [], (), or / for the unyt style.")

        unyt.matplotlib_support.label_style = v

        return

    def run_extensions(self, additional_extensions: Optional[Dict[str, ConfigExtension]] = None):
        """
        Sets up the internal extensions and affixes them to the
        object.
        """

        from pageplot.extensions import built_in_config_extensions

        if additional_extensions is None:
            additional_extensions = {}

        combined_extensions = {**built_in_config_extensions, **additional_extensions}

        for name, Extension in combined_extensions.items():
            object.__setattr__(self, name, Extension(**self.extensions.get(name, {})))

        return
