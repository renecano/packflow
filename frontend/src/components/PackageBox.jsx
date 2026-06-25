import { useRef, useMemo, useState } from "react";
import { useFrame } from "@react-three/fiber";
import { Html } from "@react-three/drei";
import * as THREE from "three";
import { fragilityColor } from "../scenarios.js";

// Una caja colocada. Cae desde arriba con easing. Soporta selección:
// el seleccionado brilla y muestra su número; los demás se atenúan.
export default function PackageBox({ box, truck, deckY = 2.4, selected, anySelected, onSelect }) {
  const ref = useRef();
  const [hovered, setHovered] = useState(false);
  const { W, H } = truck;
  const [px, py, pz] = box.position;
  const [sw, sh, sd] = box.size;

  const target = useMemo(
    () => ({
      x: px + sw / 2 - W / 2,
      y: deckY + pz + sd / 2,
      z: py + sh / 2 - H / 2,
    }),
    [px, py, pz, sw, sh, sd, W, H, deckY]
  );

  const color = useMemo(() => new THREE.Color(fragilityColor(box.fragility)), [box.fragility]);
  const dropY = useRef(target.y + 9);

  useFrame((_, delta) => {
    if (!ref.current) return;
    dropY.current += (target.y - dropY.current) * Math.min(1, delta * 6);
    ref.current.position.set(target.x, dropY.current, target.z);
    // Escala extra sutil al seleccionar o pasar el cursor.
    const s = selected ? 1.06 : hovered ? 1.03 : 1;
    ref.current.scale.lerp(new THREE.Vector3(s, s, s), Math.min(1, delta * 10));
  });

  const dimmed = anySelected && !selected;

  return (
    <mesh
      ref={ref}
      castShadow
      receiveShadow
      position={[target.x, dropY.current, target.z]}
      onClick={(e) => {
        e.stopPropagation();
        onSelect?.(selected ? null : box.id);
      }}
      onPointerOver={(e) => {
        e.stopPropagation();
        setHovered(true);
        document.body.style.cursor = "pointer";
      }}
      onPointerOut={() => {
        setHovered(false);
        document.body.style.cursor = "auto";
      }}
    >
      <boxGeometry args={[sw * 0.96, sd * 0.96, sh * 0.96]} />
      <meshStandardMaterial
        color={color}
        roughness={0.55}
        metalness={0.1}
        emissive={color}
        emissiveIntensity={selected ? 0.85 : 0.12}
        transparent
        opacity={dimmed ? 0.22 : 1}
      />
      {selected && (
        <Html center distanceFactor={16} position={[0, sd / 2 + 0.6, 0]}>
          <div
            style={{
              fontFamily: "JetBrains Mono, monospace",
              fontSize: 12,
              fontWeight: 700,
              color: "#0e1420",
              background: "#ff8a3d",
              padding: "2px 7px",
              borderRadius: 6,
              whiteSpace: "nowrap",
              boxShadow: "0 2px 10px rgba(0,0,0,.4)",
            }}
          >
            #{box.id}
          </div>
        </Html>
      )}
    </mesh>
  );
}