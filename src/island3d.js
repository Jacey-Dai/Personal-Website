// Real-time version of the storybook island: the same Blender scene exported by
// tools/export_island_glb.py, lit like direction A, and orbited by dragging.
// It only draws while something moves (drag, inertia, a turning tween, a flag rising).
import {
  BufferAttribute,
  BufferGeometry,
  Color,
  CylinderGeometry,
  DirectionalLight,
  DoubleSide,
  Group,
  HemisphereLight,
  MathUtils,
  Mesh,
  MeshStandardMaterial,
  PCFSoftShadowMap,
  PerspectiveCamera,
  Scene,
  ShaderMaterial,
  Spherical,
  Vector3,
  WebGLRenderer,
  AgXToneMapping,
  SRGBColorSpace,
} from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { DRACOLoader } from "three/examples/jsm/loaders/DRACOLoader.js";

const base = import.meta.env.BASE_URL;
// Blender is Z-up; glTF is Y-up: (x, y, z) -> (x, z, -y).
const fromBlender = (x, y, z) => new Vector3(x, z, -y);
const TARGET = fromBlender(0, -1, 1);
// The painted render's camera sat at Blender (20, -30, 31): start from the same corner.
const START = new Spherical().setFromVector3(
  fromBlender(20, -30, 31).sub(TARGET),
);
const POLAR = [MathUtils.degToRad(18), MathUtils.degToRad(72)];
const ZOOM = [0.55, 1.4];
const FOV = 26;

// Same coastline as tools/render_island.py.
const OUTLINE = Array.from({ length: 96 }, (_, i) => {
  const a = (i * Math.PI * 2) / 96;
  const r =
    1 +
    0.045 * Math.sin(3 * a) +
    0.03 * Math.cos(5 * a) +
    0.015 * Math.sin(11 * a);
  return [12.6 * r * Math.cos(a), 9.8 * r * Math.sin(a)];
});

const NOISE = /* glsl */ `
float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float vnoise(vec2 p){
  vec2 i = floor(p), f = fract(p); f = f*f*(3.0-2.0*f);
  return mix(mix(hash(i), hash(i+vec2(1,0)), f.x), mix(hash(i+vec2(0,1)), hash(i+vec2(1,1)), f.x), f.y);
}
float fbm(vec2 p){ float v = 0.0, a = 0.5; for (int i = 0; i < 4; i++){ v += a*vnoise(p); p *= 2.03; a *= 0.5; } return v; }
`;

function seaMaterial() {
  return new ShaderMaterial({
    transparent: true,
    depthWrite: false,
    side: DoubleSide,
    uniforms: {
      shallow: { value: new Color("#6fd0c4") },
      mid: { value: new Color("#2e98ad") },
      deep: { value: new Color("#2a6f9a") },
      glint: { value: new Color("#f3f7ec") },
    },
    vertexShader: /* glsl */ `
      varying vec2 vP;
      void main(){ vec4 w = modelMatrix * vec4(position, 1.0); vP = w.xz; gl_Position = projectionMatrix * viewMatrix * w; }`,
    fragmentShader: /* glsl */ `
      uniform vec3 shallow, mid, deep, glint;
      varying vec2 vP;
      ${NOISE}
      void main(){
        vec2 q = vec2(vP.x / 13.1, vP.y / 10.2);
        float d = length(q);
        float w = (d + 0.1 * fbm(q * 3.0 + 4.0)) ;
        vec3 c = mix(shallow, mid, smoothstep(1.04, 1.25, w));
        c = mix(c, deep, smoothstep(1.25, 1.6, w));
        float ripple = smoothstep(0.62, 0.9, fbm(vec2(vP.x * 0.35, vP.y * 1.1)));
        c = mix(c, glint, ripple * 0.12);
        gl_FragColor = vec4(c, 1.0 - smoothstep(1.22, 1.55, d));
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`,
  });
}

