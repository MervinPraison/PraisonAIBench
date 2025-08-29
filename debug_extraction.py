#!/usr/bin/env python3

import json
import re

# Sample JSON data from your provided content
json_data = [
    {
        "test_name": "rotating_cube_simulation",
        "response": """I'll create a complete HTML file with a rotating 3D cube using Three.js. Here's the code:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rotating 3D Cube - Three.js</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            font-family: Arial, sans-serif;
        }
        
        #container {
            position: relative;
            width: 100vw;
            height: 100vh;
        }
        
        #info {
            position: absolute;
            top: 10px;
            left: 10px;
            color: white;
            font-size: 14px;
            z-index: 100;
            background: rgba(0, 0, 0, 0.5);
            padding: 10px;
            border-radius: 5px;
        }
        
        canvas {
            display: block;
        }
    </style>
</head>
<body>
    <div id="container">
        <div id="info">
            <h3>Interactive 3D Rotating Cube</h3>
            <p>🖱️ Left click + drag: Rotate view</p>
            <p>🖱️ Right click + drag: Pan</p>
            <p>🖱️ Scroll: Zoom in/out</p>
        </div>
    </div>

    <!-- Three.js CDN -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <!-- OrbitControls for camera interaction -->
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

    <script>
        // Scene setup
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        document.getElementById('container').appendChild(renderer.domElement);

        // Create cube geometry
        const geometry = new THREE.BoxGeometry(2, 2, 2);
        
        // Create materials for each face with different colors
        const materials = [
            new THREE.MeshLambertMaterial({ color: 0xff0000 }), // Right face - Red
            new THREE.MeshLambertMaterial({ color: 0x00ff00 }), // Left face - Green
            new THREE.MeshLambertMaterial({ color: 0x0000ff }), // Top face - Blue
            new THREE.MeshLambertMaterial({ color: 0xffff00 }), // Bottom face - Yellow
            new THREE.MeshLambertMaterial({ color: 0xff00ff }), // Front face - Magenta
            new THREE.MeshLambertMaterial({ color: 0x00ffff })  // Back face - Cyan
        ];
        
        // Create cube mesh
        const cube = new THREE.Mesh(geometry, materials);
        cube.castShadow = true;
        cube.receiveShadow = true;
        scene.add(cube);

        // Add ambient light for overall illumination
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        scene.add(ambientLight);

        // Add directional light for shadows and highlights
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(5, 5, 5);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        directionalLight.shadow.camera.near = 0.5;
        directionalLight.shadow.camera.far = 500;
        scene.add(directionalLight);

        // Add point light for additional lighting effects
        const pointLight = new THREE.PointLight(0xffffff, 0.5, 100);
        pointLight.position.set(-5, -5, -5);
        scene.add(pointLight);

        // Add a ground plane to receive shadows
        const planeGeometry = new THREE.PlaneGeometry(10, 10);
        const planeMaterial = new THREE.MeshLambertMaterial({ 
            color: 0x808080,
            transparent: true,
            opacity: 0.5
        });
        const plane = new THREE.Mesh(planeGeometry, planeMaterial);
        plane.rotation.x = -Math.PI / 2;
        plane.position.y = -2;
        plane.receiveShadow = true;
        scene.add(plane);

        // Set camera position
        camera.position.set(5, 5, 5);
        camera.lookAt(0, 0, 0);

        // Add OrbitControls for user interaction
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.25;
        controls.enableZoom = true;
        controls.enablePan = true;
        controls.enableRotate = true;
        controls.autoRotate = false;
        controls.maxDistance = 20;
        controls.minDistance = 2;

        // Animation variables
        let rotationSpeed = 0.01;
        let time = 0;

        // Animation loop
        function animate() {
            requestAnimationFrame(animate);
            
            time += 0.01;
            
            // Rotate the cube
            cube.rotation.x += rotationSpeed;
            cube.rotation.y += rotationSpeed * 1.5;
            cube.rotation.z += rotationSpeed * 0.5;
            
            // Add subtle floating motion
            cube.position.y = Math.sin(time) * 0.2;
            
            // Update controls
            controls.update();
            
            // Render the scene
            renderer.render(scene, camera);
        }

        // Handle window resize
        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }

        window.addEventListener('resize', onWindowResize, false);

        // Add keyboard controls for rotation speed
        document.addEventListener('keydown', function(event) {
            switch(event.code) {
                case 'ArrowUp':
                case 'KeyW':
                    rotationSpeed = Math.min(rotationSpeed + 0.002, 0.05);
                    break;
                case 'ArrowDown':
                case 'KeyS':
                    rotationSpeed = Math.max(rotationSpeed - 0.002, 0.001);
                    break;
                case 'Space':
                    rotationSpeed = rotationSpeed > 0 ? 0 : 0.01;
                    event.preventDefault();
                    break;
            }
        });

        // Add some visual flair with particle effects
        function createStars() {
            const starsGeometry = new THREE.BufferGeometry();
            const starsMaterial = new THREE.PointsMaterial({
                color: 0xffffff,
                size: 0.1,
                transparent: true,
                opacity: 0.8
            });

            const starsVertices = [];
            for (let i = 0; i < 1000; i++) {
                const x = (Math.random() - 0.5) * 200;
                const y = (Math.random() - 0.5) * 200;
                const z = (Math.random() - 0.5) * 200;
                starsVertices.push(x, y, z);
            }

            starsGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starsVertices, 3));
            const stars = new THREE.Points(starsGeometry, starsMaterial);
            scene.add(stars);
        }

        // Initialize stars
        createStars();

        // Start the animation
        animate();

        // Add instructions update
        setTimeout(() => {
            const info = document.getElementById('info');
            info.innerHTML += '<p><small>⌨️ W/S or ↑/↓: Speed up/down rotation</small></p>';
            info.innerHTML += '<p><small>⌨️ Space: Pause/Resume rotation</small></p>';
        }, 2000);
    </script>
</body>
</html>
```

This HTML file creates a complete Three.js scene with:

## Features:
1. **Rotating 3D Cube**: Each face has a different color (red, green, blue, yellow, magenta, cyan)
2. **Continuous Rotation**: The cube rotates automatically on multiple axes with subtle floating motion
3. **Proper Lighting**: 
   - Ambient light for overall illumination
   - Directional light with shadows
   - Point light for additional effects
4. **Interactive Camera Controls**:
   - Left click + drag: Rotate view
   - Right click + drag: Pan
   - Mouse wheel: Zoom in/out
5. **Additional Features**:
   - Ground plane with shadows
   - Starfield background
   - Keyboard controls (W/S for speed, Space to pause)
   - Responsive design
   - Informational overlay

## Technical Details:
- Self-contained HTML file
- Three.js loaded from CDN
- OrbitControls for smooth camera interaction
- Shadow mapping enabled
- Anti-aliasing for smooth edges
- Responsive to window resizing

Save this code as `rotating_cube.html` and open it in any modern web browser to see the interactive 3D rotating cube in action!""",
        "model": "anthropic/claude-sonnet-4-20250514"
    },
    {
        "test_name": "particle_system_simulation", 
        "response": """I'll create a comprehensive particle system with Three.js that includes multiple effects and interactive mouse controls. Here's the complete HTML file:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Particle System</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
            font-family: Arial, sans-serif;
        }
        
        canvas {
            display: block;
            cursor: crosshair;
        }
        
        .controls {
            position: absolute;
            top: 20px;
            left: 20px;
            color: white;
            z-index: 100;
            background: rgba(0, 0, 0, 0.7);
            padding: 15px;
            border-radius: 10px;
            font-size: 14px;
        }
        
        .controls button {
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            padding: 8px 15px;
            margin: 5px;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .controls button:hover {
            background: rgba(255, 255, 255, 0.4);
            transform: scale(1.05);
        }
        
        .controls button.active {
            background: rgba(100, 200, 255, 0.6);
            border-color: rgba(100, 200, 255, 0.8);
        }
        
        .info {
            position: absolute;
            bottom: 20px;
            right: 20px;
            color: rgba(255, 255, 255, 0.7);
            background: rgba(0, 0, 0, 0.5);
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="controls">
        <div><strong>Particle Effects</strong></div>
        <button id="fountain" class="active">Fountain</button>
        <button id="explosion">Explosion</button>
        <button id="flow">Flow Stream</button>
        <button id="spiral">Spiral</button>
        <br>
        <div style="margin-top: 10px;">Move mouse to interact!</div>
    </div>
    
    <div class="info">
        <div>Particles: <span id="particleCount">2000</span></div>
        <div>FPS: <span id="fps">60</span></div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        // TRUNCATED - This response was cut off in the JSON
        if (particlePositions[i3 + 2] > 15) {
            particlePositions[i3 + 2] = -15;
            particlePositions[i3 + 1] = Math.random() *""",
        "model": "anthropic/claude-sonnet-4-20250514"
    }
]

def test_html_extraction():
    html_pattern = r'```html\s*\n(.*?)\n```'
    
    for i, item in enumerate(json_data):
        print(f"\n=== Testing Response {i+1}: {item['test_name']} ===")
        response = item['response']
        
        # Check for HTML code blocks
        matches = re.findall(html_pattern, response, re.DOTALL | re.IGNORECASE)
        
        print(f"HTML blocks found: {len(matches)}")
        
        if matches:
            html_content = matches[0].strip()
            print(f"HTML content length: {len(html_content)} characters")
            print(f"Starts with: {html_content[:50]}...")
            print(f"Ends with: ...{html_content[-50:]}")
        else:
            print("❌ No complete HTML blocks found")
            
            # Check if there's a starting ```html but no closing ```
            if '```html' in response:
                print("⚠️  Found ```html start but no complete block")
                start_pos = response.find('```html')
                remaining = response[start_pos:]
                if '```' not in remaining[7:]:  # Skip the opening ```html
                    print("⚠️  Missing closing ``` - response appears truncated")

if __name__ == "__main__":
    test_html_extraction()
