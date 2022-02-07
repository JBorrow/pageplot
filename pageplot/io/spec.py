"""
IO Structures for PagePlot.

These can be extended by using their pluggy hooks
and iheritence.
"""

import re
from pathlib import Path
from typing import Optional, Type, Union

import attr
import numpy as np
import unyt

dataset_searcher = re.compile(r"\{(.*?)\}")


@attr.s(auto_attribs=True)
class MetadataSpecification:
    """
    Specification for adding additional metadata to the I/O specification.
    """

    filename: Path = attr.ib(converter=Path)

    # Suggested Additions:
    # - For Cosmology
    #   + box_volume, the volume of the box used (for mass functions)
    #   + a, the current scale factor (if appropriate)
    #   + z, the current redshift (if appropriate)


@attr.s(auto_attribs=True)
class IOSpecification:
    """
    Base required specification for I/O extensions.
    """

    filename: Path = attr.ib(converter=Path)

    # Specification assocaited with this IOSpecification
    metadata_specification: Type = MetadataSpecification
    # Storage object that is lazy-loaded
    metadata: MetadataSpecification = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.metadata = self.metadata_specification(filename=self.filename)

    def data_from_string(
        self,
        path: Optional[str],
        mask: Optional[Union[np.array, np.lib.index_tricks.IndexExpression]] = None,
    ) -> Optional[unyt.unyt_array]:
        """
        Return a ``unyt`` array containing data assocaited with the
        given input string. If passed ``None``, this function must return
        ``None``.

        A mask may optionally be provided to select data. This can
        be handled by the individual plugin creators for lazy-loading.
        """
        return unyt.unyt_array()

    def calculation_from_string(
        self,
        calculate: Optional[str],
        mask: Optional[Union[np.array, np.lib.index_tricks.IndexExpression]] = None,
    ) -> Optional[unyt.unyt_array]:
        """
        Perform a calculation by reading relevant arrays from the appropriate
        sub-class. Individual arrays are read using ``data_from_string``.

        When using combinations of arrays, their names must be enclosed in
        curly brackets. So:

        "{PartType0/Masses} * {PartType0/InternalEnergy}"
        "PartType0/Masses"
        "PartType0/Coordinates[:, 0]"
        "{PartType0/Masses} ** 0.9"
        "{PartType0/Coordinates[:, 1]} * 0.3"

        are valid, but

        "PartType0/Masses * PartType0/InternalEnergy"
        "PartType0/Coordinates + 0.1"

        are not (these examples use the H5py backend).

        Parameters
        ----------

        calculate: str, optional
            String to calculate with. Can be None, and the function
            will return None.

        mask: np.array, np.lib.index_tricks.IndexExpression, optional
            Additional potential mask for all datasets read.

        Returns
        -------

        array: unyt.unyt_array, optional
            Either the calculated array, or None, based upon input
            parameters.
        """

        if calculate is None:
            return None

        matches = dataset_searcher.findall(calculate)

        # We replace dataset names in origianl string with UIDs.
        for_numexpr = calculate
        # numexpr does not pass through unyt data, so we need to
        # deal with our unyt units with a string.
        for_unyt = calculate
        # Same deal with the names.
        for_name = calculate

        read_datasets = {"np": np}

        if len(matches) > 0:
            # Ensure unique
            for number, match in enumerate(set(matches)):
                variable_name = f"read_var_{number}"

                read_dataset = self.data_from_string(
                    path=match,
                    mask=mask,
                )

                read_datasets[variable_name] = read_dataset

                for_numexpr = for_numexpr.replace(rf"{{{match}}}", variable_name)
                for_unyt = for_unyt.replace(rf"{{{match}}}", str(read_dataset.units))
                for_name = for_name.replace(rf"{{{match}}}", str(read_dataset.name))

            exec(
                f"output = {for_numexpr}",
                read_datasets,
            )

            output = read_datasets["output"]

            try:
                output.name = for_name
            except AttributeError:
                # We must have stripped units.
                output = unyt.unyt_array(output, units="dimensionless", name=for_name)

            return output
        else:
            return self.data_from_string(
                path=calculate,
                mask=mask,
            )
