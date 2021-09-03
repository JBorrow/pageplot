"""
Global configuration and settings for a
full run of PlotPage.
"""

from typing import Optional
from pydantic import BaseModel


class GlobalConfig(BaseModel):
    stylesheet: Optional[str] = None