function foam() {
  const rows = [1.035, 1.055, 1.1];
  const n = OUTLINE.length;
  const pos = [];
  const edge = [];
  rows.forEach((s, r) =>
    OUTLINE.forEach(([x, y]) => {
      pos.push(...fromBlender(x * s, y * s, 0.2).toArray());
      edge.push(r === 1 ? 1 : 0);
    }),
  );
  const index = [];
  for (let r = 0; r < 2; r++)
    for (let i = 0; i < n; i++) {
      const a = r * n + i;
      const b = (r + 1) * n + i;
      const c = (r + 1) * n + ((i + 1) % n);
      const d = r * n + ((i + 1) % n);
      index.push(a, c, b, a, d, c);
    }
  const g = new BufferGeometry();
  g.setAttribute("position", new BufferAttribute(new Float32Array(pos), 3));
  g.setAttribute("edge", new BufferAttribute(new Float32Array(edge), 1));
  g.setIndex(index);
  const m = new ShaderMaterial({
    transparent: true,
    depthWrite: false,
    side: DoubleSide,
    uniforms: { tint: { value: new Color("#f6f3e6") } },
    vertexShader: /* glsl */ `
      attribute float edge; varying float vEdge; varying vec2 vP;
      void main(){ vEdge = edge; vP = position.xz; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
    fragmentShader: /* glsl */ `
      uniform vec3 tint; varying float vEdge; varying vec2 vP;
      ${NOISE}
      void main(){
        float a = vEdge * smoothstep(0.42, 0.6, fbm(vP * 1.2));
        gl_FragColor = vec4(tint, a * 0.95);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`,
  });
  return new Mesh(g, m);
}

const HSV = /* glsl */ `
uniform vec3 uHsv;
vec3 rgb2hsv(vec3 c){
  vec4 K = vec4(0.0, -1.0/3.0, 2.0/3.0, -1.0);
  vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
  vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
  float d = q.x - min(q.w, q.y); float e = 1.0e-10;
  return vec3(abs(q.z + (q.w - q.y) / (6.0*d + e)), d / (q.x + e), q.x);
}
vec3 hsv2rgb(vec3 c){
  vec3 p = abs(fract(c.xxx + vec3(1.0, 2.0/3.0, 1.0/3.0)) * 6.0 - 3.0);
  return c.z * mix(vec3(1.0), clamp(p - 1.0, 0.0, 1.0), c.y);
}
`;

// Blender's Hue/Saturation/Value node, which restyle() and tinted() put on the textures.
function applyHsv(material, [h, s, v]) {
  material.onBeforeCompile = (shader) => {
    shader.uniforms.uHsv = { value: new Vector3(h, s, v) };
    shader.fragmentShader = shader.fragmentShader
      .replace("void main() {", `${HSV}\nvoid main() {`)
      .replace(
        "#include <map_fragment>",
        `#include <map_fragment>
        { vec3 hsv = rgb2hsv(max(diffuseColor.rgb, 0.0));
          hsv.x = fract(hsv.x + uHsv.x - 0.5); hsv.y = clamp(hsv.y * uHsv.y, 0.0, 1.0); hsv.z *= uHsv.z;
          diffuseColor.rgb = hsv2rgb(hsv); }`,
      );
  };
  material.customProgramCacheKey = () => "hsv";
}

function flag(color) {
  const group = new Group();
  const pole = new Mesh(
    new CylinderGeometry(0.035, 0.035, 1.3, 8),
    new MeshStandardMaterial({ color: "#5c5144", roughness: 0.8 }),
  );
  pole.position.y = 0.65;
  const shape = new BufferGeometry();
  shape.setAttribute(
    "position",
    new BufferAttribute(
      new Float32Array([
        0, 1.28, 0, 0, 0.8, 0, 0.78, 1.08, 0, 0, 0.8, 0, 0.62, 0.92, 0, 0.78,
        1.08, 0,
      ]),
      3,
    ),
  );
  shape.computeVertexNormals();
  const pennant = new Mesh(
    shape,
    new MeshStandardMaterial({ color, roughness: 0.7, side: DoubleSide }),
  );
  pennant.position.x = 0.03;
  group.add(pole, pennant);
  group.userData.pennant = pennant;
  pole.castShadow = pennant.castShadow = true;
  return group;
}

function hull(points) {
  const pts = [...points].sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const cross = (o, a, b) =>
    (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const half = (list) => {
    const out = [];
    for (const p of list) {
      while (out.length >= 2 && cross(out.at(-2), out.at(-1), p) <= 0)
        out.pop();
      out.push(p);
    }
    out.pop();
    return out;
  };
  return [...half(pts), ...half(pts.reverse())];
}

export async function createIsland3D({
  plane,
  host,
  flagColors,
  reducedMotion,
  onChange,
  onDragStart,
}) {
  const renderer = new WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.outputColorSpace = SRGBColorSpace;
  renderer.toneMapping = AgXToneMapping;
  renderer.toneMappingExposure = 1.05;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = PCFSoftShadowMap;
  renderer.domElement.className = "island-canvas";

  const draco = new DRACOLoader().setDecoderPath(`${base}draco/`);
  const gltf = await new GLTFLoader()
    .setDRACOLoader(draco)
    .loadAsync(`${base}island/island.glb`);
  draco.dispose();

  const scene = new Scene();
  const camera = new PerspectiveCamera(FOV, 1, 0.5, 400);
  // Direction A: warm afternoon sun from the front left, cool sky fill.
  const sun = new DirectionalLight(new Color().setRGB(1, 0.9, 0.78), 3.4);
  sun.position.copy(fromBlender(-0.457, -0.586, 0.669).multiplyScalar(40));
  sun.castShadow = true;
  Object.assign(sun.shadow.camera, {
    left: -19,
    right: 19,
    top: 19,
    bottom: -19,
    near: 5,
    far: 90,
  });
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.bias = -0.0004;
  sun.shadow.normalBias = 0.03;
  sun.shadow.radius = 3;
  scene.add(
    sun,
    new HemisphereLight(
      new Color().setRGB(0.62, 0.74, 0.92),
      new Color("#b9a77f"),
      1.1,
    ),
  );

  const island = gltf.scene;
  island.traverse((o) => {
    if (!o.isMesh) return;
    const m = o.material;
    o.castShadow = !m.userData.glass;
    o.receiveShadow = true;
    if (m.userData.hsv && !m.userData.hsvApplied) {
      applyHsv(m, m.userData.hsv);
      m.userData.hsvApplied = true;
    }
    // AgX flattens saturation more than Blender's Punchy look; give plain colours some back.
    if (!m.map && !m.userData.glass && !m.userData.punchy) {
      const hsl = m.color.getHSL({});
      m.color.setHSL(hsl.h, Math.min(1, hsl.s * 1.25), hsl.l * 0.92);
      m.userData.punchy = true;
    }
    if (m.userData.glass) {
      m.transparent = true;
      m.depthWrite = false;
    }
    if (m.alphaTest) m.side = DoubleSide;
  });
  scene.add(island);
  const sea = new Mesh(
    new BufferGeometry().setFromPoints(
      [
        [-1, -1],
        [1, -1],
        [1, 1],
        [-1, -1],
        [1, 1],
        [-1, 1],
      ].map(([x, z]) => new Vector3(x * 45, 0.18, z * 37)),
    ),
    seaMaterial(),
  );
  sea.renderOrder = -1;
  scene.add(sea, foam());
  island.updateMatrixWorld(true);

  // Buildings: their glass (lit after a visit), a flag on the roof, and points for hit shapes.
  const buildings = {};
  island.traverse((o) => {
    const id = o.userData.place;
    if (!id) return;
    const glass = [];
    const points = [];
    const v = new Vector3();
    let top = -Infinity;
    const box = {
      minX: Infinity,
      maxX: -Infinity,
      minZ: Infinity,
      maxZ: -Infinity,
    };
    o.traverse((child) => {
      if (!child.isMesh) return;
      if (child.material.userData.glass) {
        child.material = child.material.clone();
        child.material.emissive = new Color("#ffc46e");
        child.material.emissiveIntensity = 0;
        glass.push(child.material);
      }
      const pos = child.geometry.attributes.position;
      const step = Math.max(1, Math.floor(pos.count / 60));
      for (let i = 0; i < pos.count; i += step) {
        v.fromBufferAttribute(pos, i).applyMatrix4(child.matrixWorld);
        points.push(v.clone());
        top = Math.max(top, v.y);
        box.minX = Math.min(box.minX, v.x);
        box.maxX = Math.max(box.maxX, v.x);
        box.minZ = Math.min(box.minZ, v.z);
        box.maxZ = Math.max(box.maxZ, v.z);
      }
    });
    const pole = flag(flagColors[id]);
    pole.position.set(
      (box.minX + box.maxX) / 2,
      top - 0.15,
      (box.minZ + box.maxZ) / 2,
    );
    pole.scale.setScalar(0.001);
    pole.visible = false;
    scene.add(pole);
    buildings[id] = {
      glass,
      points,
      pole,
      glow: id === "beyond" ? 0.35 : 1.6,
      lit: 0,
      target: 0,
      centre: new Vector3(
        (box.minX + box.maxX) / 2,
        top / 2,
        (box.minZ + box.maxZ) / 2,
      ),
    };
  });

  // ---------- Orbit ----------
  const view = { theta: START.theta, phi: START.phi, zoom: 1 };
  const goal = { ...view };
  let velocity = 0;
  let baseDistance = START.radius;
  let frame = 0;
  let drag = null;
  let moved = 0;
  const pointers = new Map();

  function fit() {
    const w = plane.clientWidth || innerWidth;
    const h = plane.clientHeight || innerHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    const vfov = MathUtils.degToRad(FOV);
    const hfov = 2 * Math.atan(Math.tan(vfov / 2) * camera.aspect);
    // Desktop shows the whole island and its sea; phones get closer so buildings stay tappable.
    const width = camera.aspect < 0.8 ? 19 : 40;
    baseDistance = Math.max(
      width / 2 / Math.tan(hfov / 2),
      (width * 0.62) / 2 / Math.tan(vfov / 2),
    );
    camera.updateProjectionMatrix();
    request();
  }

  function clampGoal() {
    goal.phi = MathUtils.clamp(goal.phi, ...POLAR);
    goal.zoom = MathUtils.clamp(goal.zoom, ...ZOOM);
  }

  function place() {
    const offset = new Vector3().setFromSphericalCoords(
      baseDistance * view.zoom,
      view.phi,
      view.theta,
    );
    camera.position.copy(TARGET).add(offset);
    camera.lookAt(TARGET);
    camera.updateMatrixWorld();
  }

  const shapes = {};
  function project() {
    const v = new Vector3();
    for (const [id, b] of Object.entries(buildings)) {
      const pts = b.points.map((p) => {
        v.copy(p).project(camera);
        return [((v.x + 1) / 2) * 100, ((1 - v.y) / 2) * 100];
      });
      const shape = hull(pts);
      const xs = shape.map((p) => p[0]);
      const ys = shape.map((p) => p[1]);
      const left = Math.min(...xs);
      const top = Math.min(...ys);
      const width = Math.max(...xs) - left || 1;
      const height = Math.max(...ys) - top || 1;
      shapes[id] = {
        left,
        top,
        width,
        height,
        clip: `polygon(${shape.map(([x, y]) => `${(((x - left) / width) * 100).toFixed(2)}% ${(((y - top) / height) * 100).toFixed(2)}%`).join(",")})`,
        depth: Math.round(1000 - camera.position.distanceTo(b.centre) * 10),
      };
    }
  }

  function tick(time) {
    frame = 0;
    let busy = false;
    if (!drag && Math.abs(velocity) > 0.001) {
      goal.theta += velocity;
      velocity *= 0.9;
      busy = true;
    }
    const ease = reducedMotion ? 1 : drag ? 0.45 : 0.14;
    for (const key of ["theta", "phi", "zoom"]) {
      const d = goal[key] - view[key];
      view[key] = Math.abs(d) < 1e-3 ? goal[key] : view[key] + d * ease;
      if (view[key] !== goal[key]) busy = true;
    }
    for (const b of Object.values(buildings)) {
      if (b.lit !== b.target) {
        const d = b.target - b.lit;
        b.lit =
          reducedMotion || Math.abs(d) < 0.01 ? b.target : b.lit + d * 0.08;
        busy = true;
      }
      b.glass.forEach((m) => (m.emissiveIntensity = b.lit * b.glow));
      b.pole.visible = b.lit > 0.01;
      b.pole.scale.setScalar(Math.max(0.001, b.lit));
      b.pole.userData.pennant.rotation.y = reducedMotion
        ? 0
        : Math.sin(time / 600 + b.centre.x) * 0.25 * b.lit;
    }
    place();
    renderer.render(scene, camera);
    project();
    onChange?.(shapes);
    if (busy) request();
  }

  function request() {
    if (!frame) frame = requestAnimationFrame(tick);
  }

  // Pointer drag on the whole map, including over building links (which stay clickable on a tap).
  function down(event) {
    if (event.button > 0) return;
    pointers.set(event.pointerId, [event.clientX, event.clientY]);
    if (pointers.size === 1) {
      drag = { x: event.clientX, y: event.clientY, t: performance.now() };
      moved = 0;
      velocity = 0;
    } else drag = { pinch: spread() };
  }
  function spread() {
    const [a, b] = [...pointers.values()];
    return Math.hypot(a[0] - b[0], a[1] - b[1]);
  }
  function move(event) {
    if (!pointers.has(event.pointerId) || !drag) return;
    pointers.set(event.pointerId, [event.clientX, event.clientY]);
    if (drag.pinch) {
      const now = spread();
      goal.zoom *= drag.pinch / now;
      drag.pinch = now;
      moved += 10;
    } else {
      const dx = event.clientX - drag.x;
      const dy = event.clientY - drag.y;
      moved += Math.abs(dx) + Math.abs(dy);
      if (moved > 6 && !plane.classList.contains("is-dragging")) {
        plane.classList.add("is-dragging");
        onDragStart?.();
      }
      const speed = (Math.PI * 1.6) / Math.max(plane.clientWidth, 600);
      goal.theta -= dx * speed;
      goal.phi -= dy * speed * 0.7;
      velocity = reducedMotion ? 0 : -dx * speed * 0.5;
      drag.x = event.clientX;
      drag.y = event.clientY;
    }
    clampGoal();
    request();
  }
  function up(event) {
    pointers.delete(event.pointerId);
    if (pointers.size === 0) {
      drag = null;
      plane.classList.remove("is-dragging");
    } else if (pointers.size === 1) {
      const [[x, y]] = [...pointers.values()];
      drag = { x, y };
    }
    request();
  }
  plane.addEventListener("pointerdown", down);
  addEventListener("pointermove", move);
  addEventListener("pointerup", up);
  addEventListener("pointercancel", up);
  // A drag that ends over a building is not a click on it.
  plane.addEventListener(
    "click",
    (event) => {
      if (moved > 6) {
        event.preventDefault();
        event.stopPropagation();
      }
      moved = 0;
    },
    true,
  );
  plane.addEventListener("dragstart", (event) => event.preventDefault());
  plane.addEventListener(
    "wheel",
    (event) => {
      event.preventDefault();
      goal.zoom *= Math.exp(event.deltaY * 0.0012);
      clampGoal();
      request();
    },
    { passive: false },
  );
  new ResizeObserver(fit).observe(plane);

  host.append(renderer.domElement);
  fit();
  place();
  renderer.compile(scene, camera);

  return {
    canvas: renderer.domElement,
    shapes,
    render: request,
    resize: fit,
    rotate(degrees) {
      velocity = 0;
      goal.theta += MathUtils.degToRad(degrees);
      request();
    },
    tilt(degrees) {
      goal.phi += MathUtils.degToRad(degrees);
      clampGoal();
      request();
    },
    reset() {
      velocity = 0;
      // Turn back the short way round.
      const turns = Math.round((view.theta - START.theta) / (Math.PI * 2));
      goal.theta = START.theta + turns * Math.PI * 2;
      goal.phi = START.phi;
      goal.zoom = 1;
      request();
    },
    setVisited(ids) {
      for (const [id, b] of Object.entries(buildings))
        b.target = ids.has(id) ? 1 : 0;
      request();
    },
    get dragging() {
      return plane.classList.contains("is-dragging");
    },
  };
}
