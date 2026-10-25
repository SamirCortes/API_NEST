# API NestJS + MySQL + RabbitMQ

API REST de clientes y productor de mensajes. MySQL, RabbitMQ, la API, el consumidor y SigNoz (APM) corren en Docker. En el equipo solo hace falta Docker.

## Levantar el entorno

Con Docker encendido:

```bash
git clone https://github.com/SamirCortes/API_NEST.git
cd API_NEST
docker compose up -d --build
```

Ese comando construye la imagen y levanta la API, el consumidor, MySQL, RabbitMQ y SigNoz. La primera vez SigNoz descarga sus imágenes y puede tardar varios minutos. La cola `messages_queue` es durable y se declara sola al conectar; no hay que crearla en la consola.

| Recurso | URL |
|---------|-----|
La API escucha en el puerto **3020** del equipo. Dentro del contenedor el proceso sigue en el 3000.

| API productora | http://localhost:3020 |
| Swagger | http://localhost:3020/api/docs |
| MySQL (host) | `localhost:3307` |
| RabbitMQ AMQP | `localhost:5672` |
| RabbitMQ Management | http://localhost:15672 (user: `nest` / pass: `nest`) |
| SigNoz | http://localhost:8088 |

Dentro de la red de Docker los servicios se llaman `mysql` y `rabbitmq`, no `localhost`.

```bash
docker compose logs -f consumer
docker compose logs -f api
docker compose down
```

## Monitoreo con SigNoz

La API y el consumidor arrancan con OpenTelemetry y envían trazas y métricas al colector `otel-collector` (puerto 4318 dentro de Docker). La interfaz queda en http://localhost:8088. El puerto 8080 del equipo ya lo usa otro contenedor, por eso SigNoz se publica en el **8088**.

La primera vez que abras http://localhost:8088, SigNoz pide crear el usuario administrador. Después, en Services aparece `api-nest`. Una traza de `GET /clients` muestra el tiempo de la petición y, dentro, el `SELECT` contra MySQL.

Los criterios de saturación del taller 4 están escritos en `docs/criterios_saturacion.md` y se fijaron antes de medir.

## Prueba de estrés

El generador es k6, en el contenedor del perfil `stress`. No arranca con `docker compose up`. El escenario versionado está en `k6/clientes.js`.

| Operación | Proporción |
|-----------|------------|
| `GET /clients` | 70 % |
| `POST /clients` | 20 % |
| `PUT /clients/:id` | 10 % |

Cada alta y cada actualización manda nombres, apellidos y edad distintos. El escalón 0 dura 1 minuto con 10 usuarios y se descarta. Después hay seis escalones de 3 minutos: 10, 25, 50, 100, 200 y 400 usuarios concurrentes. Dentro de Docker la prueba habla con `http://api:3000`.

La corrida dura unos 20 minutos. No se ha ejecutado todavía.

```bash
docker compose --profile stress run --rm k6
```

## Productor

`POST /messages` recibe un JSON y lo publica en `messages_queue`. La respuesta usa `Content-Type: application/json` y `status` booleano.

Mensaje:

```json
{"sensor": "OD-01", "valor": 4.2, "unidad": "mg/L"}
```

Si se encoló:

```json
{"status": true, "message": "Mensaje encolado"}
```

Si el cuerpo no es JSON válido:

```json
{"status": false, "message": "Formato de mensaje inválido"}
```

```bash
curl -X POST http://localhost:3020/messages \
  -H "Content-Type: application/json" \
  -d '{"sensor":"OD-01","valor":4.2,"unidad":"mg/L"}'
```

## Consumidor

El contenedor `api_nest_consumer` lee la misma cola. Escribe en su log el contenido y la hora de recepción, y solo entonces confirma el mensaje (sale de la cola después de procesarse). La API no consume: se puede detener el consumidor y seguir publicando.

Los mensajes se publican como persistentes y la cola es durable, así que sobreviven a un reinicio de RabbitMQ. El volumen `rabbitmq_data` guarda esos datos.

## Casos de prueba

### 1. Consumidor detenido

```bash
docker compose stop consumer
```

Publica varios mensajes con Postman o curl. En http://localhost:15672 la cola `messages_queue` debe mostrarlos en Ready. Después:

```bash
docker compose start consumer
docker compose logs -f consumer
```

