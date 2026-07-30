#!/usr/bin/env python3
"""
E8_Thermodynamic_Forensics -- Legendre Transform Engine
Canonical <-> Microcanonical duality for three fundamental systems.
Maps thermodynamic observables to E8 6-dim gauge signals.
"""

import math
from typing import List, Dict

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: THERMODYNAMIC SYSTEMS
# ═══════════════════════════════════════════════════════════════════════════════

class TwoLevelSystem:
    """N two-level systems with spacing epsilon."""
    def __init__(self, N: int, epsilon: float):
        self.N = N
        self.epsilon = epsilon

    def canonical(self, beta: float) -> Dict:
        x = math.exp(-beta * self.epsilon)
        logZ = self.N * math.log1p(x)  # log(1+x) to avoid overflow
        Phi = -logZ
        E = self.N * self.epsilon * x / (1 + x)
        S = Phi + beta * E
        T = 1.0 / beta if beta > 0 else float('inf')
        Z = math.exp(logZ) if logZ < 700 else float('inf')
        return {'Z': Z, 'Phi': Phi, 'E': E, 'S': S, 'T': T, 'beta': beta}

    def microcanonical(self, E: float) -> Dict:
        x = E / (self.N * self.epsilon)
        if x <= 0 or x >= 1:
            return {'S': -float('inf'), 'T': 0, 'beta': float('inf'), 'x': x}
        S = -self.N * (x * math.log(x) + (1 - x) * math.log(1 - x))
        beta = (1.0 / self.epsilon) * math.log((1 - x) / x) if 0 < x < 1 else float('inf')
        T = 1.0 / beta if beta > 0 else float('inf')
        return {'S': S, 'T': T, 'beta': beta, 'x': x, 'E': E}

    def legendre_check(self, beta: float) -> float:
        c = self.canonical(beta)
        m = self.microcanonical(c['E'])
        return abs(m['S'] - (beta * c['E'] - c['Phi']))


class IdealGas3D:
    """N non-interacting particles in volume V."""
    def __init__(self, N: int, V: float, m: float, h: float = 6.626e-34):
        self.N = N
        self.V = V
        self.m = m
        self.h = h

    def canonical(self, beta: float) -> Dict:
        lambda_T = self.h * math.sqrt(beta / (2 * math.pi * self.m))
        logZ = self.N * math.log(self.V / lambda_T**3) - math.log(math.factorial(self.N))
        Phi = -logZ
        E = 1.5 * self.N / beta
        S = Phi + beta * E
        T = 1.0 / beta
        Z = math.exp(logZ) if logZ < 700 else float('inf')
        return {'Z': Z, 'Phi': Phi, 'E': E, 'S': S, 'T': T, 'beta': beta}

    def microcanonical(self, E: float) -> Dict:
        if E <= 0:
            return {'S': -float('inf'), 'T': 0}
        term = (self.V / self.N) * ((4 * math.pi * self.m * E) / (3 * self.N * self.h**2)) ** 1.5
        S = self.N * (math.log(term) + 2.5)
        beta = 1.5 * self.N / E
        T = 1.0 / beta
        return {'S': S, 'T': T, 'beta': beta, 'E': E}

    def legendre_check(self, beta: float) -> float:
        c = self.canonical(beta)
        m = self.microcanonical(c['E'])
        return abs(m['S'] - (beta * c['E'] - c['Phi']))


class HarmonicOscillator:
    """N quantum harmonic oscillators with frequency omega."""
    def __init__(self, N: int, omega: float, hbar: float = 1.054e-34):
        self.N = N
        self.omega = omega
        self.hbar = hbar

    def canonical(self, beta: float) -> Dict:
        x = beta * self.hbar * self.omega / 2.0
        # log(2 sinh x): direct form is accurate for small x; for large x use the
        # log-space identity log(2 sinh x) = x + log(1 - e^{-2x}) to avoid sinh overflow.
        if x < 20:
            Phi = self.N * math.log(2 * math.sinh(x))
        else:
            Phi = self.N * (x + math.log1p(-math.exp(-2 * x)))
        E = self.N * self.hbar * self.omega / 2.0 * (1.0 / math.tanh(x))
        S = Phi + beta * E
        T = 1.0 / beta
        Z = math.exp(-Phi) if -Phi < 700 else float('inf')  # exp(-Phi), guarded against overflow
        return {'Z': Z, 'Phi': Phi, 'E': E, 'S': S, 'T': T, 'beta': beta}

    def microcanonical(self, E: float) -> Dict:
        n = E / (self.N * self.hbar * self.omega) - 0.5
        if n < 0:
            return {'S': -float('inf'), 'T': 0}
        S = self.N * ((n + 1) * math.log(n + 1) - n * math.log(n))
        beta = (1.0 / (self.hbar * self.omega)) * math.log((n + 1) / n) if n > 0 else float('inf')
        T = 1.0 / beta if beta > 0 else float('inf')
        return {'S': S, 'T': T, 'beta': beta, 'n': n, 'E': E}

    def legendre_check(self, beta: float) -> float:
        c = self.canonical(beta)
        m = self.microcanonical(c['E'])
        return abs(m['S'] - (beta * c['E'] - c['Phi']))


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: THERMO -> E8 SIGNAL MAPPER
# ═══════════════════════════════════════════════════════════════════════════════

