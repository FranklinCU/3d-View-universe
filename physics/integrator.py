# physics/integrator.py
"""
Integradores numéricos para ecuaciones diferenciales
Implementa diferentes métodos de integración
"""

import numpy as np

class Integrator:
    """Métodos de integración numérica para sistemas dinámicos"""
    
    @staticmethod
    def euler(position, velocity, acceleration, dt):
        """
        Método de Euler (Forward Euler)
        Menos preciso pero rápido
        
        r(t+dt) = r(t) + v(t) * dt
        v(t+dt) = v(t) + a(t) * dt
        """
        new_position = position + velocity * dt
        new_velocity = velocity + acceleration * dt
        return new_position, new_velocity
    
    @staticmethod
    def leapfrog(position, velocity, acceleration, dt):
        """
        Método Leapfrog (Kick-Drift-Kick)
        Excelente conservación de energía
        
        v(t+dt/2) = v(t) + a(t) * dt/2        (Kick)
        r(t+dt) = r(t) + v(t+dt/2) * dt       (Drift)
        v(t+dt) = v(t+dt/2) + a(t+dt) * dt/2  (Kick)
        """
        # Half kick
        v_half = velocity + 0.5 * acceleration * dt
        
        # Full drift
        new_position = position + v_half * dt
        
        # Necesitamos calcular nueva aceleración aquí
        # (esto se hace fuera en el simulador)
        return new_position, v_half
    
    @staticmethod
    def verlet(position, velocity, acceleration, new_acceleration, dt):
        """
        Velocity Verlet
        Muy preciso para sistemas conservativos
        """
        new_position = position + velocity * dt + 0.5 * acceleration * dt**2
        new_velocity = velocity + 0.5 * (acceleration + new_acceleration) * dt
        return new_position, new_velocity
    
    @staticmethod
    def rk4_step(y, t, dt, derivatives_func):
        """
        Runge-Kutta de 4to orden
        
        y: estado actual [posiciones, velocidades]
        t: tiempo actual
        dt: paso de tiempo
        derivatives_func: función que calcula dy/dt
        """
        k1 = derivatives_func(t, y)
        k2 = derivatives_func(t + dt/2, y + dt*k1/2)
        k3 = derivatives_func(t + dt/2, y + dt*k2/2)
        k4 = derivatives_func(t + dt, y + dt*k3)
        
        return y + (dt/6) * (k1 + 2*k2 + 2*k3 + k4)
    
    @staticmethod
    def symplectic_euler(position, velocity, acceleration, dt):
        """
        Euler Simpéctico
        Conserva mejor la energía que Euler estándar
        
        v(t+dt) = v(t) + a(t) * dt
        r(t+dt) = r(t) + v(t+dt) * dt  <- usa velocidad actualizada
        """
        new_velocity = velocity + acceleration * dt
        new_position = position + new_velocity * dt
        return new_position, new_velocity
