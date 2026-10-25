# Criterios de saturación

Declarados el 25 de octubre de 2026, antes de la primera medición del taller 4. No se ajustan después de ver los resultados.

| Criterio | Umbral | Qué significa |
|----------|--------|----------------|
| Tasa de error | ≤ 1 % | Por encima, el sistema ya está rechazando trabajo |
| Latencia p95 | ≤ 500 ms | Por encima, la respuesta deja de ser aceptable |
| Crecimiento del throughput | Sigue subiendo al aumentar usuarios | Si al subir usuarios las peticiones por segundo se aplanan, el sistema ya saturó |

El punto de saturación es el último escalón que cumple los tres criterios a la vez.

Escalones, todavía no ejecutados, en `k6/clientes.js`: 1 minuto de calentamiento con 10 usuarios (se descarta) y luego 10, 25, 50, 100, 200 y 400 usuarios concurrentes, 3 minutos cada uno. Mezcla: 70 % listar, 20 % crear y 10 % actualizar. Si el equipo no aguanta esa progresión, se baja antes de la primera medición y se deja escrito el cambio aquí.
