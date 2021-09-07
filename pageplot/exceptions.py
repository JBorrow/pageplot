"""
Custom exceptions for pageplot
"""


class PagePlotParserError(Exception):
    def __init__(self, obj, message):
        self.obj = obj
        self.message = message
        super().__init__(self.message)


class PagePlotIncompatbleExtension(Exception):
    def __init__(self, obj, message):
        self.obj = obj
        self.message = message
        super().__init__(self.message)


class PagePlotMissingMetadataError(Exception):
    def __init__(self, obj, message):
        self.obj = (obj,)
        self.message = message
        super().__init__(self.message)