class ThermoSignalMapper:
    @staticmethod
    def from_canonical(system, beta: float, metadata: Dict = None) -> List[float]:
        if isinstance(system, TwoLevelSystem):
            c = system.canonical(beta)
            x = c['E'] / (system.N * system.epsilon)
            s0 = x
            s1 = c['S'] / system.N / math.log(2) if c['S'] > 0 else 0
            s2 = 1.0 if beta < 0 else 0.0
            residual = system.legendre_check(beta)
            s3 = 1.0 / (1.0 + residual)
            s4 = beta**2 * (system.N * system.epsilon**2 * math.exp(beta*system.epsilon) / (1+math.exp(beta*system.epsilon))**2) / system.N
            s4 = min(s4 / 0.5, 1.0)
            s5 = 1.0 if metadata else 0.0
        elif isinstance(system, IdealGas3D):
            c = system.canonical(beta)
            s0 = min(c['E'] / (1.5 * system.N * 300 * 1.38e-23), 1.0)
            s1 = c['S'] / system.N / 10.0 if c['S'] > 0 else 0
            s2 = 1.0 if c['E'] <= 0 else 0.0
            residual = system.legendre_check(beta)
            s3 = 1.0 / (1.0 + residual)
            s4 = min(1.5 / system.N, 1.0)
            s5 = 1.0 if metadata else 0.0
        elif isinstance(system, HarmonicOscillator):
            c = system.canonical(beta)
            n = c['E'] / (system.N * system.hbar * system.omega) - 0.5
            s0 = min(n / 10.0, 1.0)
            s1 = c['S'] / system.N / 1.0 if c['S'] > 0 else 0
            s2 = 1.0 if n < 0 else 0.0
            residual = system.legendre_check(beta)
            s3 = 1.0 / (1.0 + residual)
            y = beta * system.hbar * system.omega
            denom = math.expm1(y) ** 2  # (exp(y)-1)^2, accurate for small y
            s4 = 1.0 if denom == 0 else min((system.hbar * system.omega)**2 * math.exp(y) / denom, 1.0)
            s5 = 1.0 if metadata else 0.0
        else:
            s0 = s1 = s2 = s3 = s4 = s5 = 0.5
        return [float(max(0, min(1, s))) for s in [s0, s1, s2, s3, s4, s5]]


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: LANDAUER LIMIT AUDITOR
# ═══════════════════════════════════════════════════════════════════════════════

class LandauerAuditor:
    kB = 1.380649e-23

    @classmethod
    def limit(cls, T: float) -> float:
        return cls.kB * T * math.log(2)

    @classmethod
    def audit_process(cls, bits_erased: int, T: float, actual_energy: float) -> Dict:
        min_energy = bits_erased * cls.limit(T)
        ratio = actual_energy / min_energy if min_energy > 0 else float('inf')
        return {
            'landauer_limit_J': min_energy,
            'actual_energy_J': actual_energy,
            'ratio': ratio,
            'compliant': actual_energy >= min_energy,
            'violation': actual_energy < min_energy,
            'excess_entropy_nats': (actual_energy - min_energy) / (cls.kB * T) if T > 0 else 0,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: SELF-TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("E8_THERMODYNAMIC_FORENSICS -- SELF-TEST")
    print("=" * 70)

    print("\n--- Two-Level System ---")
    tls = TwoLevelSystem(N=1000, epsilon=1.0)
    for beta in [0.1, 1.0, 10.0, -0.1]:
        c = tls.canonical(beta)
        m = tls.microcanonical(c['E'])
        residual = tls.legendre_check(beta)
        signal = ThermoSignalMapper.from_canonical(tls, beta)
        print(f"  beta={beta:>6.2f}  E={c['E']:>8.2f}  S={c['S']:>8.2f}  T={c['T']:>8.2f}  residual={residual:.2e}  signal={[round(s,3) for s in signal]}")

    print("\n--- Ideal Gas (3D) ---")
    gas = IdealGas3D(N=1000, V=1e-3, m=4.65e-26)
    for beta in [0.01, 0.1, 1.0]:
        c = gas.canonical(beta)
        residual = gas.legendre_check(beta)
        signal = ThermoSignalMapper.from_canonical(gas, beta)
        print(f"  beta={beta:>6.2f}  E={c['E']:.2e}  S={c['S']:.2f}  residual={residual:.2e}  signal={[round(s,3) for s in signal]}")

    print("\n--- Harmonic Oscillator ---")
    ho = HarmonicOscillator(N=1000, omega=1e14)
    for beta in [0.01, 0.1, 1.0, 10.0]:
        c = ho.canonical(beta)
        residual = ho.legendre_check(beta)
        signal = ThermoSignalMapper.from_canonical(ho, beta)
        print(f"  beta={beta:>6.2f}  E={c['E']:.2e}  S={c['S']:.2f}  residual={residual:.2e}  signal={[round(s,3) for s in signal]}")

    print("\n--- Landauer Audit ---")
    audit = LandauerAuditor.audit_process(bits_erased=1e12, T=300, actual_energy=2.87e-9)
    print(f"  Landauer limit: {audit['landauer_limit_J']:.2e} J")
    print(f"  Actual energy:  {audit['actual_energy_J']:.2e} J")
    print(f"  Ratio: {audit['ratio']:.2f}x")
    print(f"  Compliant: {audit['compliant']}")

    print("\n--- Negative Temperature (Anomaly) ---")
    c = tls.canonical(-0.5)
    signal = ThermoSignalMapper.from_canonical(tls, -0.5)
    print(f"  beta=-0.5: E={c['E']:.2f} T={c['T']:.2f} (negative!)")
    print(f"  Signal: {[round(s,3) for s in signal]}  s2(anomaly)={signal[2]:.3f}")
