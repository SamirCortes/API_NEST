# API NestJS + MySQL + RabbitMQ

API REST de clientes y productor de mensajes. MySQL, RabbitMQ, la API y el consumidor corren en Docker. En el equipo solo hace falta Docker.

## Levantar el entorno

Con Docker encendido:

```bash
git clone https://github.com/SamirCortes/API_NEST.git
cd API_NEST
docker compose up -d --build
```

Ese comando construye la imagen y levanta cuatro contenedores: MySQL (laboratorio anterior), RabbitMQ, la API productora y el consumidor. La cola `messages_queue` es durable y se declara sola al conectar; no hay que crearla en la consola.

| Recurso | URL |
|---------|-----|
La API escucha en el puerto **3020** del equipo. Dentro del contenedor el proceso sigue en el 3000.

| API productora | http://localhost:3020 |
| Swagger | http://localhost:3020/api/docs |
| MySQL (host) | `localhost:3307` |
| RabbitMQ AMQP | `localhost:5672` |
| RabbitMQ Management | http://localhost:15672 (user: `nest` / pass: `nest`) |

Dentro de la red de Docker los servicios se llaman `mysql` y `rabbitmq`, no `localhost`.

```bash
docker compose logs -f consumer
docker compose logs -f api
docker compose down
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
| `message.published` | POST `/messages` |
| `client.created` | POST `/clients` |
| `client.updated` | PUT `/clients/:id` |
| `client.deleted` | DELETE `/clients/:id` |

Cola: `messages_queue` (durable). Los cuatro eventos los lee solo el contenedor consumidor.

**UI de administración:** http://localhost:15672 — usuario `nest` / contraseña `nest`
