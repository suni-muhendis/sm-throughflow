"""Conservative planar cascade wake reduction for prescribed profiles.

Constant-area, adiabatic control volume with no external force except
pressure on the traverse planes. See Amecke and Safarik, DLR-FB 95-32,
https://elib.dlr.de/37399/. The implementation solves the flux equations
directly for a perfect gas on the subsonic normal-flow branch.
"""
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class WakeState:
    pressure: float
    temperature: float
    normal_velocity: float
    tangential_velocity: float
    total_pressure: float
    mass_average_total_pressure: float
    mixing_entropy_over_R: float
    blockage: float


def reduce_wake(width, pressure, temperature, normal, tangential, *,
                edge_mass_flux, gamma=1.4, gas_constant=287.05):
    """Reduce a full-pitch traverse of cell means in a single frame.

    Blockage is the fractional mass deficit against the independently
    supplied edge mass flux on the same plane. A negative deficit is
    returned as measured; it may indicate that the reference is unsuitable.
    Total pressure at the mixed plane is computed from its mixed state.
    A branch requiring reverse flow or sonic/supersonic normal flow is
    outside this reference. Reynolds-stress fluxes are omitted.
    """
    width, pressure, temperature, normal, tangential = (
        np.asarray(value, dtype=float)
        for value in (width, pressure, temperature, normal, tangential)
    )
    fields = (pressure, temperature, normal, tangential)
    if width.ndim != 1 or not width.size or any(a.shape != width.shape for a in fields):
        raise ValueError("wake fields must be nonempty arrays on the same pitch cells")
    if not np.all(np.isfinite((width, *fields))) or not np.all(np.isfinite(
        (edge_mass_flux, gamma, gas_constant)
    )):
        raise ValueError("wake inputs must be finite")
    if gamma <= 1 or gas_constant <= 0 or edge_mass_flux <= 0:
        raise ValueError("gas constants and edge mass flux must be physical")
    if any(np.any(a <= 0) for a in (width, pressure, temperature, normal)):
        raise ValueError("wake cells require positive width, pressure, temperature and throughflow")
    if np.any(normal >= np.sqrt(gamma * gas_constant * temperature)):
        raise ValueError("wake reference requires subsonic normal flow in every cell")

    area = width / width.sum()
    cp = gamma * gas_constant / (gamma - 1)
    flux = pressure / (gas_constant * temperature) * normal
    mass_flux = np.dot(area, flux)
    mass_weights = area * flux / mass_flux
    normal_momentum = np.dot(area, pressure + flux * normal)
    mixed_tangential = np.dot(mass_weights, tangential)
    total_temperature = temperature + (normal**2 + tangential**2) / (2 * cp)
    mixed_total_temperature = np.dot(mass_weights, total_temperature)

    # F_n / j = u + R T/u. Eliminate T using the conserved total enthalpy.
    a = (gamma + 1) / (2 * gamma)
    b = normal_momentum / mass_flux
    c = gas_constant * (mixed_total_temperature - mixed_tangential**2 / (2 * cp))
    discriminant = b**2 - 4 * a * c
    if discriminant <= 0:
        raise ValueError("wake fluxes have no strictly subsonic mixed solution")
    mixed_normal = 2 * c / (b + np.sqrt(discriminant))
    mixed_temperature = mixed_total_temperature - (mixed_normal**2 + mixed_tangential**2) / (2 * cp)
    mixed_pressure = mass_flux / mixed_normal * gas_constant * mixed_temperature

    entropy_gain = (
        cp / gas_constant * np.dot(mass_weights, np.log(mixed_temperature / temperature))
        - np.dot(mass_weights, np.log(mixed_pressure / pressure))
    )
    if entropy_gain < -1e-12:
        raise ValueError("mixed state would decrease mass-averaged entropy")
    return WakeState(
        pressure=float(mixed_pressure),
        temperature=float(mixed_temperature),
        normal_velocity=float(mixed_normal),
        tangential_velocity=float(mixed_tangential),
        total_pressure=float(mixed_pressure * (mixed_total_temperature / mixed_temperature)**(cp / gas_constant)),
        mass_average_total_pressure=float(np.dot(mass_weights, pressure * (total_temperature / temperature)**(cp / gas_constant))),
        mixing_entropy_over_R=float(max(0., entropy_gain)),
        blockage=float(1 - mass_flux / edge_mass_flux),
    )
