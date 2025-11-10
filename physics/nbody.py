# physics/nbody.py
"""
Simulador N-body con interacciones gravitacionales newtonianas
Implementa el algoritmo de Verlet para estabilidad numérica
"""

import numpy as np
from scipy.integrate import solve_ivp
from .constants import G, SOLAR_SYSTEM_DATA, SCALE_FACTORS

class CelestialBody:
    """Representa un cuerpo celeste con propiedades físicas"""
    
    def __init__(self, name, mass, radius, position, velocity, color, emissive=False, **kwargs):
        self.name = name
        self.mass = mass
        self.radius = radius
        self.position = np.array(position, dtype=np.float64)
        self.velocity = np.array(velocity, dtype=np.float64)
        self.acceleration = np.zeros(3, dtype=np.float64)
        self.color = color
        self.emissive = emissive
        
        # Guardar TODOS los datos extra
        self.has_rings = kwargs.get('has_rings', False)
        self.rings = kwargs.get('rings', None)
        self.gradient = kwargs.get('gradient', None)
        self.orbital_elements = kwargs.get('orbital_elements', None)
        
        # Historial de trayectoria
        self.trail = []
        self.max_trail_length = 1000
    
    def add_to_trail(self):
        """Agrega posición actual al historial de trayectoria"""
        self.trail.append(self.position.copy())
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
    
    def to_dict(self, scale=True):
        """Convierte a diccionario para JSON"""
        if scale:
            pos = self.position * SCALE_FACTORS['distance']
            rad = self.radius * SCALE_FACTORS['radius']
        else:
            pos = self.position
            rad = self.radius
        
        result = {
            'name': self.name,
            'position': pos.tolist(),
            'velocity': self.velocity.tolist(),
            'radius': rad,
            'color': self.color,
            'emissive': self.emissive,
            'trail': [p.tolist() for p in self.trail[-100:]]
        }
        
        # Agregar anillos si tiene
        if self.has_rings:
            result['has_rings'] = True
            result['rings'] = self.rings
            print(f"📤 Enviando anillos de {self.name}: {self.rings}")
        
        # Agregar gradiente si tiene
        if self.gradient:
            result['gradient'] = self.gradient
        
        # Agregar período orbital si tiene
        if self.orbital_elements and 'period' in self.orbital_elements:
            result['orbital_period'] = self.orbital_elements['period']
        
        return result


