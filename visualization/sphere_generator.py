# visualization/sphere_generator.py
"""
Generación procedural matemática de esferas
Sin texturas, todo calculado mediante funciones matemáticas
"""

import numpy as np
import json

class ProceduralSphere:
    """Genera vértices de esfera mediante ecuaciones paramétricas"""
    
    @staticmethod
    def generate_sphere_vertices(radius=1.0, segments=32, rings=16):
        """
        Genera vértices de una esfera usando coordenadas esféricas
        
        x = r * sin(θ) * cos(φ)
        y = r * sin(θ) * sin(φ)
        z = r * cos(θ)
        
        donde θ ∈ [0, π] y φ ∈ [0, 2π]
        """
        vertices = []
        normals = []
        indices = []
        
        for ring in range(rings + 1):
            theta = ring * np.pi / rings
            sin_theta = np.sin(theta)
            cos_theta = np.cos(theta)
            
            for seg in range(segments + 1):
                phi = seg * 2 * np.pi / segments
                sin_phi = np.sin(phi)
                cos_phi = np.cos(phi)
                
                # Posición del vértice
                x = radius * sin_theta * cos_phi
                y = radius * sin_theta * sin_phi
                z = radius * cos_theta
                
                vertices.append([x, y, z])
                
                # Normal (normalizada)
                normals.append([sin_theta * cos_phi, sin_theta * sin_phi, cos_theta])
        
        # Generar índices para triángulos
        for ring in range(rings):
            for seg in range(segments):
                first = ring * (segments + 1) + seg
                second = first + segments + 1
                
                indices.extend([first, second, first + 1])
                indices.extend([second, second + 1, first + 1])
        
        return {
            'vertices': vertices,
            'normals': normals,
            'indices': indices
        }
    
    @staticmethod
    def generate_procedural_pattern(vertex, body_type='earth'):
        """
        Genera patrones procedurales basados en ruido matemático
        Simula características visuales sin texturas
        """
        x, y, z = vertex
        
        # Función de ruido simplificada (Perlin-like)
        def noise_3d(x, y, z, frequency=1.0):
            return (
                np.sin(x * frequency) * np.cos(y * frequency) +
                np.sin(y * frequency * 1.3) * np.cos(z * frequency * 0.7) +
                np.sin(z * frequency * 0.9) * np.cos(x * frequency * 1.1)
            ) / 3.0
        
        # Diferentes patrones según el tipo de cuerpo
        if body_type == 'sun':
            # Plasma solar: ondas de alta frecuencia
            pattern = noise_3d(x, y, z, 5.0) * 0.3 + 0.7
            color_variation = [pattern, pattern * 0.9, pattern * 0.2]
            
        elif body_type == 'rocky':
            # Planetas rocosos: cráteres y montañas
            base = noise_3d(x, y, z, 2.0)
            craters = noise_3d(x, y, z, 10.0) * 0.3
            pattern = base + craters
            color_variation = [pattern, pattern * 0.8, pattern * 0.6]
            
        elif body_type == 'gas_giant':
            # Gigantes gaseosos: bandas horizontales
            latitude = np.arcsin(z / np.sqrt(x**2 + y**2 + z**2))
            bands = np.sin(latitude * 10) * 0.4
            turbulence = noise_3d(x, y, z, 3.0) * 0.2
            pattern = bands + turbulence
            color_variation = [pattern, pattern * 0.9, pattern * 0.7]
            
        else:
            pattern = noise_3d(x, y, z, 3.0)
            color_variation = [pattern, pattern, pattern]
        
        return color_variation
    
    @staticmethod
    def apply_lighting(normal, light_direction, base_color):
        """
        Calcula iluminación usando el modelo de Phong
        
        I = Ia + Id * (N · L) + Is * (R · V)^n
        """
        # Normalizar vectores
        N = normal / np.linalg.norm(normal)
        L = light_direction / np.linalg.norm(light_direction)
        
        # Componente difusa (Lambert)
        diffuse = max(0, np.dot(N, L))
        
        # Componente ambiental
        ambient = 0.2
        
        # Color final
        final_color = np.array(base_color) * (ambient + diffuse * 0.8)
        final_color = np.clip(final_color, 0, 1)
        
        return final_color.tolist()
