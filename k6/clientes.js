// Escenario del taller 4. Criterios fijados el 25/10/2026 en docs/criterios_saturacion.md.
// 70 % listar, 20 % crear, 10 % actualizar. Los datos de cada escritura cambian.
// El escalón 0 es el calentamiento de 1 minuto y no entra en la tabla.
// Cada escalón medido dura 3 minutos con usuarios constantes.
// Entre escalones hay 5 s para que no se mezclen los usuarios del anterior.

import http from 'k6/http';
import { check } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://api:3000';
const SMOKE = __ENV.K6_SMOKE === '1';

const ESCALONES = [
  { id: '0', vus: 10, duration: '1m', start: '0s', calentamiento: true },
  { id: '1', vus: 10, duration: '3m', start: '1m5s' },
  { id: '2', vus: 25, duration: '3m', start: '4m10s' },
  { id: '3', vus: 50, duration: '3m', start: '7m15s' },
  { id: '4', vus: 100, duration: '3m', start: '10m20s' },
  { id: '5', vus: 200, duration: '3m', start: '13m25s' },
  { id: '6', vus: 400, duration: '3m', start: '16m30s' },
];

function escenario(step) {
  return {
    executor: 'constant-vus',
    exec: 'flujo',
    vus: step.vus,
    duration: step.duration,
    startTime: step.start,
    gracefulStop: '5s',
    tags: { escalon: step.id, usuarios: String(step.vus) },
  };
}

const pasos = SMOKE
  ? [{ id: '1', vus: 2, duration: '15s', start: '0s' }]
  : ESCALONES;

const thresholds = {};
for (const step of pasos) {
  if (step.calentamiento) {
    continue;
  }
  thresholds[`http_req_failed{escalon:${step.id}}`] = ['rate<=0.01'];
  thresholds[`http_req_duration{escalon:${step.id}}`] = ['p(95)<=500'];
  thresholds[`http_reqs{escalon:${step.id}}`] = ['count>=0'];
}

export const options = {
  scenarios: Object.fromEntries(
    pasos.map((step) => [`escalon_${step.id}`, escenario(step)]),
  ),
  thresholds,
  summaryTrendStats: ['avg', 'p(50)', 'p(95)', 'p(99)', 'count'],
};

function clienteNuevo(origen, n) {
  return {
    names: `C${origen}${n}v${__VU}`,
    surnames: `S${Math.floor(Math.random() * 1e9)}`,
    age: Math.floor(Math.random() * 90),
    status: true,
  };
}

export function setup() {
  const ids = [];
  const cantidad = SMOKE ? 5 : 40;
  for (let i = 0; i < cantidad; i += 1) {
    const res = http.post(
      `${BASE_URL}/clients`,
      JSON.stringify(clienteNuevo('setup', i)),
      {
        headers: { 'Content-Type': 'application/json' },
        tags: { operacion: 'semilla' },
      },
    );
    const id = res.json('data.id');
    if (id) {
      ids.push(id);
    }
  }
  if (ids.length === 0) {
    throw new Error(
      'No se pudo crear la semilla de clientes para las actualizaciones',
    );
  }
  return { ids };
}

export function flujo(data) {
  const roll = Math.random();
  const headers = { 'Content-Type': 'application/json' };
  let res;

  if (roll < 0.7) {
    res = http.get(`${BASE_URL}/clients`, { tags: { operacion: 'listar' } });
  } else if (roll < 0.9) {
    res = http.post(
      `${BASE_URL}/clients`,
      JSON.stringify(clienteNuevo('vu', __ITER)),
      { headers, tags: { operacion: 'crear' } },
    );
  } else {
    const id = data.ids[Math.floor(Math.random() * data.ids.length)];
    res = http.put(
      `${BASE_URL}/clients/${id}`,
      JSON.stringify({
        surnames: `U${__VU}i${__ITER}`,
        age: Math.floor(Math.random() * 90),
      }),
      { headers, tags: { operacion: 'actualizar' } },
    );
  }

  check(res, {
    'respuesta 2xx': (r) => r.status >= 200 && r.status < 300,
    'status true': (r) => {
      try {
        return r.json('status') === true;
      } catch {
        return false;
      }
    },
  });
}

function valor(data, nombre, campo) {
  const metric = data.metrics[nombre];
  if (!metric || metric.values[campo] === undefined) {
    return '-';
  }
  const n = metric.values[campo];
  return Number.isInteger(n) ? String(n) : n.toFixed(2);
}

export function handleSummary(data) {
  const lineas = [
    'Escalon  Usuarios  pet/s   p50_ms  p95_ms  p99_ms  error_%  (0 = calentamiento, no se analiza)',
  ];
  for (const step of pasos) {
    const tag = `escalon:${step.id}`;
    const error = data.metrics[`http_req_failed{${tag}}`];
    const errorPct =
      error && error.values.rate !== undefined
        ? (error.values.rate * 100).toFixed(2)
        : '-';
    lineas.push(
      [
        step.id.padEnd(8),
        String(step.vus).padEnd(9),
        valor(data, `http_reqs{${tag}}`, 'rate').padEnd(7),
        valor(data, `http_req_duration{${tag}}`, 'p(50)').padEnd(7),
        valor(data, `http_req_duration{${tag}}`, 'p(95)').padEnd(7),
        valor(data, `http_req_duration{${tag}}`, 'p(99)').padEnd(7),
        errorPct,
      ].join(' '),
    );
  }
  return { stdout: `${lineas.join('\n')}\n` };
}
