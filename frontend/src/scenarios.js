// Manifiestos preconfigurados para el demo. Cada caja:
// { w, h, d, weight, fragility (0-1), delivery_order }

export const SCENARIOS = [
  {
    id: "super",
    name: "Reparto de supermercado",
    meta: "14 cajas · frágiles mezclados",
    boxes: [
      { w: 3, h: 2, d: 2, weight: 38, fragility: 0.1, delivery_order: 11 },
      { w: 2, h: 2, d: 3, weight: 22, fragility: 0.85, delivery_order: 0 },
      { w: 2, h: 3, d: 2, weight: 30, fragility: 0.2, delivery_order: 8 },
      { w: 1, h: 2, d: 2, weight: 9, fragility: 0.7, delivery_order: 1 },
      { w: 3, h: 3, d: 2, weight: 47, fragility: 0.05, delivery_order: 12 },
      { w: 2, h: 1, d: 3, weight: 14, fragility: 0.5, delivery_order: 3 },
      { w: 2, h: 2, d: 2, weight: 19, fragility: 0.3, delivery_order: 6 },
      { w: 1, h: 1, d: 2, weight: 7, fragility: 0.9, delivery_order: 2 },
      { w: 3, h: 2, d: 3, weight: 41, fragility: 0.15, delivery_order: 13 },
      { w: 2, h: 2, d: 1, weight: 12, fragility: 0.6, delivery_order: 4 },
      { w: 1, h: 3, d: 2, weight: 16, fragility: 0.4, delivery_order: 7 },
      { w: 2, h: 3, d: 3, weight: 35, fragility: 0.1, delivery_order: 10 },
      { w: 1, h: 2, d: 1, weight: 6, fragility: 0.75, delivery_order: 5 },
      { w: 2, h: 2, d: 2, weight: 24, fragility: 0.25, delivery_order: 9 },
    ],
  },
  {
    id: "pharma",
    name: "Ruta de farmacia",
    meta: "12 cajas · alta fragilidad",
    boxes: [
      { w: 2, h: 2, d: 2, weight: 11, fragility: 0.95, delivery_order: 0 },
      { w: 1, h: 2, d: 2, weight: 8, fragility: 0.9, delivery_order: 1 },
      { w: 2, h: 1, d: 2, weight: 9, fragility: 0.85, delivery_order: 4 },
      { w: 2, h: 2, d: 1, weight: 7, fragility: 0.8, delivery_order: 2 },
      { w: 3, h: 2, d: 2, weight: 28, fragility: 0.2, delivery_order: 9 },
      { w: 1, h: 1, d: 3, weight: 6, fragility: 0.95, delivery_order: 3 },
      { w: 2, h: 2, d: 3, weight: 15, fragility: 0.7, delivery_order: 6 },
      { w: 2, h: 3, d: 2, weight: 18, fragility: 0.6, delivery_order: 7 },
      { w: 3, h: 3, d: 2, weight: 44, fragility: 0.1, delivery_order: 11 },
      { w: 1, h: 2, d: 2, weight: 10, fragility: 0.88, delivery_order: 5 },
      { w: 2, h: 2, d: 2, weight: 13, fragility: 0.75, delivery_order: 8 },
      { w: 2, h: 1, d: 3, weight: 20, fragility: 0.3, delivery_order: 10 },
    ],
  },
  {
    id: "industrial",
    name: "Carga industrial",
    meta: "13 cajas · pesadas y grandes",
    boxes: [
      { w: 3, h: 3, d: 3, weight: 90, fragility: 0.0, delivery_order: 9 },
      { w: 3, h: 3, d: 2, weight: 75, fragility: 0.05, delivery_order: 7 },
      { w: 3, h: 2, d: 3, weight: 68, fragility: 0.0, delivery_order: 11 },
      { w: 2, h: 3, d: 3, weight: 60, fragility: 0.1, delivery_order: 5 },
      { w: 3, h: 3, d: 3, weight: 95, fragility: 0.0, delivery_order: 12 },
      { w: 2, h: 2, d: 3, weight: 40, fragility: 0.2, delivery_order: 3 },
      { w: 3, h: 2, d: 2, weight: 52, fragility: 0.1, delivery_order: 8 },
      { w: 2, h: 2, d: 2, weight: 34, fragility: 0.3, delivery_order: 1 },
      { w: 3, h: 3, d: 2, weight: 70, fragility: 0.0, delivery_order: 10 },
      { w: 2, h: 3, d: 2, weight: 45, fragility: 0.15, delivery_order: 4 },
      { w: 2, h: 2, d: 3, weight: 48, fragility: 0.2, delivery_order: 6 },
      { w: 3, h: 2, d: 3, weight: 64, fragility: 0.05, delivery_order: 2 },
      { w: 2, h: 2, d: 2, weight: 30, fragility: 0.25, delivery_order: 0 },
    ],
  },
  {
    id: "mixto",
    name: "Distribución mixta",
    meta: "20 cajas · carga completa",
    boxes: [
      { w: 2, h: 1, d: 3, weight: 12, fragility: 0.09, delivery_order: 17 },
      { w: 3, h: 3, d: 1, weight: 28, fragility: 0.22, delivery_order: 15 },
      { w: 1, h: 1, d: 3, weight: 37, fragility: 0.4, delivery_order: 11 },
      { w: 1, h: 3, d: 1, weight: 27, fragility: 0.29, delivery_order: 18 },
      { w: 3, h: 1, d: 1, weight: 28, fragility: 0.56, delivery_order: 7 },
      { w: 2, h: 1, d: 3, weight: 32, fragility: 0.64, delivery_order: 6 },
      { w: 3, h: 1, d: 2, weight: 31, fragility: 0.56, delivery_order: 19 },
      { w: 2, h: 2, d: 3, weight: 39, fragility: 0.43, delivery_order: 3 },
      { w: 1, h: 1, d: 3, weight: 35, fragility: 0.36, delivery_order: 14 },
      { w: 2, h: 3, d: 2, weight: 38, fragility: 0.08, delivery_order: 0 },
      { w: 2, h: 3, d: 1, weight: 12, fragility: 0.73, delivery_order: 9 },
      { w: 2, h: 1, d: 2, weight: 22, fragility: 0.42, delivery_order: 5 },
      { w: 1, h: 3, d: 3, weight: 35, fragility: 0.96, delivery_order: 16 },
      { w: 2, h: 3, d: 2, weight: 28, fragility: 0.82, delivery_order: 8 },
      { w: 2, h: 1, d: 1, weight: 40, fragility: 0.58, delivery_order: 13 },
      { w: 3, h: 1, d: 1, weight: 33, fragility: 0.47, delivery_order: 2 },
      { w: 3, h: 3, d: 2, weight: 18, fragility: 0.31, delivery_order: 1 },
      { w: 3, h: 2, d: 1, weight: 40, fragility: 0.39, delivery_order: 12 },
      { w: 3, h: 1, d: 2, weight: 10, fragility: 0.36, delivery_order: 4 },
      { w: 1, h: 3, d: 1, weight: 22, fragility: 0.77, delivery_order: 10 },
    ],
  },
  {
    id: "pico",
    name: "Hora pico",
    meta: "18 cajas · secuencia exigente",
    boxes: [
      { w: 3, h: 1, d: 2, weight: 42, fragility: 0.84, delivery_order: 6 },
      { w: 2, h: 2, d: 3, weight: 27, fragility: 0.08, delivery_order: 12 },
      { w: 2, h: 2, d: 1, weight: 28, fragility: 0.14, delivery_order: 15 },
      { w: 3, h: 2, d: 3, weight: 24, fragility: 0.76, delivery_order: 0 },
      { w: 2, h: 3, d: 1, weight: 23, fragility: 0.43, delivery_order: 17 },
      { w: 3, h: 2, d: 3, weight: 27, fragility: 0.59, delivery_order: 7 },
      { w: 1, h: 2, d: 3, weight: 38, fragility: 0.61, delivery_order: 4 },
      { w: 2, h: 1, d: 1, weight: 30, fragility: 0.54, delivery_order: 1 },
      { w: 2, h: 2, d: 3, weight: 21, fragility: 0.25, delivery_order: 16 },
      { w: 3, h: 2, d: 3, weight: 19, fragility: 0.89, delivery_order: 11 },
      { w: 1, h: 3, d: 2, weight: 15, fragility: 0.24, delivery_order: 13 },
      { w: 3, h: 2, d: 2, weight: 10, fragility: 0.43, delivery_order: 2 },
      { w: 1, h: 1, d: 1, weight: 29, fragility: 0.42, delivery_order: 14 },
      { w: 2, h: 3, d: 2, weight: 16, fragility: 0.7, delivery_order: 3 },
      { w: 2, h: 2, d: 1, weight: 37, fragility: 0.41, delivery_order: 10 },
      { w: 3, h: 3, d: 3, weight: 15, fragility: 0.63, delivery_order: 5 },
      { w: 3, h: 1, d: 3, weight: 29, fragility: 0.97, delivery_order: 9 },
      { w: 1, h: 3, d: 3, weight: 32, fragility: 0.86, delivery_order: 8 },
    ],
  },
];

// Color por fragilidad: verde (seguro) -> ámbar -> rojo (muy frágil).
export function fragilityColor(f) {
  const stops = [
    [0.0, [61, 214, 140]], // #3DD68C ok
    [0.5, [242, 169, 59]], // #F2A93B warn
    [1.0, [229, 72, 77]], // #E5484D danger
  ];
  let a = stops[0];
  let b = stops[stops.length - 1];
  for (let i = 0; i < stops.length - 1; i++) {
    if (f >= stops[i][0] && f <= stops[i + 1][0]) {
      a = stops[i];
      b = stops[i + 1];
      break;
    }
  }
  const t = (f - a[0]) / (b[0] - a[0] || 1);
  const rgb = a[1].map((c, i) => Math.round(c + (b[1][i] - c) * t));
  return `rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`;
}