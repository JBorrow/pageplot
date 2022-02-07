"""
A wrapper for multiple IO components.
"""

from pathlib import Path
from typing import Any, List, Optional, Union

import attr
import numpy as np
import unyt

from pageplot.exceptions import PagePlotParserError

from .spec import IOSpecification, MetadataSpecification, dataset_searcher


@attr.s(auto_attribs=False)
class MultiMetadataSpecification:
    filenames: List[Path] = attr.ib()
    base_spec: MetadataSpecification = attr.ib()

    individual_metadata: List[MetadataSpecification]

    def __attrs_post_init__(self):
        self.individual_metadata = [
            self.base_spec(filename) for filename in self.filenames
        ]

    def __getattr__(self, attr) -> List[Any]:
        return [getattr(metadata, attr, None) for metadata in self.individual_metadata]


@attr.s(auto_attribs=False)
class MultiIOSpecification:
    filenames: List[Path] = attr.ib()

    base_data_spec: IOSpecification = attr.ib()
    base_metadata_spec: MetadataSpecification = attr.ib()

    metadata: MultiMetadataSpecification
    individual_data: List[IOSpecification]

    def __attrs_post_init__(self):
        self.individual_data = [
            self.base_data_spec(filename) for filename in self.filenames
        ]

        self.metadata = MultiMetadataSpecification(
            filenames=self.filenames,
            base_spec=self.base_metadata_spec,
        )

    def data_from_string(
        self,
        path: Optional[str],
        mask: Optional[Union[np.array, np.lib.index_tricks.IndexExpression]] = None,
    ) -> Optional[unyt.unyt_array]:
        """ """

        if path is None:
            return None

        if mask is None:
            mask = np.s_[:]

        individual_reads = []

        for data in self.individual_data:
            try:
                individual_reads.append(data.data_from_string(path=path, mask=None))
            except KeyError:
                # Must just not be in this file.
                continue

        if len(individual_reads) == 0:
            raise RuntimeError(
                f"Unable to find {path} in any files, or its units are not registered "
                "and the code raised a KeyError internally."
            )

        base_unit = individual_reads[-1].units
        base_name = individual_reads[-1].name

        for array in individual_reads:
            array.convert_to_units(base_unit)

        return unyt.unyt_array(
            np.concatenate(individual_reads)[mask], units=base_unit, name=base_name
        )

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