Esos mensajes deben aparecer en el log y la cola debe quedar en cero.

### 2. Reinicio de RabbitMQ

Con el consumidor detenido y mensajes en Ready:

```bash
docker compose restart rabbitmq
```

Espera a que la consola vuelva a abrir. Los mensajes siguen en la cola. Luego `docker compose start consumer` y se consumen.

### 3. Mensaje inválido

```bash
curl -i -X POST http://localhost:3020/messages \
  -H "Content-Type: application/json" \
  -d '{sensor: OD-01}'
```

La respuesta es `status: false` y el contador de la cola no aumenta.

## Pagos

`POST /pagos` guarda el pago en MySQL con estado `REGISTRADO`, publica solo su `id` en `messages_queue` y responde enseguida. No espera a que el consumidor termine.

```json
{"referencia": "PAG-0001", "valor": 125000, "medio": "transferencia"}
```

```json
{"status": true, "message": "Pago registrado", "data": {"id": 1, "estado": "REGISTRADO"}}
```

Si faltan datos, el valor no es un número mayor que cero, o el cuerpo no es JSON:

```json
{"status": false, "message": "Datos del pago inválidos"}
```

`GET /pagos/:id` consulta el mismo pago. Justo después del registro el estado es `REGISTRADO`. Unos segundos después pasa a `PROCESADO`.

El consumidor espera `PROCESS_DELAY_MS`, escribe un comprobante en `procesamientos` y solo entonces confirma el mensaje. En el log quedan el id, la hora en que lo tomó y la hora en que terminó.

En el caso 1 ese valor era `4000` (4 segundos). Para el caso 2 quedó en `15000` dentro de `docker-compose.yml`: el pago 16 se registró al instante y el log terminó unos 15 segundos después. Para volver a la pausa corta, pon `4000` y ejecuta `docker compose up -d consumer`.

```bash
docker compose logs -f consumer
```

### Casos

1. Consumidor detenido. `docker compose stop consumer`, registra cinco pagos y revisa en MySQL que siguen en `REGISTRADO`. La API responde igual de rápido. Luego `docker compose start consumer` y los cinco pasan a `PROCESADO`.
2. Acción más lenta. En `docker-compose.yml` cambia `PROCESS_DELAY_MS` a `15000` y ejecuta `docker compose up -d consumer`. Vuelve a medir el tiempo de `POST /pagos`: no debe crecer, porque la API no espera esa pausa.
3. Fallo al procesar. Registra un pago con referencia `PAG-FALLA`. El consumidor lo toma, falla antes de actualizar la base y devuelve el mensaje a la cola. El pago sigue en `REGISTRADO`. Para la captura, detén el consumidor y mira la cola y la tabla. Ese mensaje se reintenta mientras el consumidor siga encendido; al terminar la evidencia, bórralo desde la consola de RabbitMQ o deja el consumidor detenido.

La colección está en `postman/Pagos_RabbitMQ.postman_collection.json`.

Las capturas de los tres casos están en `postman/` y en el manual `docs/Manual_Entrega_API_Nest.pdf`.

## Colección Postman

Archivo del taller: `postman/Mensajeria_RabbitMQ.postman_collection.json`

1. Postman → **Import** y selecciona ese archivo.
2. Ejecuta **1. Mensaje válido** y **2. Mensaje inválido**.
3. Para los diez mensajes, abre el Collection Runner, elige solo **1. Mensaje válido** y pon 10 iteraciones.
4. Exporta la colección si Postman la modifica.

La colección del CRUD de clientes sigue en `postman/API_Nest_Clients.postman_collection.json`.

## Desarrollo local (no hace falta para la entrega)

Esta vía instala Node en el equipo. El taller se evalúa solo con Docker.

### Opción B — API en local + MySQL en Docker

### 1. Obtener el proyecto

```bash
git clone https://github.com/SamirCortes/API_NEST.git
cd API_NEST
```

O copia la carpeta del proyecto y ábrela en la terminal.

### 2. Instalar dependencias

