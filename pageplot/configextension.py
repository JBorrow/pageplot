"""
Extension for configuration. Needs to be a separate file to avoid
circular imports.
"""

import attr


@attr.s(auto_attribs=True)
class ConfigExtension:
    """
    Used for creating extensions to the :class:`GlobalConfig`
    object. This is used to enable 'global' property setting.


    Notes
    -----

    For instance, in the ``velociraptor_data`` extension, a
    global relative path is required at configuration time (to
    prevent needing to type out a long path in each config
    file). This is enabled through a ``ConfigExtension``.

    You can access the properties here as
    ``GlobalConfig(...).{registration_name}.{any_additional_properties}``
    in your ``PlotExtensions``, where the ``GlobalConfig`` instance is
    usually available as ``self.config``.

    You can add your own extensions to the
    ``GlobalConfig(extensions={"registration_name": MyExt(ConfigExtension)})``.
    This should be the same registration name as an associated ``PlotExtension``
    should it be required.

    Note that extensions are _always_ used (internal and external)
    for the global configuration so should be happy recieving nothing
    (i.e. they must have defaults for everything).
    """

    registration_name: str = "base_config_extension"

    def activate_extension(self):
        """
        Do anything that you need to activate the extension in here,
        such as load relevant data, or convert types.
        """

        return
