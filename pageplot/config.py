"""
Global configuration and settings for a
full run of PlotPage.
"""

from typing import Optional
from pydantic import BaseModel, validator

import unyt
from matplotlib.pyplot import style


class GlobalConfig(BaseModel):
    stylesheet: Optional[str] = None

    unyt_matplotlib_support_enable: bool = True
    unyt_label_style: str = "[]"

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



