// static/js/main.js
// MEJORADO: Controles de velocidad preestablecidos

let socket;
let renderer;
let isSimulationRunning = false;
let currentTimeScale = 1.0;

document.addEventListener('DOMContentLoaded', () => {
    console.log('🌌 Inicializando Sistema Solar N-Body');
    
    renderer = new SolarSystemRenderer('canvas-container');
    
    initializeWebSocket();
    setupUIControls();
    
    setTimeout(() => {
        const loading = document.getElementById('loading');
        if (loading) {
            loading.style.opacity = '0';
            setTimeout(() => loading.remove(), 500);
        }
    }, 2000);
});

function initializeWebSocket() {
    socket = io({
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionAttempts: 5
    });
    
    socket.on('connect', () => {
        console.log('✅ Conectado al servidor');
        updateStatus('Conectado', '#0f0');
        socket.emit('start_simulation');
    });
    
    socket.on('disconnect', () => {
        console.log('❌ Desconectado');
        updateStatus('Desconectado', '#f00');
    });
    
    socket.on('connection_response', (data) => {
        console.log('📡', data.message);
    });
    
    socket.on('simulation_update', (data) => {
        if (data.state && data.state.bodies) {
            renderer.updateBodies(data.state.bodies);
        }
        updateStats(data);
    });
    
    socket.on('simulation_status', (data) => {
        console.log('📊', data.status);
        
        if (data.status === 'started' || data.status === 'already_running') {
            isSimulationRunning = true;
            document.getElementById('startBtn').textContent = '▶️ Corriendo';
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
        } else if (data.status === 'stopped') {
            isSimulationRunning = false;
            document.getElementById('startBtn').textContent = '▶️ Iniciar';
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
        }
    });
    
    socket.on('time_scale_updated', (data) => {
        console.log(`⏱️ Escala: ${data.scale}x`);
        currentTimeScale = data.scale;
    });
    
    socket.on('error', (data) => {
        console.error('❌ Error:', data.message);
    });
}

function setupUIControls() {
    // Botones básicos
    document.getElementById('startBtn').addEventListener('click', () => {
        socket.emit('start_simulation');
    });
    
    document.getElementById('stopBtn').addEventListener('click', () => {
        socket.emit('stop_simulation');
    });
    
    document.getElementById('resetBtn').addEventListener('click', () => {
        if (confirm('¿Reiniciar simulación?')) {
            socket.emit('reset_simulation');
        }
    });
    
    // MEJORADO: Botones de velocidad preestablecidos
    document.querySelectorAll('.speed-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const speed = parseFloat(e.target.dataset.speed);
            setTimeScale(speed);
            
            // Actualizar botón activo
            document.querySelectorAll('.speed-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
        });
    });
    
    // Slider de velocidad
    const timeScaleSlider = document.getElementById('timeScale');
    timeScaleSlider.addEventListener('input', (e) => {
        const scale = parseFloat(e.target.value);
        setTimeScale(scale);
        
        // Desactivar todos los botones
        document.querySelectorAll('.speed-btn').forEach(b => b.classList.remove('active'));
    });
    
    // Checkboxes
    document.getElementById('showTrails')?.addEventListener('change', (e) => {
        renderer.setTrailsVisible(e.target.checked);
    });
    
    document.getElementById('showLabels')?.addEventListener('change', (e) => {
        renderer.setLabelsVisible(e.target.checked);
    });
    
    // NUEVO: Botón de reset de cámara
    document.getElementById('resetCameraBtn')?.addEventListener('click', () => {
        renderer.resetCamera();
    });
}

function setTimeScale(scale) {
    socket.emit('set_time_scale', { scale: scale });
    document.getElementById('speedValue').textContent = scale.toFixed(1);
    document.getElementById('timeScale').value = scale;
}

function updateStats(data) {
    if (data.state && data.state.time !== undefined) {
        const days = (data.state.time / 86400).toFixed(1);
        const years = (days / 365.25).toFixed(2);
        document.getElementById('simTime').textContent = `${days} días (${years} años)`;
    }
    
    if (data.energy) {
        if (data.energy.total !== undefined) {
            document.getElementById('totalEnergy').textContent = data.energy.total.toExponential(2) + ' J';
        }
        if (data.energy.kinetic !== undefined) {
            document.getElementById('kineticEnergy').textContent = data.energy.kinetic.toExponential(2) + ' J';
        }
        if (data.energy.potential !== undefined) {
            document.getElementById('potentialEnergy').textContent = data.energy.potential.toExponential(2) + ' J';
        }
    }
    
    if (data.fps !== undefined) {
        document.getElementById('fps').textContent = data.fps;
    }
}

function updateStatus(message, color) {
    const statusElement = document.getElementById('connectionStatus');
    if (statusElement) {
        statusElement.textContent = message;
        statusElement.style.color = color;
    }
}

window.addEventListener('error', (event) => {
    console.error('❌ Error global:', event.error);
});

window.addEventListener('beforeunload', () => {
    if (socket && socket.connected) {
        socket.disconnect();
    }
});
