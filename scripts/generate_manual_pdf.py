#!/usr/bin/env python3
"""Generate delivery manual PDF for API Nest laboratory."""

from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos

ROOT = Path(__file__).resolve().parent.parent
POSTMAN = ROOT / "postman"
OUT = ROOT / "docs" / "Manual_Entrega_API_Nest.pdf"

GITHUB = "https://github.com/SamirCortes/API_NEST.git"

SCREENSHOTS = [
    ("1. Crear cliente (POST /clients)", "image create clients.png"),
    ("2. Listar clientes (GET /clients)", "image list clients.png"),
    ("3. Consultar cliente por id (GET /clients/:id)", "image list client.png"),
    ("4. Actualizar cliente (PUT /clients/:id)", "image update client.png"),
    ("5. Eliminar cliente (DELETE /clients/:id)", "image delete client.png"),
    ("6. Listado posterior a eliminar (GET /clients)", "image list client delete.png"),
]


class ManualPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(80, 80, 80)
        self.cell(
            0,
            6,
            "FET - Optativa IV | API NestJS + MySQL",
            align="C",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        self.ln(2)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"Pagina {self.page_no()}/{{nb}}", align="C")

    def section(self, title: str):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(20, 60, 120)
        self.multi_cell(0, 7, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def body(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 5.5, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def bullet(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 5.5, f"- {text}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def code(self, text: str):
        self.set_font("Courier", "", 8)
        self.set_fill_color(245, 245, 245)
        usable = self.epw
        self.multi_cell(
            usable, 4.5, text, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT
        )
        self.ln(2)

    def bold_line(self, text: str):
        self.set_font("Helvetica", "B", 10)
        self.multi_cell(0, 5.5, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def build():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pdf = ManualPDF(format="A4")
    pdf.alias_nb_pages()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(
        0,
        8,
        "Manual de entrega - API REST NestJS + MySQL",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(
        0,
        6,
        "Laboratorio: Optativa IV - Sistemas de Tiempo Real Distribuidos\n"
        "Fundacion Escuela Tecnologica de Neiva (FET)",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.ln(2)

    pdf.section("1. Contenido del paquete de entrega")
    pdf.body(
        "El archivo ZIP de entrega contiene el codigo fuente del proyecto "
        "(sin node_modules), el script SQL, Docker Compose, la coleccion de "
        "Postman, las capturas de evidencia y este manual."
    )
    pdf.bullet("Codigo fuente: carpeta API_NEST/ (raiz del proyecto NestJS)")
    pdf.bullet("Script SQL: sql/01_create_database_and_clients.sql")
    pdf.bullet("Contenedor MySQL: docker-compose.yml")
    pdf.bullet("Coleccion Postman: postman/API_Nest_Clients.postman_collection.json")
    pdf.bullet("Capturas Postman: postman/*.png")
    pdf.bullet("Este manual: docs/Manual_Entrega_API_Nest.pdf")
    pdf.ln(1)

    pdf.section("2. Repositorio en GitHub")
    pdf.body("El codigo fuente tambien esta publicado en:")
    pdf.code(GITHUB)
    pdf.body("Para clonar en otro equipo:")
    pdf.code(f"git clone {GITHUB}\ncd API_NEST")

    pdf.section("3. Requisitos previos (instalacion desde cero)")
    pdf.bullet("Instalar Docker Desktop: https://www.docker.com/products/docker-desktop/")
    pdf.bullet("Abrir Docker Desktop y esperar a que el motor este Running")
    pdf.bullet("Instalar Node.js 20 o superior: https://nodejs.org/")
    pdf.bullet("Verificar: docker --version && node -v && npm -v")
    pdf.bullet("(Opcional) Postman para importar la coleccion de pruebas")

    pdf.section("4. Como levantar MySQL (contenedor Docker)")
    pdf.body(
        "El archivo docker-compose.yml define el servicio MySQL 8.0. "
        "Crea automaticamente la base de datos api_nest. Puerto del host: 3307."
    )
    pdf.code("cd API_NEST\ndocker compose up -d\n# o bien:\nnpm run docker:up")
    pdf.body("Credenciales por defecto (.env.example):")
    pdf.code(
        "Host: localhost\n"
        "Port: 3307\n"
        "Database: api_nest\n"
        "User: nest\n"
        "Password: nest\n"
        "Root password: root"
    )
    pdf.body(
        "Si DBeaver muestra 'Public Key Retrieval is not allowed', "
        "en Driver properties configure allowPublicKeyRetrieval=true."
    )

    pdf.section("5. Script SQL y migraciones")
    pdf.body("Hay dos formas equivalentes de crear la tabla clients:")
    pdf.bold_line("Opcion A - Script SQL (entregable)")
    pdf.body(
        "Archivo: sql/01_create_database_and_clients.sql\n"
        "Puede ejecutarlo en DBeaver o por linea de comandos:"
    )
    pdf.code(
        "docker exec -i api_nest_mysql mysql -unest -pnest < "
        "sql/01_create_database_and_clients.sql"
    )
    pdf.bold_line("Opcion B - Migracion TypeORM")
    pdf.body(
        "Archivo: src/database/migrations/1740000000000-CreateClientsTable.ts"
    )
    pdf.code("cp .env.example .env\nnpm install\nnpm run migration:run")
    pdf.body("SQL equivalente de la tabla:")
    pdf.code(
        "CREATE TABLE `clients` (\n"
        "  `id` int NOT NULL AUTO_INCREMENT,\n"
        "  `names` varchar(100) NOT NULL,\n"
        "  `surnames` varchar(100) NOT NULL,\n"
        "  `age` int NULL,\n"
        "  `created_at` timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),\n"
        "  `status` tinyint NOT NULL DEFAULT 1,\n"
        "  PRIMARY KEY (`id`)\n"
        ") ENGINE=InnoDB;"
    )

    pdf.section("6. Como levantar el proyecto (API NestJS)")
    pdf.code(
        "cd API_NEST\n"
        "cp .env.example .env\n"
        "npm install\n"
        "npm run docker:up\n"
        "npm run migration:run\n"
        "npm run start:dev"
    )
    pdf.body("URLs:")
    pdf.bullet("API: http://localhost:3000")
    pdf.bullet("Swagger: http://localhost:3000/api/docs")
    pdf.bullet("Endpoints base: http://localhost:3000/clients")

    pdf.section("7. Coleccion de Postman (ruta de importacion)")
    pdf.body("Ruta del archivo a importar en Postman:")
    pdf.code("postman/API_Nest_Clients.postman_collection.json")
    pdf.body(
        "Pasos:\n"
        "1. Abrir Postman\n"
        "2. Pulsar Import\n"
        "3. Seleccionar el archivo anterior\n"
        "4. Verificar variable baseUrl = http://localhost:3000\n"
        "5. Ejecutar las peticiones en orden (1 a 8)"
    )
    pdf.body(
        "La coleccion incluye: crear, listar, consultar, actualizar, "
        "crear sin edad, validacion, 404 y eliminar."
    )

    pdf.section("8. Formato de respuesta de la API")
    pdf.code(
        '{ "status": true, "message": "Registro consultado", "data": {} }\n'
        '{ "status": true, "message": "Registro eliminado" }\n'
        '{ "status": false, "message": "Registro no encontrado" }'
    )

    pdf.section("9. Declaracion de uso de herramientas de inteligencia artificial")
    pdf.body(
        "Se utilizo Cursor (editor con agente de IA, modelo Composer) como "
        "asistencia durante el desarrollo del laboratorio."
    )
    pdf.bold_line("Herramienta:")
    pdf.body("Cursor AI (agente de codigo).")
    pdf.bold_line("Para que se uso:")
    pdf.bullet("Generar la estructura inicial del proyecto NestJS")
    pdf.bullet("Configurar TypeORM, Docker Compose (MySQL) y migraciones")
    pdf.bullet("Implementar CRUD REST, validaciones y formato de respuesta")
    pdf.bullet("Montar Swagger, coleccion Postman y documentacion README")
    pdf.bullet("Ajustar mensajes de validacion en espanol (nombres, apellidos, etc.)")
    pdf.bold_line("Modificaciones realizadas sobre lo generado por IA:")
    pdf.bullet("Revision y pruebas manuales de endpoints en Postman")
    pdf.bullet("Ajuste del puerto MySQL a 3307 y configuracion allowPublicKeyRetrieval")
    pdf.bullet("Personalizacion de mensajes de negocio y validacion en espanol")
    pdf.bullet("Capturas de evidencia y armado del paquete de entrega academico")
    pdf.bullet("Verificacion de migraciones/SQL y flujo de instalacion en local")
    pdf.body(
        "El estudiante asume la responsabilidad del codigo entregado, "
        "de su funcionamiento y de la comprension de la solucion."
    )

    pdf.add_page()
    pdf.section("10. Evidencias - Capturas de Postman")
    pdf.body(
        "A continuacion se incluyen capturas de las peticiones ejecutadas "
        "en Postman con sus respectivas respuestas."
    )

    for title, filename in SCREENSHOTS:
        img_path = POSTMAN / filename
        if not img_path.exists():
            continue
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 6, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)
        max_w = pdf.epw
        pdf.image(str(img_path), x=pdf.l_margin, w=max_w)

    pdf.output(str(OUT))
    print(f"PDF generado: {OUT}")


if __name__ == "__main__":
    build()
