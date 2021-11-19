"""
Reader for AREPO SubFind HDF5 group catalogues.

Needs to loop over many, many files, so employs a parallel mapper to
do that. These are typically latency limited on HPC systems.
"""

from typing import Optional, Type, Dict, Any, Union, List

import attr

from pageplot.exceptions import PagePlotParserError
from .spec import IOSpecification, MetadataSpecification

from glob import glob
from pathlib import Path

import h5py
import unyt

import numpy as np


@attr.s(auto_attribs=True)
class MetadataAREPOSubFind(MetadataSpecification):
    """
    All quantities are given as h and a-free when appropriate.
    """

    # Base units
    length: unyt.unyt_quantity = attr.ib(init=False)
    mass: unyt.unyt_quantity = attr.ib(init=False)
    velocity: unyt.unyt_quantity = attr.ib(init=False)
    time: unyt.unyt_quantity = attr.ib(init=False)

    box_length: unyt.unyt_quantity = attr.ib(init=False)
    a: float = attr.ib(init=False)
    z: float = attr.ib(init=False)
    h: float = attr.ib(init=False)

    unit_registry: Dict[str, Optional[unyt.unyt_quantity]] = attr.ib(init=False)

    def get_parameter(
        self, name: str, in_units: str, out_units: str
    ) -> unyt.unyt_quantity:
        with h5py.File(self.filename, "r") as handle:
            return unyt.unyt_quantity(handle["Parameters"].attrs[name], in_units).to(
                out_units
            )

    def get_header(self, name: str) -> Any:
        with h5py.File(self.filename, "r") as handle:
            return handle["Header"].attrs[name]

    def __attrs_post_init__(self):
        # Loads in all the metadata after initialisation
        self.length = self.get_parameter("UnitLength_in_cm", "cm", "kpc")
        self.mass = self.get_parameter("UnitMass_in_g", "g", "Solar_Mass")
        self.velocity = self.get_parameter("UnitVelocity_in_cm_per_s", "cm/s", "km/s")
        self.time = (self.length / self.velocity).to("Gyr")

        self.a = float(self.get_header("Time"))
        self.z = float(self.get_header("Redshift"))
        self.h = float(self.get_header("HubbleParam"))

        self.box_length = unyt.unyt_quantity(
            float(self.get_header("BoxSize")) / self.h, self.length
        )
        self.box_volume = self.box_length ** 3

        # Set up unit registry. This gives units for all possible fields.
        self.unit_registry = {
            "Group/GroupBHMass": self.mass / self.h,
            "Group/GroupBHMdot": self.mass / self.time,
            "Group/GroupCM": self.a * self.length / self.h,
            "Group/GroupFirstSub": None,
            "Group/GroupGasMetalFractions": None,
            "Group/GroupGasMetallicity": None,
            "Group/GroupLen": None,
            "Group/GroupLenType": None,
            "Group/GroupMass": self.mass / self.h,
            "Group/GroupMassType": self.mass / self.h,
            "Group/GroupNsubs": None,
            "Group/GroupPos": self.a * self.length / self.h,
            # Manual unit alert
            "Group/GroupSFR": unyt.unyt_quantity(1.0, "Solar_Mass / year"),
            "Group/GroupStarMetalFractions": None,
            "Group/GroupStarMetallicity": None,
            # Peculiar velocity obtained by multiplying by 1 / a
            "Group/GroupVel": self.velocity / self.a,
            "Group/GroupWindMass": self.mass / self.h,
            "Group/Group_M_Crit200": self.mass / self.h,
            "Group/Group_M_Crit500": self.mass / self.h,
            "Group/Group_M_Mean200": self.mass / self.h,
            "Group/Group_M_TopHat200": self.mass / self.h,
            "Group/Group_R_Crit200": self.a * self.length / self.h,
            "Group/Group_R_Crit500": self.a * self.length / self.h,
            "Group/Group_R_Mean200": self.a * self.length / self.h,
            "Group/Group_R_TopHat200": self.a * self.length / self.h,
            "Subhalo/SubhaloBHMass": self.mass / self.h,
            "Subhalo/SubhaloBHMdot": self.mass / self.time,
            "Subhalo/SubhaloBfldDisk": self.h
            * self.a ** 2
            * (self.mass)
            / ((self.length) * (self.time) ** 2),
            "Subhalo/SubhaloBfldHalo": self.h
            * self.a ** 2
            * (self.mass)
            / ((self.length) * (self.time) ** 2),
            "Subhalo/SubhaloCM": self.a * self.length / self.h,
            "Subhalo/SubhaloFlag": None,
            "Subhalo/SubhaloGasMetalFractions": None,
            "Subhalo/SubhaloGasMetalFractionsHalfRad": None,
            "Subhalo/SubhaloGasMetalFractionsMaxRad": None,
            "Subhalo/SubhaloGasMetalFractionsSfr": None,
            "Subhalo/SubhaloGasMetalFractionsSfrWeighted": None,
            "Subhalo/SubhaloGasMetallicity": None,
            "Subhalo/SubhaloGasMetallicityHalfRad": None,
            "Subhalo/SubhaloGasMetallicityMaxRad": None,
            "Subhalo/SubhaloGasMetallicitySfr": None,
            "Subhalo/SubhaloGasMetallicitySfrWeighted": None,
            "Subhalo/SubhaloGrNr": None,
            "Subhalo/SubhaloHalfmassRad": self.a * self.length / self.h,
            "Subhalo/SubhaloHalfmassRadType": self.a * self.length / self.h,
            "Subhalo/SubhaloIDMostbound": None,
            "Subhalo/SubhaloLen": None,
            "Subhalo/SubhaloLenType": None,
            "Subhalo/SubhaloMass": self.mass / self.h,
            "Subhalo/SubhaloMassInHalfRad": self.mass / self.h,
            "Subhalo/SubhaloMassInHalfRadType": self.mass / self.h,
            "Subhalo/SubhaloMassInMaxRad": self.mass / self.h,
            "Subhalo/SubhaloMassInMaxRadType": self.mass / self.h,
            "Subhalo/SubhaloMassInRad": self.mass / self.h,
            "Subhalo/SubhaloMassInRadType": self.mass / self.h,
            "Subhalo/SubhaloMassType": self.mass / self.h,
            "Subhalo/SubhaloParent": None,
            "Subhalo/SubhaloPos": self.a * self.length / self.h,
            # Manual unit alert!
            "Subhalo/SubhaloSFR": unyt.unyt_quantity(1.0, "Solar_Mass / year"),
            "Subhalo/SubhaloSFRinHalfRad": unyt.unyt_quantity(1.0, "Solar_Mass / year"),
            "Subhalo/SubhaloSFRinMaxRad": unyt.unyt_quantity(1.0, "Solar_Mass / year"),
            "Subhalo/SubhaloSFRinRad": unyt.unyt_quantity(1.0, "Solar_Mass / year"),
            "Subhalo/SubhaloSpin": self.velocity * self.length / self.h,
            "Subhalo/SubhaloStarMetalFractions": None,
            "Subhalo/SubhaloStarMetalFractionsHalfRad": None,
            "Subhalo/SubhaloStarMetalFractionsMaxRad": None,
            "Subhalo/SubhaloStarMetallicity": None,
            "Subhalo/SubhaloStarMetallicityHalfRad": None,
            "Subhalo/SubhaloStarMetallicityMaxRad": None,
            # In magnitudes
            "Subhalo/SubhaloStellarPhotometrics": None,
            "Subhalo/SubhaloStellarPhotometricsMassInRad": self.mass / self.h,
            "Subhalo/SubhaloStellarPhotometricsRad": self.a * self.length / self.h,
            "Subhalo/SubhaloVel": self.velocity,
            "Subhalo/SubhaloVelDisp": self.velocity,
            "Subhalo/SubhaloVmax": self.velocity,
            "Subhalo/SubhaloVmaxRad": self.a * self.length / self.h,
            "Subhalo/SubhaloWindMass": self.mass / self.h,
        }


