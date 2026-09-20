# API NestJS + MySQL

API REST de clientes con NestJS, TypeORM, MySQL en Docker y documentación Swagger.

## Requisitos

Antes de empezar, instala en tu PC:

- [Node.js](https://nodejs.org/) **20 o superior**
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (debe estar **encendido**)
- Git (opcional, si clonas el repositorio)

## Pasos para levantar la API en otro PC

### 1. Obtener el proyecto

```bash
git clone <URL_DEL_REPOSITORIO>
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

El archivo `.env` queda así por defecto:

```env
PORT=3000
DB_HOST=localhost
DB_PORT=3307
DB_USERNAME=nest
DB_PASSWORD=nest
DB_DATABASE=api_nest
```

> MySQL se expone en el puerto **3307** del host para no chocar con otras instalaciones.

### 4. Encender MySQL (Docker)

Asegúrate de que Docker Desktop esté corriendo y luego:

```bash
npm run docker:up
```

Espera unos segundos a que MySQL arranque. La base de datos se llama `api_nest`.

### 5. Ejecutar migraciones

Crea la tabla `clients`:

```bash
npm run migration:run
```

### 6. Levantar la API

```bash
npm run start:dev
```

Si todo salió bien verás algo como:

```text
API: http://localhost:3000
Swagger: http://localhost:3000/api/docs
```

### 7. Probar

| Recurso | URL |
|---------|-----|
| API | http://localhost:3000 |
| Swagger | http://localhost:3000/api/docs |

Desde Swagger puedes probar todos los endpoints del CRUD.

## Colección Postman

Archivo: `postman/API_Nest_Clients.postman_collection.json`

1. Abre Postman → **Import**
2. Selecciona ese archivo
3. Con la API corriendo, ejecuta las requests en orden (1 → 8)

La variable `baseUrl` apunta a `http://localhost:3000`. Al crear un cliente, se guarda el `id` en `clientId` para las demás pruebas.

## Detener el entorno

```bash
# Detener la API: Ctrl + C en la terminal

# Detener MySQL
npm run docker:down
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
| `POST`   | `/clients`      | Crear cliente            |
| `GET`    | `/clients`      | Listar clientes          |
| `GET`    | `/clients/:id`  | Consultar cliente por id |
| `PUT`    | `/clients/:id`  | Actualizar cliente       |
| `DELETE` | `/clients/:id`  | Eliminar cliente         |

### Ejemplo con curl

```bash
curl -X POST http://localhost:3000/clients \
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
npm run docker:up          # Levantar MySQL
npm run docker:down        # Detener MySQL
npm run migration:run      # Aplicar migraciones
npm run migration:revert   # Revertir última migración
npm run start:dev          # API en modo desarrollo
npm run build              # Compilar proyecto
npm run start:prod         # API en producción (después de build)
```