class NBodySimulator:
    """Simulador de sistema N-body con gravedad newtoniana"""
    
    def __init__(self, time_step=3600, method='verlet'):
        self.bodies = []
        self.time = 0.0
        self.time_step = time_step  # segundos
        self.method = method  # 'verlet', 'rk4', 'euler'
        
    def add_body(self, body):
        """Agrega un cuerpo al sistema"""
        self.bodies.append(body)
    
    def initialize_solar_system(self):
        """Inicializa el sistema solar con datos reales"""
        for key, data in SOLAR_SYSTEM_DATA.items():
            body = CelestialBody(
                name=data['name'],
                mass=data['mass'],
                radius=data['radius'],
                position=data['position'].copy(),
                velocity=data['velocity'].copy(),
                color=data['color'],
                emissive=data.get('emissive', False),
                has_rings=data.get('has_rings', False),
                rings=data.get('rings', None),
                gradient=data.get('gradient', None),
                orbital_elements=data.get('orbital_elements', None)
            )
            self.add_body(body)
            
            if body.has_rings:
                print(f"💍 {body.name} tiene anillos configurados: {body.rings}")
    
    def compute_gravitational_acceleration(self, body_index):
        """
        Calcula la aceleración gravitacional sobre un cuerpo
        debido a todos los demás cuerpos
        
        F = G * m1 * m2 / r²
        a = F / m = G * m2 / r²
        """
        body = self.bodies[body_index]
        acceleration = np.zeros(3, dtype=np.float64)
        
        for i, other_body in enumerate(self.bodies):
            if i == body_index:
                continue
            
            # Vector de posición relativa
            r_vec = other_body.position - body.position
            r_magnitude = np.linalg.norm(r_vec)
            
            # Evitar división por cero (colisiones)
            if r_magnitude < (body.radius + other_body.radius):
                r_magnitude = body.radius + other_body.radius
            
            # Aceleración gravitacional: a = G * M / r² * r_hat
            r_hat = r_vec / r_magnitude
            a_magnitude = G * other_body.mass / (r_magnitude ** 2)
            acceleration += a_magnitude * r_hat
        
        return acceleration
    
    def step_verlet(self):
        """
        Integrador de Verlet (Velocity Verlet)
        Más estable y preciso que Euler para sistemas conservativos
        
        r(t+dt) = r(t) + v(t)*dt + 0.5*a(t)*dt²
        v(t+dt) = v(t) + 0.5*(a(t) + a(t+dt))*dt
        """
        dt = self.time_step
        
        # Calcular aceleraciones actuales
        accelerations = []
        for i in range(len(self.bodies)):
            acc = self.compute_gravitational_acceleration(i)
            accelerations.append(acc)
            self.bodies[i].acceleration = acc
        
        # Actualizar posiciones
        for i, body in enumerate(self.bodies):
            body.position += body.velocity * dt + 0.5 * accelerations[i] * dt**2
        
        # Calcular nuevas aceleraciones
        new_accelerations = []
        for i in range(len(self.bodies)):
            acc = self.compute_gravitational_acceleration(i)
            new_accelerations.append(acc)
        
        # Actualizar velocidades
        for i, body in enumerate(self.bodies):
            body.velocity += 0.5 * (accelerations[i] + new_accelerations[i]) * dt
            body.acceleration = new_accelerations[i]
            
            # Agregar a trayectoria cada 10 pasos
            if int(self.time / dt) % 10 == 0:
                body.add_to_trail()
        
        self.time += dt
    
    def step_rk4(self):
        """
        Integrador Runge-Kutta de 4to orden
        Muy preciso pero más costoso computacionalmente
        """
        def derivatives(t, state):
            """Calcula derivadas para RK4"""
            n = len(self.bodies)
            positions = state[:3*n].reshape(n, 3)
            velocities = state[3*n:].reshape(n, 3)
            
            # Calcular aceleraciones
            accelerations = np.zeros((n, 3))
            for i in range(n):
                for j in range(n):
                    if i == j:
                        continue
                    r_vec = positions[j] - positions[i]
                    r_mag = np.linalg.norm(r_vec)
                    if r_mag < 1e6:  # Evitar singularidades
                        r_mag = 1e6
                    r_hat = r_vec / r_mag
                    accelerations[i] += G * self.bodies[j].mass * r_hat / r_mag**2
            
            return np.concatenate([velocities.flatten(), accelerations.flatten()])
        
        # Estado actual
        state = np.concatenate([
            np.array([b.position for b in self.bodies]).flatten(),
            np.array([b.velocity for b in self.bodies]).flatten()
        ])
        
        # Integrar
        sol = solve_ivp(
            derivatives,
            (self.time, self.time + self.time_step),
            state,
            method='RK45',
            max_step=self.time_step
        )
        
        # Actualizar estados
        final_state = sol.y[:, -1]
        n = len(self.bodies)
        positions = final_state[:3*n].reshape(n, 3)
        velocities = final_state[3*n:].reshape(n, 3)
        
        for i, body in enumerate(self.bodies):
            body.position = positions[i]
            body.velocity = velocities[i]
            if int(self.time / self.time_step) % 10 == 0:
                body.add_to_trail()
        
        self.time += self.time_step
    
    def step(self):
        """Ejecuta un paso de simulación"""
        if self.method == 'verlet':
            self.step_verlet()
        elif self.method == 'rk4':
            self.step_rk4()
        else:
            raise ValueError(f"Método desconocido: {self.method}")
    
    def get_state(self):
        """Retorna el estado actual del sistema"""
        return {
            'time': self.time,
            'bodies': [body.to_dict() for body in self.bodies]
        }
    
    def compute_energy(self):
        """Calcula la energía total del sistema (conservada en sistemas ideales)"""
        kinetic = 0.0
        potential = 0.0
        
        # Energía cinética
        for body in self.bodies:
            kinetic += 0.5 * body.mass * np.dot(body.velocity, body.velocity)
        
        # Energía potencial gravitacional
        for i, body1 in enumerate(self.bodies):
            for j, body2 in enumerate(self.bodies[i+1:], start=i+1):
                r = np.linalg.norm(body2.position - body1.position)
                potential -= G * body1.mass * body2.mass / r
        
        return {
            'kinetic': kinetic,
            'potential': potential,
            'total': kinetic + potential
        }
