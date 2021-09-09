"""
Reader for AREPO SubFind HDF5 group catalogues.

Needs to loop over many, many files, so employs a parallel mapper to
do that. These are typically latency limited on HPC systems.
"""

from typing import Optional, Type, Dict, Any, Union

from pydantic.class_validators import validator
from pydantic.errors import NoneIsAllowedError

from pageplot.exceptions import PagePlotParserError
from .spec import IOSpecification, MetadataSpecification

from glob import glob

import h5py
import unyt

import numpy as np


class MetadataAREPOSubFind(MetadataSpecification):
    """
    All quantities are given as h and a-free when appropriate.
    """

    # Base units
    _length: unyt.unyt_quantity = None
    _mass: unyt.unyt_quantity = None
    _velocity: unyt.unyt_quantity = None
    _time: unyt.unyt_quantity = None

    _box_length: unyt.unyt_quantity = None
    _a: float = None
    _z: float = None
    _h: float = None

    _unit_registry: Dict[str, Any] = None

    @property
    def length(self):
        if self._length is None:
            with h5py.File(self.filename, "r") as handle:
                raw_value = handle["Parameters"].attrs["UnitLength_in_cm"]

            object.__setattr__(
                self, "_length", unyt.unyt_quantity(raw_value, "cm").to("kpc")
            )

        return self._length

    @property
    def mass(self):
        if self._mass is None:
            with h5py.File(self.filename, "r") as handle:
                raw_value = handle["Parameters"].attrs["UnitMass_in_g"]

            object.__setattr__(
                self, "_mass", unyt.unyt_quantity(raw_value, "g").to("Solar_Mass")
            )

        return self._mass

    @property
    def velocity(self):
        if self._velocity is None:
            with h5py.File(self.filename, "r") as handle:
                raw_value = handle["Parameters"].attrs["UnitVelocity_in_cm_per_s"]

            object.__setattr__(
                self, "_velocity", unyt.unyt_quantity(raw_value, "cm/s").to("km/s")
            )

        return self._velocity

    @property
    def time(self):
        return (self.length / self.velocity).to("Gyr")

    def _get_header(self, name) -> Any:
        with h5py.File(self.filename, "r") as handle:
            return handle["Header"].attrs[name]

    @property
    def box_length(self) -> unyt.unyt_quantity:
        """
        Co-moving box length.
        """
        if self._box_length is None:
            object.__setattr__(
                self,
                "_box_length",
                unyt.unyt_quantity(self._get_header("BoxSize") / self.h, self.length),
            )

        return self._box_length

    @property
    def box_volume(self) -> unyt.unyt_quantity:
        """
        Co-moving box volume.
        """
        return self.box_length ** 3

    @property
    def a(self) -> float:
        """
        Scale factor that the halo catalogue represents.
        """
        if self._a is None:
            object.__setattr__(self, "_a", self._get_header("Time"))

        return self._a

    @property
    def z(self) -> float:
        """
        Redshift that the halo catalogue represents.
        """
        if self._z is None:
            object.__setattr__(self, "_z", self._get_header("Redshift"))

        return self._z

    @property
    def h(self) -> float:
        """
        Hubble parameter ('little-h')
        """
        if self._h is None:
            object.__setattr__(self, "_h", self._get_header("HubbleParam"))

        return self._h

    @property
    def unit_registry(self) -> Dict:
        if self._unit_registry is None:
            object.__setattr__(
                self,
                "_unit_registry",
                {
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
                    "Subhalo/SubhaloSFRinHalfRad": unyt.unyt_quantity(
                        1.0, "Solar_Mass / year"
                    ),
                    "Subhalo/SubhaloSFRinMaxRad": unyt.unyt_quantity(
                        1.0, "Solar_Mass / year"
                    ),
                    "Subhalo/SubhaloSFRinRad": unyt.unyt_quantity(
                        1.0, "Solar_Mass / year"
                    ),
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
                    "Subhalo/SubhaloStellarPhotometricsRad": self.a
                    * self.length
                    / self.h,
                    "Subhalo/SubhaloVel": self.velocity,
                    "Subhalo/SubhaloVelDisp": self.velocity,
                    "Subhalo/SubhaloVmax": self.velocity,
                    "Subhalo/SubhaloVmaxRad": self.a * self.length / self.h,
                    "Subhalo/SubhaloWindMass": self.mass / self.h,
                },
            )

        return self._unit_registry

    class Config:
        arbitrary_types_allowed = True


class IOAREPOSubFind(IOSpecification):
    # Specification assocaited with this IOSpecification
    _metadata_specification: Type = MetadataAREPOSubFind
    # Storage object that is lazy-loaded
    _metadata: MetadataAREPOSubFind = None

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

    def read_raw_field(self, field: str, selector: np.s_) -> np.array:
        """
        Reads a raw field from (potentially) many files.
        """

        if self.filename.stem.endswith(".0"):
            read = []

            never_found = True

            for path in self.filename.parent.glob(
                self.filename.stem.replace(".0", r".*") + self.filename.suffix
            ):
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

    class Config:
        arbitrary_types_allowed = True
