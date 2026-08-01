"""E8 Thermodynamic Forensics — Legendre transform engine.

Canonical <-> microcanonical duality for three fundamental systems
(two-level, 3D ideal gas, quantum harmonic oscillator), a mapper that
projects thermodynamic observables onto E8 6-dim gauge signals, and a
Landauer-limit auditor for information-erasure energy compliance.
"""

from packages.e8_thermo.e8_thermodynamic_forensics import (
    HarmonicOscillator,
    IdealGas3D,
    LandauerAuditor,
    ThermoSignalMapper,
    TwoLevelSystem,
)

__all__ = [
    "TwoLevelSystem",
    "IdealGas3D",
    "HarmonicOscillator",
    "ThermoSignalMapper",
    "LandauerAuditor",
]
