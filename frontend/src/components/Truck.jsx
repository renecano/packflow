import { useMemo } from "react";
import * as THREE from "three";

// Camión low-poly translúcido (look de "modelo técnico"): cabina, chasis y
// ruedas semitransparentes con aristas que definen los contornos, para ver la
// carga sin obstrucción. Faros y postes traseros quedan como acentos sólidos.
//
// volumen de carga: x ∈ [-W/2, W/2], y ∈ [deckY, deckY+D], z ∈ [-H/2, H/2]
// puerta (env x=0) -> three x = -W/2 (trasera, abierta) · cabina en +W/2

const WHEEL_R = 0.9;
const GLASS = { transparent: true, opacity: 0.16, side: THREE.DoubleSide };
const EDGE = "#4a5d7a";

function BoxGlass({ size, position, color = "#3a4a63", edge = EDGE }) {
  const edges = useMemo(() => new THREE.EdgesGeometry(new THREE.BoxGeometry(...size)), [size]);
  return (
    <group position={position}>
      <mesh>
        <boxGeometry args={size} />
        <meshStandardMaterial color={color} flatShading {...GLASS} />
      </mesh>
      <lineSegments geometry={edges}>
        <lineBasicMaterial color={edge} transparent opacity={0.6} />
      </lineSegments>
    </group>
  );
}

function Wheel({ position }) {
  return (
    <group position={position}>
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[WHEEL_R, WHEEL_R, 0.55, 12]} />
        <meshStandardMaterial color="#14181f" roughness={0.85} transparent opacity={0.35} flatShading />
      </mesh>
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[WHEEL_R * 0.45, WHEEL_R * 0.45, 0.6, 8]} />
        <meshStandardMaterial color="#5d6a80" metalness={0.5} roughness={0.4} transparent opacity={0.5} flatShading />
      </mesh>
    </group>
  );
}

export default function Truck({ truck, deckY = 2.4 }) {
  const { W, H, D } = truck;
  const t = 0.12;

  const cargoEdges = useMemo(
    () => new THREE.EdgesGeometry(new THREE.BoxGeometry(W, D, H)),
    [W, D, H]
  );

  const cabFront = W / 2 + 3.4;
  const wheelZ = H / 2 - 0.3;

  return (
    <group>
      {/* CHASIS */}
      <BoxGlass
        size={[cabFront + W / 2, 0.4, H - 0.4]}
        position={[(cabFront - W / 2) / 2, deckY - 0.3, 0]}
        color="#2a3546"
      />

      {/* RUEDAS */}
      <Wheel position={[W / 2 + 1.8, WHEEL_R, wheelZ]} />
      <Wheel position={[W / 2 + 1.8, WHEEL_R, -wheelZ]} />
      <Wheel position={[-W / 2 + 2.6, WHEEL_R, wheelZ]} />
      <Wheel position={[-W / 2 + 2.6, WHEEL_R, -wheelZ]} />
      <Wheel position={[-W / 2 + 0.4, WHEEL_R, wheelZ]} />
      <Wheel position={[-W / 2 + 0.4, WHEEL_R, -wheelZ]} />

      {/* CABINA */}
      <group position={[W / 2 + 1.7, deckY, 0]}>
        <BoxGlass size={[3.4, 4.8, H - 0.2]} position={[0, 2.4, 0]} color="#3a4a63" />
        {/* parabrisas tintado (acento) */}
        <mesh position={[1.72, 3.2, 0]} rotation={[0, Math.PI / 2, 0]}>
          <planeGeometry args={[H - 1.2, 2.2]} />
          <meshStandardMaterial color="#0e1420" metalness={0.4} roughness={0.2} emissive="#4fd1e0" emissiveIntensity={0.12} transparent opacity={0.55} side={THREE.DoubleSide} />
        </mesh>
        {/* faros (acento sólido) */}
        <mesh position={[1.74, 0.8, H / 2 - 1.1]}>
          <boxGeometry args={[0.2, 0.6, 0.7]} />
          <meshStandardMaterial color="#ffce8a" emissive="#ff8a3d" emissiveIntensity={0.8} />
        </mesh>
        <mesh position={[1.74, 0.8, -(H / 2 - 1.1)]}>
          <boxGeometry args={[0.2, 0.6, 0.7]} />
          <meshStandardMaterial color="#ffce8a" emissive="#ff8a3d" emissiveIntensity={0.8} />
        </mesh>
      </group>

      {/* CAJA DE CARGA (abierta) */}
      <group position={[0, deckY + D / 2, 0]}>
        {/* piso (sólido para recibir sombra) */}
        <mesh position={[0, -D / 2 + 0.06, 0]} receiveShadow>
          <boxGeometry args={[W, 0.12, H]} />
          <meshStandardMaterial color="#1b2435" roughness={0.9} flatShading />
        </mesh>
        {/* pared frontal translúcida (lado cabina) */}
        <mesh position={[W / 2 - t / 2, 0, 0]}>
          <boxGeometry args={[t, D, H]} />
          <meshStandardMaterial color="#2a3546" transparent opacity={0.16} side={THREE.DoubleSide} />
        </mesh>
        {/* paredes laterales translúcidas */}
        <mesh position={[0, 0, H / 2 - t / 2]}>
          <boxGeometry args={[W, D, t]} />
          <meshStandardMaterial color="#3a4a63" transparent opacity={0.1} side={THREE.DoubleSide} />
        </mesh>
        <mesh position={[0, 0, -H / 2 + t / 2]}>
          <boxGeometry args={[W, D, t]} />
          <meshStandardMaterial color="#3a4a63" transparent opacity={0.1} side={THREE.DoubleSide} />
        </mesh>
        {/* aristas del volumen */}
        <lineSegments geometry={cargoEdges}>
          <lineBasicMaterial color={EDGE} transparent opacity={0.85} />
        </lineSegments>
        {/* postes traseros ámbar (marco de la puerta) */}
        {[H / 2 - t, -(H / 2 - t)].map((z, i) => (
          <mesh key={i} position={[-W / 2 + t, 0, z]}>
            <boxGeometry args={[t * 1.6, D, t * 1.6]} />
            <meshStandardMaterial color="#ff8a3d" emissive="#ff8a3d" emissiveIntensity={0.25} flatShading />
          </mesh>
        ))}
      </group>
    </group>
  );
}