```bash
npm install
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

El archivo `.env` queda así por defecto (para API local):

```env
PORT=3000
DB_HOST=localhost
DB_PORT=3307
DB_USERNAME=nest
DB_PASSWORD=nest
DB_DATABASE=api_nest
```

> MySQL se expone en el puerto **3307** del host. Dentro de Docker Compose, la API usa `DB_HOST=mysql` y puerto `3306`.

### 4. Encender MySQL (Docker)

```bash
docker compose up -d mysql
```

### 5. Ejecutar migraciones

```bash
npm run migration:run
```

### 6. Levantar la API en local

```bash
npm run start:dev
```

Si todo salió bien verás algo como:

```text
API: http://localhost:3020
Swagger: http://localhost:3020/api/docs
```

### 7. Probar

| Recurso | URL |
|---------|-----|
| API | http://localhost:3020 |
| Swagger | http://localhost:3020/api/docs |

Desde Swagger puedes probar todos los endpoints del CRUD.

## Colección Postman

Archivo: `postman/API_Nest_Clients.postman_collection.json`

1. Abre Postman → **Import**
2. Selecciona ese archivo
3. Con la API corriendo, ejecuta las requests en orden (1 → 8)

La variable `baseUrl` apunta a `http://localhost:3020`. Al crear un cliente, se guarda el `id` en `clientId` para las demás pruebas.

## Detener el entorno

```bash
# Si usas Docker completo (API + MySQL):
npm run docker:down

# Si la API corre en local: Ctrl + C, luego:
docker compose stop mysql
```

## Entidad `clients`

| Columna      | Tipo         | Restricciones                     |
|--------------|--------------|-----------------------------------|
| `id`         | INT          | PK, AUTO_INCREMENT                |
| `names`      | VARCHAR(100) | NOT NULL                          |
| `surnames`   | VARCHAR(100) | NOT NULL                          |
| `age`        | INT          | NULL (opcional)                   |
| `created_at` | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP         |
| `status`     | BOOLEAN      | NOT NULL, DEFAULT true            |

## Formato de respuesta

Todas las respuestas usan `Content-Type: application/json` y `status` como **boolean**.

**Éxito con datos**
```json
{ "status": true, "message": "Registro consultado", "data": {} }
```

**Éxito sin datos**
```json
{ "status": true, "message": "Registro eliminado" }
```

**Error**
```json
{ "status": false, "message": "Registro no encontrado" }
```

## Endpoints

| Método   | Ruta            | Descripción              |
|----------|-----------------|--------------------------|
| `POST`   | `/pagos`        | Registrar pago               |
| `GET`    | `/pagos/:id`    | Consultar pago por id        |
| `POST`   | `/messages`     | Publicar mensaje en la cola |
| `POST`   | `/clients`      | Crear cliente            |
| `GET`    | `/clients`      | Listar clientes          |
| `GET`    | `/clients/:id`  | Consultar cliente por id |
| `PUT`    | `/clients/:id`  | Actualizar cliente       |
| `DELETE` | `/clients/:id`  | Eliminar cliente         |

### Ejemplo con curl

```bash
curl -X POST http://localhost:3020/clients \
  -H "Content-Type: application/json" \
  -d '{"names":"Ana","surnames":"Lopez","age":28}'
```

## Conexión desde DBeaver

Si aparece `Public Key Retrieval is not allowed`:

1. Editar conexión → **Driver properties**
2. `allowPublicKeyRetrieval` = `true`
3. (Opcional) `useSSL` = `false`

Datos:

- Host: `localhost`
- Port: `3307`
- Database: `api_nest`
- User: `nest`
- Password: `nest`

## Scripts útiles

```bash
npm run docker:up          # Build + levantar API y MySQL
npm run docker:down        # Detener contenedores
npm run docker:logs        # Logs de la API
npm run docker:logs:consumer # Logs del consumidor
npm run docker:rebuild     # Rebuild forzado
npm run migration:run      # Migraciones (API local)
npm run migration:revert   # Revertir última migración
npm run start:dev          # API en modo desarrollo (local)
npm run build              # Compilar proyecto
npm run start:prod         # API en producción (después de build)
```

## RabbitMQ

| Evento | Cuándo |
|--------|--------|
| `payment.registered` | POST `/pagos` |
| `message.published` | POST `/messages` |
| `client.created` | POST `/clients` |
| `client.updated` | PUT `/clients/:id` |
| `client.deleted` | DELETE `/clients/:id` |

Cola: `messages_queue` (durable). Esos eventos los lee solo el contenedor consumidor. `payment.registered` además actualiza el pago en MySQL.

**UI de administración:** http://localhost:15672 — usuario `nest` / contraseña `nest`
