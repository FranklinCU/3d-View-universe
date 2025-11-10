# visualization/shader_math.py
"""
Funciones matemáticas para shaders y renderizado procedural
"""

import numpy as np

class ShaderMath:
    """Funciones matemáticas para generación procedural"""
    
    @staticmethod
    def perlin_noise_3d(x, y, z, octaves=4, persistence=0.5, lacunarity=2.0):
        """
        Ruido Perlin 3D simplificado
        Usado para generar texturas procedurales
        """
        total = 0.0
        frequency = 1.0
        amplitude = 1.0
        max_value = 0.0
        
        for _ in range(octaves):
            total += ShaderMath._noise3d(
                x * frequency, 
                y * frequency, 
                z * frequency
            ) * amplitude
            
            max_value += amplitude
            amplitude *= persistence
            frequency *= lacunarity
        
        return total / max_value
    
    @staticmethod
    def _noise3d(x, y, z):
        """Función de ruido básica 3D"""
        # Componentes sinusoidales entrelazadas
        n = (
            np.sin(x * 2.1) * np.cos(y * 1.7) +
            np.sin(y * 3.3) * np.cos(z * 2.4) +
            np.sin(z * 1.9) * np.cos(x * 2.8) +
            np.sin(x * 0.7 + y * 1.3) * np.cos(z * 0.9) +
            np.sin(y * 0.5 + z * 1.1) * np.cos(x * 1.4)
        ) / 5.0
        
        return n
    
    @staticmethod
    def turbulence(x, y, z, size=32):
        """
        Función de turbulencia (ruido fractal)
        Útil para nubes, plasma, etc.
        """
        value = 0.0
        initial_size = size
        
        while size >= 1:
            value += ShaderMath._noise3d(
                x / size, 
                y / size, 
                z / size
            ) * size
            size /= 2.0
        
        return value / initial_size
    
    @staticmethod
    def marble_pattern(x, y, z, scale=1.0):
        """Patrón de mármol procedural"""
        return np.sin(
            x * scale + 
            ShaderMath.turbulence(x, y, z, 32) * 0.5
        )
    
    @staticmethod
    def wood_pattern(x, y, z, ring_frequency=10.0):
        """Patrón de madera procedural"""
        distance = np.sqrt(x*x + z*z)
        return np.sin(distance * ring_frequency + ShaderMath.turbulence(x, y, z, 16))
    
    @staticmethod
    def voronoi_noise(x, y, z, num_points=10):
        """
        Ruido Voronoi (células)
        Útil para cráteres, células, estructuras
        """
        # Puntos aleatorios (seeded para reproducibilidad)
        np.random.seed(42)
        points = np.random.rand(num_points, 3) * 10 - 5
        
        # Encontrar punto más cercano
        min_dist = float('inf')
        for point in points:
            dist = np.sqrt(
                (x - point[0])**2 + 
                (y - point[1])**2 + 
                (z - point[2])**2
            )
            if dist < min_dist:
                min_dist = dist
        
        return min_dist
    
    @staticmethod
    def generate_crater_pattern(lat, lon, crater_density=0.1):
        """
        Genera patrón de cráteres basado en coordenadas esféricas
        """
        # Convertir a cartesiano
        x = np.cos(lat) * np.cos(lon)
        y = np.cos(lat) * np.sin(lon)
        z = np.sin(lat)
        
        # Usar Voronoi para cráteres
        crater = ShaderMath.voronoi_noise(x*10, y*10, z*10)
        crater = max(0, 1.0 - crater * crater_density)
        
        return crater
    
    @staticmethod
    def generate_gas_bands(latitude, num_bands=8, turbulence_amount=0.3):
        """
        Genera bandas de gas para gigantes gaseosos
        """
        # Bandas basadas en latitud
        bands = np.sin(latitude * num_bands)
        
        # Agregar turbulencia
        turb = ShaderMath._noise3d(
            latitude * 5, 
            np.cos(latitude) * 3, 
            np.sin(latitude) * 4
        ) * turbulence_amount
        
        return bands + turb
    
    @staticmethod
    def phong_lighting(normal, light_dir, view_dir, shininess=32):
        """
        Modelo de iluminación Phong
        
        I = I_ambient + I_diffuse + I_specular
        """
        # Normalizar vectores
        N = normal / np.linalg.norm(normal)
        L = light_dir / np.linalg.norm(light_dir)
        V = view_dir / np.linalg.norm(view_dir)
        
        # Componente ambiental
        ambient = 0.1
        
        # Componente difusa (Lambert)
        diffuse = max(0, np.dot(N, L)) * 0.6
        
        # Componente especular
        R = 2 * np.dot(N, L) * N - L
        specular = pow(max(0, np.dot(R, V)), shininess) * 0.3
        
        return ambient + diffuse + specular
    
    @staticmethod
    def fresnel_effect(normal, view_dir, ior=1.5):
        """
        Efecto Fresnel (reflexión en bordes)
        Útil para atmósferas
        """
        N = normal / np.linalg.norm(normal)
        V = view_dir / np.linalg.norm(view_dir)
        
        cos_theta = abs(np.dot(N, V))
        
        # Aproximación de Schlick
        R0 = ((1.0 - ior) / (1.0 + ior)) ** 2
        fresnel = R0 + (1.0 - R0) * (1.0 - cos_theta) ** 5
        
        return fresnel
