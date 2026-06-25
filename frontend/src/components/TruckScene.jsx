import { Canvas } from "@react-three/fiber";
import { OrbitControls, Grid, ContactShadows, Environment } from "@react-three/drei";
import Truck from "./Truck.jsx";
import PackageBox from "./PackageBox.jsx";

const DECK = 2.4;

export default function TruckScene({ truck, placed, selectedId, onSelect }) {
  const focus = [-1, DECK + truck.D * 0.45, 0];

  return (
    <Canvas
      shadows
      dpr={[1, 2]}
      camera={{ position: [-15, 12, 16], fov: 40 }}
      gl={{ antialias: true }}
      onPointerMissed={() => onSelect?.(null)}
    >
      <color attach="background" args={["#0e1420"]} />
      <fog attach="fog" args={["#0e1420", 32, 70]} />

      <ambientLight intensity={0.45} />
      <directionalLight
        position={[12, 20, 8]}
        intensity={1.3}
        castShadow
        shadow-mapSize={[2048, 2048]}
        shadow-camera-left={-24}
        shadow-camera-right={24}
        shadow-camera-top={24}
        shadow-camera-bottom={-24}
      />
      <directionalLight position={[-12, 9, -8]} intensity={0.35} color="#4fd1e0" />
      <Environment preset="warehouse" />

      <Truck truck={truck} deckY={DECK} />

      {placed.map((box) => (
        <PackageBox
          key={box.id}
          box={box}
          truck={truck}
          deckY={DECK}
          selected={box.id === selectedId}
          anySelected={selectedId !== null && selectedId !== undefined}
          onSelect={onSelect}
        />
      ))}

      <Grid
        position={[0, 0, 0]}
        args={[60, 60]}
        cellSize={1}
        cellColor="#1e2838"
        sectionSize={4}
        sectionColor="#2a3546"
        fadeDistance={48}
        fadeStrength={1.5}
        infiniteGrid
      />
      <ContactShadows position={[0, 0.02, 0]} opacity={0.45} scale={40} blur={2.6} far={14} />

      <OrbitControls
        enablePan={false}
        minDistance={12}
        maxDistance={48}
        maxPolarAngle={Math.PI / 2.1}
        autoRotate={placed.length === 0}
        autoRotateSpeed={0.5}
        target={focus}
      />
    </Canvas>
  );
}
