// static/js/utils.js
// Funciones de utilidad

const Utils = {
    // Formatear números científicos
    formatScientific(num, decimals = 2) {
        if (num === 0) return '0';
        const exponent = Math.floor(Math.log10(Math.abs(num)));
        const mantissa = (num / Math.pow(10, exponent)).toFixed(decimals);
        return `${mantissa}e${exponent}`;
    },
    
    // Formatear tiempo
    formatTime(seconds) {
        const days = Math.floor(seconds / 86400);
        const years = (days / 365.25).toFixed(2);
        
        if (days < 365) {
            return `${days} días`;
        } else {
            return `${years} años`;
        }
    },
    
    // Convertir AU a km
    auToKm(au) {
        return (au * 149597870.7).toFixed(0);
    },
    
    // Calcular distancia entre dos puntos
    distance(p1, p2) {
        return Math.sqrt(
            Math.pow(p2[0] - p1[0], 2) +
            Math.pow(p2[1] - p1[1], 2) +
            Math.pow(p2[2] - p1[2], 2)
        );
    },
    
    // Interpolación lineal
    lerp(a, b, t) {
        return a + (b - a) * t;
    },
    
    // Clamp value between min and max
    clamp(value, min, max) {
        return Math.max(min, Math.min(max, value));
    },
    
    // Generar color desde temperatura (kelvin)
    temperatureToColor(kelvin) {
        const temp = kelvin / 100;
        let r, g, b;
        
        // Red
        if (temp <= 66) {
            r = 255;
        } else {
            r = temp - 60;
            r = 329.698727446 * Math.pow(r, -0.1332047592);
            r = Utils.clamp(r, 0, 255);
        }
        
        // Green
        if (temp <= 66) {
            g = temp;
            g = 99.4708025861 * Math.log(g) - 161.1195681661;
            g = Utils.clamp(g, 0, 255);
        } else {
            g = temp - 60;
            g = 288.1221695283 * Math.pow(g, -0.0755148492);
            g = Utils.clamp(g, 0, 255);
        }
        
        // Blue
        if (temp >= 66) {
            b = 255;
        } else if (temp <= 19) {
            b = 0;
        } else {
            b = temp - 10;
            b = 138.5177312231 * Math.log(b) - 305.0447927307;
            b = Utils.clamp(b, 0, 255);
        }
        
        return [r / 255, g / 255, b / 255];
    },
    
    // FPS counter
    FPSCounter: class {
        constructor() {
            this.fps = 0;
            this.frames = 0;
            this.lastTime = performance.now();
        }
        
        update() {
            this.frames++;
            const currentTime = performance.now();
            const elapsed = currentTime - this.lastTime;
            
            if (elapsed >= 1000) {
                this.fps = Math.round((this.frames * 1000) / elapsed);
                this.frames = 0;
                this.lastTime = currentTime;
            }
            
            return this.fps;
        }
    }
};
