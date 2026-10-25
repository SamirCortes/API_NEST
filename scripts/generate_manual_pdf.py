#!/usr/bin/env python3
"""Genera el manual de entrega del laboratorio NestJS + RabbitMQ."""

from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
POSTMAN = ROOT / "postman"
OUT = ROOT / "docs" / "Manual_Entrega_API_Nest.pdf"
GITHUB = "https://github.com/SamirCortes/API_NEST.git"

FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_B = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_I = "/System/Library/Fonts/Supplemental/Arial Italic.ttf"

CLIENT_SHOTS = [
    ("1. Crear cliente (POST /clients)", "image create clients.png"),
    ("2. Listar clientes (GET /clients)", "image list clients.png"),
    ("3. Consultar cliente por id (GET /clients/:id)", "image list client.png"),
    ("4. Actualizar cliente (PUT /clients/:id)", "image update client.png"),
    ("5. Eliminar cliente (DELETE /clients/:id)", "image delete client.png"),
    ("6. Listado posterior a eliminar (GET /clients)", "image list client delete.png"),
]

PAGOS_SHOTS = [
    (
        "Caso 1, antes. Cola messages_queue vacía, con el consumidor detenido.",
        "pagos cola vacia.png",
    ),
    (
        "Caso 1, antes. Cinco pagos en Ready, 0 consumidores y mensajes persistentes.",
        "pagos 5 pagos registrados.png",
    ),
    (
        "Caso 1, antes. Los pagos 3 a 7 están en REGISTRADO. "
        "El pago 2 (PAG-FALLA) también sigue en REGISTRADO.",
        "pagos 5 registros en BD.png",
    ),
    (
        "Caso 1, después. El log muestra los pagos 3 a 7 tomados y finalizados. "
        "Arriba también se ve el fallo del pago 2, que volvió a la cola.",
        "pagos procesados consola.png",
    ),
    (
        "Caso 1, después. La cola queda en 0 y hay 1 consumidor activo.",
        "pagos pagos procesados rabbitMQ.png",
    ),
    (
        "Caso 2. PROCESS_DELAY_MS quedó en 15000.",
        "pagos cambio a 15 segundos.png",
    ),
    (
        "Caso 2. POST /pagos del pago 16 responde de inmediato con estado REGISTRADO.",
        "pago registrado delay .png",
    ),
    (
        "Caso 2. Mientras el consumidor espera, el pago 16 sigue en REGISTRADO.",
        "pago regsitrado delay BD.png",
    ),
    (
        "Caso 2. Log del pago 16: tomado a las 23:12:21.705Z y finalizado a las 23:12:36.759Z (15 segundos).",
        "pago procesado delay consola.png",
    ),
    (
        "Caso 2. Tabla de pagos después de registrar el pago 16.",
        "pago procesado delay.png",
    ),
]

RABBIT_SHOTS = [
    (
        "Mensaje válido. POST /messages responde status true y Mensaje encolado.",
        "rabbitMQ mensaje encolado.jpeg",
    ),
    (
        "Caso 1, antes. Consumidor detenido: 5 mensajes en Ready. "
        "La cola es durable y los 5 mensajes son persistentes.",
        "rabbitMQ 5 mensajes cola.jpeg",
    ),
    (
        "Caso 1, después. Al levantar el consumidor la cola queda en 0 "
        "y aparece 1 consumidor.",
        "rabbitMQ 5 ejecutados.jpeg",
    ),
    (
        "Caso 3. Cuerpo que no es JSON válido: status false y "
        "Formato de mensaje inválido. No se publica en la cola.",
        "rabbitMQ formato invalido.jpeg",
    ),
]


class ManualPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 9)
        self.set_text_color(80, 80, 80)
        self.cell(
            0,
            6,
            "FET - Optativa IV | API NestJS + MySQL + RabbitMQ",
            align="C",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        self.ln(2)

    def footer(self):
        self.set_y(-12)
        self.set_font("Arial", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"Página {self.page_no()}/{{nb}}", align="C")

    def section(self, title: str):
        self.ln(1)
        self.set_font("Arial", "B", 13)
        self.set_text_color(20, 60, 120)
        self.multi_cell(0, 7, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def body(self, text: str):
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 5.5, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def bullet(self, text: str):
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 5.5, f"- {text}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def code(self, text: str):
        self.set_font("Arial", "", 9)
        self.set_fill_color(245, 245, 245)
        self.multi_cell(
            self.epw, 4.8, text, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT
        )
        self.ln(2)

    def bold_line(self, text: str):
        self.set_font("Arial", "B", 10)
        self.multi_cell(0, 5.5, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def screenshot(self, title: str, path: Path):
        self.add_page()
        self.set_font("Arial", "B", 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)
        with Image.open(path) as image:
            width_px, height_px = image.size
        max_w = self.epw
        max_h = self.h - self.get_y() - 18
        height = max_w * (height_px / width_px)
        if height > max_h:
            self.image(str(path), x=self.l_margin, h=max_h)
        else:
            self.image(str(path), x=self.l_margin, w=max_w)


def build():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pdf = ManualPDF(format="A4")
    pdf.add_font("Arial", "", FONT)
    pdf.add_font("Arial", "B", FONT_B)
    pdf.add_font("Arial", "I", FONT_I)
    pdf.alias_nb_pages()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.multi_cell(
        0,
        8,
        "Manual de entrega - API REST NestJS, MySQL y RabbitMQ",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(
        0,
        6,
        "Laboratorio: Optativa IV - Sistemas de Tiempo Real Distribuidos\n"
        "Fundación Escuela Tecnológica de Neiva (FET)\n"
        "Taller 2: Mensajería con RabbitMQ en contenedores Docker",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.ln(2)

    pdf.section("1. Contenido del paquete de entrega")
    pdf.body(
        "El ZIP contiene el código fuente (sin node_modules), Docker, el script SQL, "
        "las colecciones de Postman, las capturas y este manual. El PDF está en la "
        "raíz de la carpeta de entrega y también en API_NEST/docs/."
    )
    pdf.bullet("Código fuente: carpeta API_NEST/")
    pdf.bullet("Imagen y composición: Dockerfile y docker-compose.yml")
    pdf.bullet("Script SQL de clientes: sql/01_create_database_and_clients.sql")
    pdf.bullet("Script SQL de pagos: sql/02_create_pagos_and_procesamientos.sql")
    pdf.bullet("Postman de pagos: postman/Pagos_RabbitMQ.postman_collection.json")
    pdf.bullet("Postman de clientes: postman/API_Nest_Clients.postman_collection.json")
    pdf.bullet("Postman de mensajería: postman/Mensajeria_RabbitMQ.postman_collection.json")
    pdf.bullet("Capturas: postman/*.png y postman/*.jpeg")
    pdf.bullet("Este manual: Manual_Entrega_API_Nest.pdf")

    pdf.section("2. Repositorio")
    pdf.body("El código también está publicado en:")
    pdf.code(GITHUB)
    pdf.code(f"git clone {GITHUB}\ncd API_NEST")

    pdf.section("3. Cómo levantar todo con un solo comando")
    pdf.body(
        "En el equipo solo hace falta Docker. No se instala Node, RabbitMQ ni MySQL. "
        "Con Docker encendido:"
    )
    pdf.code("cd API_NEST\ndocker compose up -d --build")
    pdf.body(
        "Ese comando construye la imagen y levanta MySQL, RabbitMQ, la API productora "
        "y el consumidor. La cola messages_queue es durable y se crea sola al conectar."
    )
    pdf.bullet("API productora: http://localhost:3020")
    pdf.bullet("Swagger: http://localhost:3020/api/docs")
    pdf.bullet("MySQL en el equipo: localhost:3307 (usuario nest, clave nest)")
    pdf.bullet("RabbitMQ AMQP: localhost:5672")
    pdf.bullet("Consola RabbitMQ: http://localhost:15672 (usuario nest, clave nest)")
    pdf.body(
        "Dentro de la red de Docker los servicios se llaman mysql y rabbitmq, no localhost. "
        "La API publica el puerto 3020 porque en este equipo el 3000 estaba ocupado. "
        "Dentro del contenedor el proceso escucha en el 3000."
    )
    pdf.code(
        "docker compose logs -f consumer\n"
        "docker compose logs -f api\n"
        "docker compose down"
    )

    pdf.section("4. Productor")
    pdf.body(
        "El contenedor de la API expone POST /messages. Recibe un JSON, lo publica "
        "en messages_queue y responde Content-Type: application/json. El campo status "
        "es booleano."
    )
    pdf.code('{"sensor": "OD-01", "valor": 4.2, "unidad": "mg/L"}')
    pdf.bold_line("Si el mensaje se publica:")
    pdf.code('{"status": true, "message": "Mensaje encolado"}')
    pdf.bold_line("Si el cuerpo no es JSON válido:")
    pdf.code('{"status": false, "message": "Formato de mensaje inválido"}')
    pdf.body(
        "Crear, actualizar o borrar un cliente también publica un evento en la misma cola. "
        "Consultar o listar no publica nada."
    )

    pdf.section("5. Consumidor")
    pdf.body(
        "El contenedor api_nest_consumer usa la misma imagen y ejecuta node dist/consumer.js. "
        "No abre un puerto. Se conecta a messages_queue, escribe en su log el contenido y "
        "la hora, y solo después confirma el mensaje para retirarlo de la cola. "
        "Si RabbitMQ aún no está listo, reintenta la conexión."
    )
    pdf.code("docker compose logs -f consumer")

    pdf.section("6. Casos que se comprueban")
    pdf.bold_line("1. Consumidor detenido")
    pdf.code(
        "docker compose stop consumer\n"
        "# Publicar varios POST /messages\n"
        "# En la consola, messages_queue muestra Ready > 0\n"
        "docker compose start consumer\n"
        "docker compose logs -f consumer"
    )
    pdf.body(
        "Los mensajes se acumulan y, al levantar el consumidor, se procesan todos. "
        "La cola vuelve a Ready 0."
    )
    pdf.bold_line("2. Reinicio de RabbitMQ")
    pdf.body(
        "Con el consumidor detenido y mensajes en Ready se ejecuta "
        "docker compose restart rabbitmq. La cola es durable y los mensajes son "
        "persistentes, así que siguen en la cola al volver la consola. "
        "En la captura de los 5 mensajes se ve durable: true y Persistent: 5."
    )
    pdf.code("docker compose restart rabbitmq")
    pdf.bold_line("3. Mensaje inválido")
    pdf.code(
        "curl -i -X POST http://localhost:3020/messages \\\n"
        "  -H \"Content-Type: application/json\" \\\n"
        "  -d '{sensor: OD-01}'"
    )
    pdf.body(
        "La respuesta lleva status en false y el contador de la cola no aumenta."
    )

    pdf.section("7. Registro de pagos")
    pdf.body(
        "POST /pagos valida los datos, inserta el pago con estado REGISTRADO, "
        "publica solo su id en messages_queue y responde enseguida. "
        "GET /pagos/:id consulta ese pago. El consumidor espera PROCESS_DELAY_MS, "
        "pasa el estado a PROCESADO, guarda un comprobante en procesamientos "
        "y solo entonces confirma el mensaje."
    )
    pdf.code(
        "POST http://localhost:3020/pagos\n"
        '{"referencia": "PAG-0001", "valor": 125000, "medio": "transferencia"}\n\n'
        '{"status": true, "message": "Pago registrado", '
        '"data": {"id": 1, "estado": "REGISTRADO"}}'
    )
    pdf.bold_line("Datos inválidos, sin insertar ni publicar:")
    pdf.code('{"status": false, "message": "Datos del pago inválidos"}')
    pdf.body(
        "En el caso 1 el retardo era de 4 segundos. En el log, el pago 3 se tomó "
        "a las 23:03:41.564Z y terminó a las 23:03:45.598Z. El pago 7 terminó "
        "a las 23:04:01.677Z. La API ya había respondido REGISTRADO antes de eso."
    )
    pdf.body(
        "En el caso 2, PROCESS_DELAY_MS pasó a 15000. El pago 16 se registró "
        "a las 23:12:21.692Z y la API respondió REGISTRADO en esa misma petición. "
        "El consumidor lo tomó a las 23:12:21.705Z y lo finalizó a las 23:12:36.759Z, "
        "unos 15 segundos después. El tiempo de respuesta de la API no siguió esa espera."
    )
    pdf.body(
        "En el caso 3, la referencia PAG-FALLA hace fallar el procesamiento. "
        "El pago 2 permanece en REGISTRADO, no tiene fila en procesamientos "
        "y el log dice que el mensaje vuelve a la cola."
    )
    pdf.code(
        "docker compose logs -f consumer\n"
        "# Caso 2: PROCESS_DELAY_MS=15000 y docker compose up -d consumer"
    )

    pdf.section("8. Colecciones de Postman")
    pdf.bold_line("Mensajería")
    pdf.code("postman/Mensajeria_RabbitMQ.postman_collection.json")
    pdf.body(
        "Importar en Postman. La variable baseUrl es http://localhost:3020. "
        "La petición 1 envía un mensaje válido y la 2 un cuerpo que no es JSON. "
        "Para diez mensajes válidos, usar el Collection Runner solo con la petición 1 "
        "y 10 iteraciones."
    )
    pdf.bold_line("Pagos")
    pdf.code("postman/Pagos_RabbitMQ.postman_collection.json")
    pdf.body(
        "Tiene tres peticiones: pago válido, pago inválido y consulta por id. "
        "baseUrl es http://localhost:3020. La consulta hay que ejecutarla "
        "al registrar y otra vez unos diez segundos después."
    )
    pdf.bold_line("Clientes")
    pdf.code("postman/API_Nest_Clients.postman_collection.json")
    pdf.body("Ejecutar las peticiones del CRUD en orden. baseUrl también apunta al puerto 3020.")

    pdf.section("9. API de clientes")
    pdf.bullet("POST /clients crea un cliente y publica client.created")
    pdf.bullet("GET /clients y GET /clients/:id solo consultan")
    pdf.bullet("PUT /clients/:id actualiza y publica client.updated")
    pdf.bullet("DELETE /clients/:id elimina y publica client.deleted")
    pdf.body(
        "La tabla clients se crea con la migración al arrancar la API, o con "
        "sql/01_create_database_and_clients.sql. Las tablas pagos y procesamientos "
        "están en sql/02_create_pagos_and_procesamientos.sql."
    )

    pdf.section("10. Declaración de uso de herramientas de inteligencia artificial")
    pdf.body(
        "Se utilizó Cursor, con el modelo Grok, como asistencia durante el laboratorio."
    )
    pdf.bold_line("Para qué se usó:")
    pdf.bullet("Comparar el taller de RabbitMQ con la API de clientes ya existente")
    pdf.bullet("Separar el productor y el consumidor en contenedores distintos")
    pdf.bullet("Publicar mensajes persistentes en la cola durable messages_queue")
    pdf.bullet("Ajustar POST /messages y POST /pagos al formato de respuesta pedido")
    pdf.bullet("Agregar las tablas pagos y procesamientos y el procesamiento asíncrono")
    pdf.bullet("Actualizar Docker Compose, el README, Swagger y las colecciones de Postman")
    pdf.bullet("Generar este manual y el paquete ZIP de entrega")
    pdf.bold_line("Qué se revisó o hizo sobre ese resultado:")
    pdf.bullet("Pruebas manuales en Swagger, Postman, DBeaver y la consola de RabbitMQ")
    pdf.bullet("Capturas de los casos del taller 3: consumidor detenido, pausa de 15 segundos y fallo PAG-FALLA")
    pdf.bullet("El puerto publicado de la API quedó en 3020 porque el 3000 estaba ocupado")
    pdf.body(
        "El estudiante asume la responsabilidad del código entregado, "
        "de su funcionamiento y de la comprensión de la solución."
    )

    pdf.section("11. Evidencias del CRUD de clientes")
    pdf.body("Capturas de Postman de las peticiones del laboratorio anterior.")
    for title, filename in CLIENT_SHOTS:
        image = POSTMAN / filename
        if image.exists():
            pdf.screenshot(title, image)

    pdf.add_page()
    pdf.section("12. Evidencias de RabbitMQ")
    pdf.body(
        "Capturas del productor y de la consola de administración. "
        "La cola es messages_queue."
    )
    for title, filename in RABBIT_SHOTS:
        image = POSTMAN / filename
        if image.exists():
            pdf.screenshot(title, image)

    pdf.add_page()
    pdf.section("13. Evidencias del taller de pagos")
    pdf.body(
        "Capturas de la cola, de la tabla pagos y del registro del consumidor "
        "para los casos del taller 3."
    )
    for title, filename in PAGOS_SHOTS:
        image = POSTMAN / filename
        if image.exists():
            pdf.screenshot(title, image)
        else:
            pdf.body(f"Falta la captura: {filename}")

    pdf.output(str(OUT))
    print(f"PDF generado: {OUT}")


if __name__ == "__main__":
    build()
