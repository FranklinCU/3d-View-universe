// static/js/renderer.js
// MEJORADO: Cámara suave, estelas que se desvanecen

class SolarSystemRenderer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.bodies = new Map();
        this.trails = new Map();
        this.labels = new Map();
        this.rings = new Map();
        this.labelsVisible = true;
        this.trailsVisible = true;
        
        // Sistema de estelas con desvanecimiento
        this.trailHistory = new Map();
        this.trailMaxAge = 30000; // 30 segundos antes de empezar a desvanecer
        this.maxTrailPoints = 500;
        
        this.init();
    }
    
    init() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x000000);
        
        const aspect = window.innerWidth / window.innerHeight;
        this.camera = new THREE.PerspectiveCamera(60, aspect, 0.1, 50000);
        this.camera.position.set(400, 300, 400);
        this.camera.lookAt(0, 0, 0);
        
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true,
            alpha: true
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.container.appendChild(this.renderer.domElement);
        
        // MEJORADO: Controles de cámara más suaves
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.08; // Más suave
        this.controls.rotateSpeed = 0.6;
        this.controls.zoomSpeed = 1.2;
        this.controls.panSpeed = 0.8;
        this.controls.minDistance = 20;
        this.controls.maxDistance = 3000;
        this.controls.target.set(0, 0, 0);
        this.controls.enablePan = true;
        this.controls.screenSpacePanning = true;
        
        // Límites verticales para evitar giros extraños
        this.controls.maxPolarAngle = Math.PI * 0.95;
        this.controls.minPolarAngle = Math.PI * 0.05;
        
        this.setupLighting();
        this.createFixedStarField();
        this.createReferenceGrid();
        
        window.addEventListener('resize', () => this.onWindowResize());
        
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        this.renderer.domElement.addEventListener('click', (e) => this.onMouseClick(e));
        
        // Doble click para resetear cámara
        this.renderer.domElement.addEventListener('dblclick', () => this.resetCamera());
        
        this.animate();
        
        console.log('✨ Renderizador inicializado (cámara mejorada + estelas con fade)');
    }
    
    setupLighting() {
        const ambientLight = new THREE.AmbientLight(0x111111, 0.5);
        this.scene.add(ambientLight);
    }
    
    createFixedStarField() {
        const starsGeometry = new THREE.BufferGeometry();
        const starVertices = [];
        const starColors = [];
        
        for (let i = 0; i < 25000; i++) {
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.acos(2 * Math.random() - 1);
            const radius = 3500 + Math.random() * 2500;
            
            const x = radius * Math.sin(phi) * Math.cos(theta);
            const y = radius * Math.sin(phi) * Math.sin(theta);
            const z = radius * Math.cos(phi);
            
            starVertices.push(x, y, z);
            
            const brightness = 0.7 + Math.random() * 0.3;
            starColors.push(brightness, brightness * 0.95, brightness * 0.9);
        }
        
        starsGeometry.setAttribute('position', 
            new THREE.Float32BufferAttribute(starVertices, 3)
        );
        starsGeometry.setAttribute('color',
            new THREE.Float32BufferAttribute(starColors, 3)
        );
        
        const starsMaterial = new THREE.PointsMaterial({
            size: 1.5,
            vertexColors: true,
            transparent: true,
            opacity: 0.9,
            sizeAttenuation: true
        });
        
        const starField = new THREE.Points(starsGeometry, starsMaterial);
        starField.frustumCulled = false;
        this.scene.add(starField);
    }
    
    createReferenceGrid() {
        const gridHelper = new THREE.GridHelper(1500, 60, 0x003300, 0x001100);
        gridHelper.position.y = 0;
        this.scene.add(gridHelper);
        
        const axesHelper = new THREE.AxesHelper(300);
        this.scene.add(axesHelper);
    }
    
    createProceduralBody(bodyData) {
        const { name, radius, color, emissive, gradient } = bodyData;
        
        let visualRadius = radius;
        if (emissive && radius > 5) {
            visualRadius = 6 + Math.log(radius) * 2;
        }
        
        const geometry = new THREE.IcosahedronGeometry(visualRadius, 5);
        
        const material = new THREE.ShaderMaterial({
            uniforms: {
                color: { value: new THREE.Color(...color) },
                colorGradient: { 
                    value: gradient ? [
                        new THREE.Color(gradient[0], gradient[1], gradient[2]),
                        new THREE.Color(gradient[3], gradient[4], gradient[5])
                    ] : [new THREE.Color(...color), new THREE.Color(...color)]
                },
                emissive: { value: emissive ? 1.0 : 0.0 },
                time: { value: 0.0 },
                sunPosition: { value: new THREE.Vector3(0, 0, 0) }
            },
            vertexShader: `
                varying vec3 vNormal;
                varying vec3 vPosition;
                varying vec3 vWorldPosition;
                
                void main() {
                    vNormal = normalize(normalMatrix * normal);
                    vPosition = position;
                    vec4 worldPosition = modelMatrix * vec4(position, 1.0);
                    vWorldPosition = worldPosition.xyz;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                uniform vec3 color;
                uniform vec3 colorGradient[2];
                uniform float emissive;
                uniform float time;
                uniform vec3 sunPosition;
                
                varying vec3 vNormal;
                varying vec3 vPosition;
                varying vec3 vWorldPosition;
                
                float noise(vec3 p) {
                    return fract(
                        sin(dot(p, vec3(12.9898, 78.233, 45.164))) * 43758.5453 +
                        sin(dot(p, vec3(93.989, 67.345, 12.989))) * 28618.2341
                    );
                }
                
                float fractalNoise(vec3 p) {
                    float value = 0.0;
                    float amplitude = 1.0;
                    float frequency = 1.0;
                    
                    for(int i = 0; i < 5; i++) {
                        value += amplitude * noise(p * frequency);
                        amplitude *= 0.5;
                        frequency *= 2.0;
                    }
                    
                    return value;
                }
                
                void main() {
                    vec3 lightDir = normalize(sunPosition - vWorldPosition);
                    float diffuse = max(0.0, dot(vNormal, lightDir));
                    
                    float gradientX = (vPosition.x + 1.0) * 0.5;
                    float gradientY = (vPosition.y + 1.0) * 0.5;
                    float gradientZ = (vPosition.z + 1.0) * 0.5;
                    float gradientMix = (gradientX + gradientY + gradientZ) / 3.0;
                    
                    vec3 baseColor = mix(colorGradient[0], colorGradient[1], gradientMix);
                    
                    float pattern = fractalNoise(vPosition * 3.0 + time * 0.03);
                    pattern = pattern * 0.25 + 0.75;
                    
                    vec3 finalColor = baseColor * pattern;
                    
                    if (emissive > 0.5) {
                        finalColor += baseColor * 0.9;
                        finalColor = finalColor * (1.0 + sin(time * 1.5) * 0.15);
                    } else {
                        finalColor = finalColor * (0.35 + diffuse * 0.65);
                        
                        vec3 viewDir = normalize(cameraPosition - vWorldPosition);
                        vec3 reflectDir = reflect(-lightDir, vNormal);
                        float spec = pow(max(dot(viewDir, reflectDir), 0.0), 16.0);
                        finalColor += vec3(spec * 0.3);
                    }
                    
                    gl_FragColor = vec4(finalColor, 1.0);
                }
            `
        });
        
        const mesh = new THREE.Mesh(geometry, material);
        mesh.userData.bodyName = name;
        mesh.userData.originalRadius = radius;
        mesh.userData.bodyData = bodyData;
        
        if (emissive) {
            const light = new THREE.PointLight(0xffffaa, 2.5, 8000);
            mesh.add(light);
        }
        
        return mesh;
    }
    
    createRings(planetMesh, ringData) {
        const planetRadius = planetMesh.userData.originalRadius;
        const innerRadius = planetRadius * ringData.inner_radius;
        const outerRadius = planetRadius * ringData.outer_radius;
        
        const geometry = new THREE.RingGeometry(innerRadius, outerRadius, 128, 8);
        
        const material = new THREE.MeshBasicMaterial({
            color: new THREE.Color(...ringData.color),
            side: THREE.DoubleSide,
            transparent: true,
            opacity: ringData.opacity || 0.7
        });
        
        const ringMesh = new THREE.Mesh(geometry, material);
        ringMesh.rotation.x = Math.PI / 2;
        
        return ringMesh;
    }
    
    createLabel(name) {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 512;
        canvas.height = 128;
        
        context.fillStyle = 'rgba(0, 20, 0, 0.85)';
        context.fillRect(0, 0, canvas.width, canvas.height);
        
        context.strokeStyle = '#0f0';
        context.lineWidth = 4;
        context.strokeRect(0, 0, canvas.width, canvas.height);
        
        context.font = 'Bold 48px Arial';
        context.fillStyle = '#0f0';
        context.textAlign = 'center';
        context.textBaseline = 'middle';
        context.fillText(name, canvas.width / 2, canvas.height / 2);
        
        const texture = new THREE.CanvasTexture(canvas);
        const spriteMaterial = new THREE.SpriteMaterial({ 
            map: texture,
            transparent: true,
            depthTest: false,
            depthWrite: false
        });
        const sprite = new THREE.Sprite(spriteMaterial);
        sprite.scale.set(10, 2.5, 1);
        
        return sprite;
    }
    
    updateBodies(bodies) {
        const currentTime = Date.now();
        
        bodies.forEach(bodyData => {
            const { name, position, radius, color, emissive } = bodyData;
            
            if (!this.bodies.has(name)) {
                const mesh = this.createProceduralBody(bodyData);
                this.bodies.set(name, mesh);
                this.scene.add(mesh);
                
                if (bodyData.has_rings && bodyData.rings) {
                    const rings = this.createRings(mesh, bodyData.rings);
                    mesh.add(rings);
                    this.rings.set(name, rings);
                    console.log(`✅ Anillos añadidos a ${name}`);
                }
                
                const label = this.createLabel(name);
                this.labels.set(name, label);
                this.scene.add(label);
                
                // Inicializar historial con timestamps
                this.trailHistory.set(name, []);
                
                console.log(`🪐 ${name} creado`);
            }
            
            const mesh = this.bodies.get(name);
            mesh.position.set(position[0], position[1], position[2]);
            
            const label = this.labels.get(name);
            if (label) {
                const offset = mesh.userData.originalRadius * 1.8 + 4;
                label.position.set(
                    position[0],
                    position[1] + offset,
                    position[2]
                );
                label.visible = this.labelsVisible;
            }
            
            if (mesh.material.uniforms) {
                mesh.material.uniforms.time.value += 0.015;
                mesh.material.uniforms.sunPosition.value.set(0, 0, 0);
            }
            
            // SISTEMA DE ESTELAS CON DESVANECIMIENTO
            if (!emissive) {
                const history = this.trailHistory.get(name);
                
                // Agregar nuevo punto con timestamp
                history.push({
                    position: new THREE.Vector3(position[0], position[1], position[2]),
                    timestamp: currentTime
                });
                
                // Eliminar puntos muy antiguos
                const fadeStartTime = currentTime - this.trailMaxAge;
                while (history.length > 0 && history[0].timestamp < fadeStartTime - 10000) {
                    history.shift();
                }
                
                // Limitar puntos totales
                if (history.length > this.maxTrailPoints) {
                    history.shift();
                }
                
                // Crear o actualizar línea
                if (!this.trails.has(name)) {
                    const trailGeometry = new THREE.BufferGeometry();
                    const trailMaterial = new THREE.LineBasicMaterial({
                        vertexColors: true,
                        transparent: true,
                        linewidth: 2
                    });
                    const trailLine = new THREE.Line(trailGeometry, trailMaterial);
                    this.trails.set(name, trailLine);
                    this.scene.add(trailLine);
                }
                
                const trailLine = this.trails.get(name);
                
                if (history.length > 1) {
                    const positions = [];
                    const colors = [];
                    
                    history.forEach((point, index) => {
                        positions.push(point.position.x, point.position.y, point.position.z);
                        
                        // Calcular alpha basado en edad y posición en la cola
                        const age = currentTime - point.timestamp;
                        const ageAlpha = Math.max(0, 1 - (age / this.trailMaxAge));
                        const positionAlpha = index / history.length;
                        const finalAlpha = ageAlpha * positionAlpha * 0.9;
                        
                        colors.push(finalAlpha, finalAlpha, finalAlpha);
                    });
                    
                    trailLine.geometry.setAttribute(
                        'position',
                        new THREE.Float32BufferAttribute(positions, 3)
                    );
                    trailLine.geometry.setAttribute(
                        'color',
                        new THREE.Float32BufferAttribute(colors, 3)
                    );
                    
                    trailLine.geometry.attributes.position.needsUpdate = true;
                    trailLine.geometry.attributes.color.needsUpdate = true;
                    trailLine.visible = this.trailsVisible;
                }
            }
        });
    }
    
    setLabelsVisible(visible) {
        this.labelsVisible = visible;
        this.labels.forEach(label => {
            label.visible = visible;
        });
    }
    
    setTrailsVisible(visible) {
        this.trailsVisible = visible;
        this.trails.forEach(trail => {
            trail.visible = visible;
        });
    }
    
    resetCamera() {
        // Resetear cámara a posición inicial
        const targetPos = new THREE.Vector3(400, 300, 400);
        const targetLookAt = new THREE.Vector3(0, 0, 0);
        
        const duration = 1000;
        const start = Date.now();
        const startPos = this.camera.position.clone();
        const startTarget = this.controls.target.clone();
        
        const animate = () => {
            const elapsed = Date.now() - start;
            const progress = Math.min(elapsed / duration, 1);
            const easeProgress = 1 - Math.pow(1 - progress, 3);
            
            this.camera.position.lerpVectors(startPos, targetPos, easeProgress);
            this.controls.target.lerpVectors(startTarget, targetLookAt, easeProgress);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        animate();
        console.log('📷 Cámara reseteada (doble click)');
    }
    
    onMouseClick(event) {
        this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        this.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
        
        this.raycaster.setFromCamera(this.mouse, this.camera);
        const meshes = Array.from(this.bodies.values());
        const intersects = this.raycaster.intersectObjects(meshes);
        
        if (intersects.length > 0) {
            const clickedMesh = intersects[0].object;
            const bodyName = clickedMesh.userData.bodyName;
            console.log(`🖱️ Clic en: ${bodyName}`);
            this.focusOnBody(bodyName);
        }
    }
    
    focusOnBody(bodyName) {
        const mesh = this.bodies.get(bodyName);
        if (!mesh) return;
        
        const targetPos = mesh.position.clone();
        const distance = mesh.userData.originalRadius * 5 + 40;
        
        const duration = 1500;
        const start = Date.now();
        const startPos = this.camera.position.clone();
        const startTarget = this.controls.target.clone();
        
        const animate = () => {
            const elapsed = Date.now() - start;
            const progress = Math.min(elapsed / duration, 1);
            const easeProgress = 1 - Math.pow(1 - progress, 3);
            
            this.camera.position.lerpVectors(
                startPos,
                new THREE.Vector3(
                    targetPos.x + distance,
                    targetPos.y + distance * 0.7,
                    targetPos.z + distance
                ),
                easeProgress
            );
            
            this.controls.target.lerpVectors(startTarget, targetPos, easeProgress);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        animate();
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }
    
    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }
}
