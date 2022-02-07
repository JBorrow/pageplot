"""
Function for parsing and using the mask variable.
"""

import operator
from typing import Optional, Union

import numpy as np
import unyt

from pageplot.io.spec import IOSpecification


def get_mask(
    data: IOSpecification, mask_text: Optional[str]
) -> Union[np.array, np.lib.index_tricks.IndexExpression]:
    """
    Gets the mask (boolean) based on input text and
    the available data that conforms to the specification.

    Masks of the following kind are accepted, where {DataName}
    is the name of an item that will be successfully parsed
    by data.data_from_string:

    {DataName} < Number Unit
    {DataName} > Number Unit
    {DataName} <= Number Unit
    {DataName} >= Number Unit
    {DataName} == Number Unit
    {DataName} != Number Unit
    {DataName} # Convert {DataName to a boolean}
    None # Returns np.s_[:]

    For example, you could have

    /My/Favourite/Dataset kpc < 1.0 Mpc

    for the in-built h5py IO Specification.

    Parameters
    ----------

    data: IOSpecification
        The data file to read from

    mask_text: str | None
        Mask text matching the above specification.
    """

    if mask_text is None:
        return np.s_[:]

    # In order of priority. Once a match is found the loop
    # exits (so e.g. <= needs to be before <).
    contain_possibilities = ["<=", ">=", "<", ">", "==", "!="]
    contain_operators = [
        operator.le,
        operator.ge,
        operator.lt,
        operator.gt,
        operator.eq,
        operator.ne,
    ]

    for op, check in zip(contain_operators, contain_possibilities):
        if check in mask_text:
            data_name, compare = mask_text.split(check)

            raw_data = data.calculation_from_string(data_name.strip())

            value, unit = compare.strip().split(" ", 1)

            return op(raw_data, unyt.unyt_quantity(float(value), unit))

    return data.calculation_from_string(mask_text).astype(bool)