@attr.s(auto_attribs=True)
class IOAREPOSubFind(IOSpecification):
    # Specification assocaited with this IOSpecification
    metadata_specification: Type = MetadataAREPOSubFind
    # Storage object that is lazy-loaded
    metadata: MetadataAREPOSubFind = None

    # Internals
    ordered_filenames: Optional[List[Path]] = None

    def get_unit(self, field: str) -> unyt.unyt_quantity:
        """
        Gets the appropriate unit for the field. Ensures trailing
        slash is removed if required.
        """

        if field.startswith("/"):
            search_field = field[1:]
        else:
            search_field = field

        return self.metadata.unit_registry[search_field]

    def get_ordered_filenames(self):
        """
        Stores the internal ``ordered_filenames``.
        """

        if self.filename.stem.endswith(".0"):
            if self.ordered_filenames is None:
                self.ordered_filenames = sorted(
                    self.filename.parent.glob(
                        self.filename.stem.replace(".0", r".*") + self.filename.suffix
                    ),
                    key=lambda x: int(x.stem.split(".")[-1]),
                )

        return

    def read_raw_field(self, field: str, selector: np.s_) -> np.array:
        """
        Reads a raw field from (potentially) many files.
        """

        if self.filename.stem.endswith(".0"):
            if self.ordered_filenames is None:
                self.get_ordered_filenames()

            read = []

            never_found = True

            for path in self.ordered_filenames:
                try:
                    with h5py.File(path, "r") as handle:
                        read.append(handle[field][selector])
                        never_found = False
                except KeyError:
                    # Empty file, just skip it.
                    continue
                except OSError:
                    raise PagePlotParserError(
                        self.filename, f"Unable to open file {path}"
                    )

            if never_found:
                raise KeyError(
                    f"Cannot find key {field} with selector {selector} in any files."
                )

            raw = np.concatenate(read)
        else:
            with h5py.File(self.filename, "r") as handle:
                raw = handle[field][selector]

        return raw

    def data_from_string(
        self,
        path: Optional[str],
        mask: Optional[Union[np.array, np.lib.index_tricks.IndexExpression]] = None,
    ) -> Optional[unyt.unyt_array]:
        """
        Gets data from the specified path. h5py does all the
        caching that you could ever need!

        path: Optional[str]
            Path in dataset with units. Example:
            ``/Coordinates/Gas Mpc``

        Notes
        -----

        When passed ``None``, returns ``None``
        """

        if path is None:
            return None

        if mask is None:
            mask = np.s_[:]

        if path.count("[") > 0:
            start = path.find("[")
            stop = path.find("]")

            field = path[:start]

            # For some reason python doesn't like us polluting the local namespace.
            stored_result = {}
            exec(f"selector = np.s_[{path[start+1:stop]}]", {"np": np}, stored_result)
            selector = stored_result["selector"]
        else:
            field = path
            selector = np.s_[:]

        return unyt.unyt_array(
            self.read_raw_field(field=field, selector=selector),
            self.get_unit(field),
            name=path,
        )[mask]
