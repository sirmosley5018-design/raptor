# E8 Thermodynamic Forensics

A Legendre transform engine mapping canonical ↔ microcanonical thermodynamic
duality onto E8 6-dimensional gauge signals.

## Contents

- `e8_thermodynamic_forensics.py` — the core module:
  - `TwoLevelSystem`, `IdealGas3D`, `HarmonicOscillator` — three fundamental
    systems, each with `canonical(beta)`, `microcanonical(E)`, and
    `legendre_check(beta)` methods.
  - `ThermoSignalMapper` — maps thermodynamic observables to a 6-dim E8 gauge signal.
  - `LandauerAuditor` — audits energy dissipation against the Landauer limit.
- `reference_natural_units.py` — an independent natural-units reference
  implementation used to cross-validate the core module.

## Usage

```bash
python3 e8_thermodynamic_forensics.py   # runs the built-in self-test
```

```python
from e8_thermodynamic_forensics import TwoLevelSystem, ThermoSignalMapper, LandauerAuditor

tls = TwoLevelSystem(N=1000, epsilon=1.0)
c = tls.canonical(beta=1.0)          # {'Z', 'Phi', 'E', 'S', 'T', 'beta'}
signal = ThermoSignalMapper.from_canonical(tls, beta=1.0)
```

## Notes

- Entropy uses the convention `S = beta*E + logZ` (i.e. `S = beta*E - Phi`).
- Ideal-gas entropy can go formally negative at low temperature — this is the
  expected Sackur–Tetrode breakdown when the classical approximation leaves its
  domain of validity, not a bug.

## Requirements

- The core module (`e8_thermodynamic_forensics.py`) uses only the Python
  standard library.
- The reference (`reference_natural_units.py`) requires `numpy`.
