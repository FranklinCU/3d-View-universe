# physics/__init__.py
"""
Módulo de física para simulación N-body
"""

from .constants import G, AU, DAY, SOLAR_SYSTEM_DATA, SCALE_FACTORS
from .nbody import NBodySimulator, CelestialBody
from .integrator import Integrator

__all__ = [
    'G', 'AU', 'DAY', 'SOLAR_SYSTEM_DATA', 'SCALE_FACTORS',
    'NBodySimulator', 'CelestialBody', 'Integrator'
]
