# app.py
"""
Servidor Flask para simulación N-body - CORREGIDO
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import threading
import time
from physics.nbody import NBodySimulator
from physics.constants import SCALE_FACTORS
from visualization.sphere_generator import ProceduralSphere

app = Flask(__name__)
app.config['SECRET_KEY'] = 'solar-system-secret-key-2025'

# CORRECCIÓN: Configuración correcta de SocketIO
socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    async_mode='threading',
    logger=False,
    engineio_logger=False
)
CORS(app)

# Variables globales
simulator = None
simulation_thread = None
simulation_running = False
simulation_lock = threading.Lock()

def initialize_simulation():
    """Inicializa el simulador con el sistema solar"""
    global simulator
    with simulation_lock:
        simulator = NBodySimulator(time_step=3600, method='verlet')
        simulator.initialize_solar_system()
        print(f"✅ Simulación inicializada con {len(simulator.bodies)} cuerpos celestes")
    return simulator

def simulation_loop():
    """Loop principal de simulación - CORREGIDO"""
    global simulation_running, simulator
    
    print("🚀 Loop de simulación iniciado")
    
    frame_count = 0
    last_update_time = time.time()
    
    while simulation_running:
        try:
            with simulation_lock:
                if simulator is None:
                    break
                
                # Ejecutar paso de física
                simulator.step()
                frame_count += 1
                
                # Enviar actualización cada 5 frames
                if frame_count % 5 == 0:
                    state = simulator.get_state()
                    energy = simulator.compute_energy()
                    
                    # Calcular FPS
                    current_time = time.time()
                    elapsed = current_time - last_update_time
                    fps = 5 / elapsed if elapsed > 0 else 0
                    last_update_time = current_time
                    
                    # CORRECCIÓN: Usar socketio.emit sin broadcast
                    socketio.emit('simulation_update', {
                        'state': state,
                        'energy': energy,
                        'fps': round(fps, 1)
                    }, namespace='/')
            
            # Control de velocidad (~20 FPS)
            time.sleep(0.05)
            
        except Exception as e:
            print(f"❌ Error en simulation_loop: {e}")
            import traceback
            traceback.print_exc()
            simulation_running = False
            break
    
    print("🛑 Loop de simulación detenido")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/initialize', methods=['POST'])
def api_initialize():
    global simulator
    try:
        simulator = initialize_simulation()
        return jsonify({
            'status': 'success',
            'bodies': len(simulator.bodies)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/state', methods=['GET'])
def api_state():
    global simulator
    if simulator is None:
        return jsonify({'status': 'error', 'message': 'Not initialized'}), 400
    
    with simulation_lock:
        state = simulator.get_state()
        energy = simulator.compute_energy()
    
    return jsonify({'status': 'success', 'state': state, 'energy': energy})

@app.route('/api/sphere_data', methods=['GET'])
def api_sphere_data():
    try:
        radius = float(request.args.get('radius', 1.0))
        segments = int(request.args.get('segments', 32))
        rings = int(request.args.get('rings', 16))
        
        sphere_data = ProceduralSphere.generate_sphere_vertices(
            radius=radius, segments=segments, rings=rings
        )
        return jsonify({'status': 'success', 'data': sphere_data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# ==================== WebSocket Events ====================

@socketio.on('connect')
def handle_connect():
    print(f"🔌 Cliente conectado: {request.sid}")
    emit('connection_response', {'status': 'connected'})
    
    if simulator is not None:
        with simulation_lock:
            state = simulator.get_state()
            energy = simulator.compute_energy()
        emit('simulation_update', {'state': state, 'energy': energy, 'fps': 0})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"🔌 Cliente desconectado: {request.sid}")

@socketio.on('start_simulation')
def handle_start_simulation(data=None):
    global simulation_running, simulation_thread, simulator
    
    print("▶️ Iniciando simulación")
    
    try:
        if simulator is None:
            simulator = initialize_simulation()
        
        if not simulation_running:
            simulation_running = True
            simulation_thread = threading.Thread(target=simulation_loop, daemon=True)
            simulation_thread.start()
            
            # CORRECCIÓN: emit a todos los clientes conectados
            socketio.emit('simulation_status', {
                'status': 'started',
                'message': 'Simulación iniciada'
            }, namespace='/')
            print("✅ Simulación iniciada")
        else:
            emit('simulation_status', {
                'status': 'already_running'
            })
    
    except Exception as e:
        print(f"❌ Error: {e}")
        emit('simulation_status', {'status': 'error', 'message': str(e)})

@socketio.on('stop_simulation')
def handle_stop_simulation():
    global simulation_running
    
    print("⏸️ Pausando simulación")
    simulation_running = False
    
    socketio.emit('simulation_status', {
        'status': 'stopped'
    }, namespace='/')

@socketio.on('reset_simulation')
def handle_reset_simulation():
    global simulator, simulation_running
    
    print("🔄 Reiniciando simulación")
    
    was_running = simulation_running
    simulation_running = False
    time.sleep(0.1)
    
    simulator = initialize_simulation()
    
    socketio.emit('simulation_status', {
        'status': 'reset'
    }, namespace='/')
    
    if was_running:
        handle_start_simulation()

@socketio.on('set_time_scale')
def handle_time_scale(data):
    global simulator
    
    if simulator is None:
        emit('error', {'message': 'No inicializada'})
        return
    
    try:
        scale = float(data.get('scale', 1.0))
        
        with simulation_lock:
            simulator.time_step = 3600 * scale
        
        socketio.emit('time_scale_updated', {
            'scale': scale,
            'time_step': simulator.time_step
        }, namespace='/')
        
        print(f"⏱️ Escala: {scale}x")
    
    except Exception as e:
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    print("=" * 60)
    print("🌌 SISTEMA SOLAR N-BODY")
    print("=" * 60)
    print("📡 http://localhost:5000")
    print("=" * 60)
    
    initialize_simulation()
    
    # CORRECCIÓN: Sin allow_unsafe_werkzeug
    socketio.run(
        app,
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=False
    )