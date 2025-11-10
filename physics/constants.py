# physics/constants.py
"""
Constantes físicas con órbitas en el plano XZ (Y = altura)
"""

import numpy as np

# Constante gravitacional universal (m³ kg⁻¹ s⁻²)
G = 6.67430e-11

# Unidad Astronómica (metros)
AU = 1.496e11

# Día en segundos
DAY = 86400

# OPTIMIZACIÓN: Factores de escala mejorados
SCALE_FACTORS = {
    'distance': 2e-9,      # AUMENTADO: Mayor separación visual
    'radius': 3e-7,        # Radio reducido para mejor proporción
    'time': 43200          # Medio día por paso (más rápido)
}

# Masa del Sol
SUN_MASS = 1.989e30

# Datos reales con ÓRBITAS EN EL PLANO XZ
SOLAR_SYSTEM_DATA = {
    'sun': {
        'name': 'Sol',
        'mass': SUN_MASS,
        'radius': 6.96e8,
        'position': np.array([0.0, 0.0, 0.0]),  # Centro
        'velocity': np.array([0.0, 0.0, 0.0]),
        'color': [1.0, 0.85, 0.2],
        'emissive': True,
        'gradient': [1.0, 0.9, 0.2, 1.0, 0.7, 0.0]  # Gradiente amarillo-naranja
    },
    'mercury': {
        'name': 'Mercurio',
        'mass': 3.301e23,
        'radius': 2.44e6,
        # CAMBIO: Posición en X, órbita en plano XZ
        'position': np.array([0.387 * AU, 0.0, 0.0]),
        'velocity': np.array([0.0, 0.0, 47870.0]),  # Velocidad en Z
        'color': [0.7, 0.7, 0.7],
        'gradient': [0.6, 0.6, 0.6, 0.8, 0.8, 0.8],
        'orbital_elements': {
            'semi_major_axis': 0.387 * AU,
            'eccentricity': 0.206,
            'inclination': 7.0,
            'period': 87.97 * DAY
        }
    },
    'venus': {
        'name': 'Venus',
        'mass': 4.867e24,
        'radius': 6.05e6,
        'position': np.array([0.723 * AU, 0.0, 0.0]),
        'velocity': np.array([0.0, 0.0, 35020.0]),
        'color': [0.95, 0.75, 0.4],
        'gradient': [0.95, 0.75, 0.4, 0.85, 0.65, 0.3],
        'orbital_elements': {
            'semi_major_axis': 0.723 * AU,
            'eccentricity': 0.007,
            'inclination': 3.4,
            'period': 224.7 * DAY
        }
    },
    'earth': {
        'name': 'Tierra',
        'mass': 5.972e24,
        'radius': 6.371e6,
        'position': np.array([1.0 * AU, 0.0, 0.0]),
        'velocity': np.array([0.0, 0.0, 29780.0]),
        'color': [0.2, 0.5, 0.95],
        'gradient': [0.1, 0.3, 0.8, 0.3, 0.6, 1.0],
        'orbital_elements': {
            'semi_major_axis': 1.0 * AU,
            'eccentricity': 0.017,
            'inclination': 0.0,
            'period': 365.25 * DAY
        }
    },
    'mars': {
        'name': 'Marte',
        'mass': 6.417e23,
        'radius': 3.39e6,
        'position': np.array([1.524 * AU, 0.0, 0.0]),
        'velocity': np.array([0.0, 0.0, 24070.0]),
        'color': [0.95, 0.45, 0.2],
        'gradient': [0.95, 0.45, 0.2, 0.85, 0.35, 0.1],
        'orbital_elements': {
            'semi_major_axis': 1.524 * AU,
            'eccentricity': 0.093,
            'inclination': 1.85,
            'period': 686.98 * DAY
        }
    },
    'jupiter': {
        'name': 'Júpiter',
        'mass': 1.898e27,
        'radius': 6.99e7,
        'position': np.array([5.203 * AU, 0.0, 0.0]),
        'velocity': np.array([0.0, 0.0, 13070.0]),
        'color': [0.85, 0.75, 0.55],
        'gradient': [0.9, 0.8, 0.6, 0.8, 0.7, 0.5],
        'orbital_elements': {
            'semi_major_axis': 5.203 * AU,
            'eccentricity': 0.048,
            'inclination': 1.3,
            'period': 4332.59 * DAY
        }
    },
    'saturn': {
        'name': 'Saturno',
        'mass': 5.683e26,
        'radius': 5.82e7,
        'position': np.array([9.537 * AU, 0.0, 0.0]),
        'velocity': np.array([0.0, 0.0, 9690.0]),
        'color': [0.95, 0.85, 0.65],
        'gradient': [0.95, 0.85, 0.65, 0.85, 0.75, 0.55],
        'has_rings': True,
        'rings': {
            'inner_radius': 1.3,  # Multiplicador del radio del planeta
            'outer_radius': 2.3,
            'color': [0.9, 0.85, 0.7],
            'opacity': 0.7
        },
        'orbital_elements': {
            'semi_major_axis': 9.537 * AU,
            'eccentricity': 0.056,
            'inclination': 2.5,
            'period': 10759.22 * DAY
        }
    },
    'uranus': {
        'name': 'Urano',
        'mass': 8.681e25,
        'radius': 2.54e7,
        'position': np.array([19.191 * AU, 0.0, 0.0]),
        'velocity': np.array([0.0, 0.0, 6810.0]),
        'color': [0.4, 0.75, 0.95],
        'gradient': [0.3, 0.7, 0.9, 0.5, 0.8, 1.0],
        'orbital_elements': {
            'semi_major_axis': 19.191 * AU,
            'eccentricity': 0.047,
            'inclination': 0.8,
            'period': 30688.5 * DAY
        }
    },
    'neptune': {
        'name': 'Neptuno',
        'mass': 1.024e26,
        'radius': 2.46e7,
        'position': np.array([30.069 * AU, 0.0, 0.0]),
        'velocity': np.array([0.0, 0.0, 5430.0]),
        'color': [0.2, 0.4, 0.95],
        'gradient': [0.15, 0.35, 0.9, 0.25, 0.45, 1.0],
        'orbital_elements': {
            'semi_major_axis': 30.069 * AU,
            'eccentricity': 0.009,
            'inclination': 1.8,
            'period': 60182 * DAY
        }
    }
}
