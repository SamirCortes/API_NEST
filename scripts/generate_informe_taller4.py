#!/usr/bin/env python3
"""Informe del taller 4: APM (SigNoz) y prueba de estrés (k6)."""

from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
POSTMAN = ROOT / "postman"
DOCS = ROOT / "docs"
CHARTS = DOCS / "taller4"
OUT = DOCS / "Informe_Taller_04_APM.pdf"

FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_B = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_I = "/System/Library/Fonts/Supplemental/Arial Italic.ttf"

# Medición del 26/10/2026, 10:10 a 10:30 hora local (UTC-5).
# Pet./s, percentiles y error del APM: trazas Server de GET, POST y PUT /clients
# en signoz_traces.signoz_index_v3, una fila por escalón de 3 minutos.
# La columna rate impresa por k6 divide el conteo entre los 19,5 min de toda
# la prueba, por eso no se usa como peticiones por segundo.
USUARIOS = [10, 25, 50, 100, 200, 400]
PET_S = [72.0, 46.7, 38.1, 31.2, 26.7, 24.4]
P95 = [278, 959, 2235, 5505, 13397, 30208]
ERROR_APM = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
ERROR_K6 = [0.0, 0.0, 0.0, 0.0, 0.0, 1.37]


def chart(path: Path, title: str, ylabel: str, series, y_max, hline=None, hline_label=None):
    width, height = 1100, 640
    left, right, top, bottom = 100, 40, 80, 90
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(FONT, 20)
    font_b = ImageFont.truetype(FONT_B, 26)
    font_s = ImageFont.truetype(FONT, 16)
    draw.text((left, 24), title, fill=(20, 40, 70), font=font_b)

    plot_w = width - left - right
    plot_h = height - top - bottom
    x0, y0 = left, top
    x1, y1 = left + plot_w, top + plot_h
    draw.rectangle((x0, y0, x1, y1), outline=(180, 180, 180))

    ticks = 5
    for i in range(ticks + 1):
        value = y_max * i / ticks
        y = y1 - (plot_h * i / ticks)
        draw.line((x0, y, x1, y), fill=(230, 230, 230))
        label = f"{value:.0f}" if y_max >= 10 else f"{value:.1f}"
        draw.text((8, y - 10), label, fill=(80, 80, 80), font=font_s)

    n = len(USUARIOS)
    step = plot_w / n

    def xy(index, value):
        x = x0 + step * (index + 0.5)
        y = y1 - (plot_h * (value / y_max))
        return x, y

    if hline is not None:
        y = y1 - (plot_h * (hline / y_max))
        draw.line((x0, y, x1, y), fill=(180, 50, 50), width=2)
        if hline_label:
            draw.text((x0 + 8, y - 22), hline_label, fill=(180, 50, 50), font=font_s)

    for name, values, color in series:
        points = [xy(i, values[i]) for i in range(n)]
        draw.line(points, fill=color, width=3)
        for x, y in points:
            draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=color)

    for i, users in enumerate(USUARIOS):
        x = x0 + step * (i + 0.5)
        draw.text((x - 16, y1 + 12), str(users), fill=(40, 40, 40), font=font)
    draw.text((x0, height - 32), "Usuarios concurrentes", fill=(40, 40, 40), font=font)
    draw.text((8, top - 28), ylabel, fill=(40, 40, 40), font=font_s)

    legend_x = x1 - 280
    for i, (name, _values, color) in enumerate(series):
        y = y0 + 12 + i * 26
        draw.rectangle((legend_x, y, legend_x + 18, y + 18), fill=color)
        draw.text((legend_x + 26, y - 2), name, fill=(30, 30, 30), font=font_s)

    image.save(path)


def build_charts():
    CHARTS.mkdir(parents=True, exist_ok=True)
    chart(
        CHARTS / "usuarios_vs_peticiones.png",
        "Usuarios frente a peticiones por segundo",
        "Pet./s",
        [("APM, api-nest", PET_S, (20, 90, 160))],
        y_max=80,
    )
    chart(
        CHARTS / "usuarios_vs_p95.png",
        "Usuarios frente a latencia p95",
        "p95 (ms)",
        [("p95 del APM", P95, (20, 90, 160))],
        y_max=32000,
        hline=500,
        hline_label="Criterio: 500 ms",
    )
    chart(
        CHARTS / "usuarios_vs_error.png",
        "Usuarios frente a tasa de error",
        "Error (%)",
        [
            ("APM, trazas con error", ERROR_APM, (20, 90, 160)),
            ("k6, fallos vistos por el cliente", ERROR_K6, (180, 90, 40)),
        ],
        y_max=2,
        hline=1,
        hline_label="Criterio: 1 %",
    )


class InformePDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 9)
        self.set_text_color(80, 80, 80)
        self.cell(
            0,
            6,
            "FET - Optativa IV | Taller 4 - APM y prueba de estrés",
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

    def shot(self, title: str, path: Path):
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

    def table(self, headers, rows, widths):
        self.set_font("Arial", "B", 7)
        self.set_fill_color(20, 60, 120)
        self.set_text_color(255, 255, 255)
        for index, header in enumerate(headers):
            self.cell(widths[index], 7, header, border=1, fill=True, align="C")
        self.ln()
        self.set_text_color(0, 0, 0)
        self.set_font("Arial", "", 8)
        for row in rows:
            for index, cell in enumerate(row):
                self.cell(widths[index], 6.5, cell, border=1, align="C")
            self.ln()
        self.ln(2)


def build():
    build_charts()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pdf = InformePDF(format="A4")
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
        "Informe del taller 4 - Monitoreo con APM y prueba de estrés",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(
        0,
        6,
        "Optativa IV - Sistemas de Tiempo Real Distribuidos\n"
        "Fundación Escuela Tecnológica de Neiva (FET)\n"
        "Medición: 26 de octubre de 2026, 10:10 a 10:30 (UTC-5)",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.ln(2)

    pdf.section("1. Respuesta")
    pdf.body(
        "Esta infraestructura soporta 72 peticiones por segundo con 10 usuarios "
        "concurrentes antes de incumplir los criterios declarados el 25 de octubre de 2026. "
        "El recurso que impone ese límite es la API: un proceso Node con tope de 1 CPU. "
        "A partir de 25 usuarios el caudal baja y la latencia p95 pasa de 500 ms. "
        "La memoria de la API no se llenó y el tiempo del SELECT no explica la espera."
    )

    pdf.section("2. Criterios, fijados antes de medir")
    pdf.body(
        "Quedaron escritos el 25 de octubre de 2026 en docs/criterios_saturacion.md. "
        "No se cambiaron después de ver la corrida."
    )
    pdf.bullet("Tasa de error menor o igual a 1 %.")
    pdf.bullet("Latencia p95 menor o igual a 500 ms.")
    pdf.bullet("El throughput tiene que seguir subiendo al aumentar los usuarios.")
    pdf.body(
        "El punto de saturación es el último escalón que cumple los tres a la vez. "
        "El calentamiento de 1 minuto con 10 usuarios no entra en la tabla."
    )

    pdf.section("3. Cómo se midió")
    pdf.body(
        "SigNoz recibe las trazas de la API por OpenTelemetry. k6 corre en otro contenedor "
        "y durante 3 minutos en cada escalón llama al CRUD de clientes: 70 % GET /clients, "
        "20 % POST /clients y 10 % PUT /clients/:id, con datos distintos en cada escritura. "
        "Escalones: 10, 25, 50, 100, 200 y 400 usuarios, sin pausa entre peticiones."
    )
    pdf.body(
        "Las peticiones por segundo, los percentiles y el error de la tabla salen de las "
        "trazas de servidor de SigNoz (GET /clients, POST /clients y PUT /clients/:id), "
        "contadas dentro de cada ventana de 3 minutos. En el escalón 1 el APM registró "
        "12.955 peticiones; el contador de k6 en ese mismo tramo pasó de 11.082 a 24.081 "
        "iteraciones, 12.999 en 3 minutos, unas 72 por segundo. Coinciden."
    )
    pdf.body(
        "La tabla que k6 imprime al final no sirve para la columna de peticiones por segundo. "
        "Su columna rate divide el conteo del escalón entre los 19,5 minutos de toda la prueba, "
        "y por eso muestra 11,10 en el escalón 1. Los percentiles y el porcentaje de error "
        "de esa tabla sí corresponden a cada escalón. El código 99 de k6 solo avisa de que "
        "se cruzaron los umbrales a partir del escalón 2."
    )

    pdf.section("4. Tabla de los seis escalones")
    pdf.body(
        "Latencia y error: APM. Peticiones por segundo: conteo de trazas del APM dividido "
        "entre 180 segundos. CPU, memoria y conexiones: no se muestreó docker stats durante "
        "la corrida, y esas celdas no se rellenan con una estimación."
    )
    headers = ["Esc", "Usr", "Pet/s", "p50", "p95", "p99", "Err%", "CPU API", "CPU BD", "Mem", "Conex"]
    widths = [11, 14, 14, 16, 18, 18, 14, 18, 18, 14, 16]
    rows = [
        ["1", "10", "72,0", "60", "278", "381", "0,00", "s/d", "s/d", "s/d", "s/d"],
        ["2", "25", "46,7", "242", "959", "1158", "0,00", "s/d", "s/d", "s/d", "s/d"],
        ["3", "50", "38,1", "938", "2235", "2626", "0,00", "s/d", "s/d", "s/d", "s/d"],
        ["4", "100", "31,2", "2714", "5505", "6247", "0,00", "s/d", "s/d", "s/d", "s/d"],
        ["5", "200", "26,7", "6796", "13397", "14439", "0,00", "s/d", "s/d", "s/d", "s/d"],
        ["6", "400", "24,4", "15254", "30208", "31548", "0,00", "s/d", "s/d", "s/d", "s/d"],
    ]
    pdf.table(headers, rows, widths)
    pdf.body(
        "Los tiempos están en milisegundos y son los de la traza en el servidor. "
        "s/d significa sin dato de docker stats. En el escalón 6 k6 vio 1,37 % de fallos "
        "en el cliente (el p99 del cliente llegó a 60 s y k6 cortó esas peticiones). "
        "En SigNoz esas mismas peticiones que sí terminaron quedaron en HTTP 200 o 201, "
        "con 0 % de trazas en error. El criterio de error del APM se cumple en los seis "
        "escalones. El de latencia y el de crecimiento del caudal solo se cumplen en el 1."
    )
    pdf.body(
        "Referencia del cliente, no usada como columna oficial de latencia: p95 de k6 "
        "338 ms, 1126 ms, 2455 ms, 5913 ms, 14101 ms y 31906 ms. Va por encima del servidor, "
        "como corresponde al viaje de ida y vuelta, y cruza 500 ms en el mismo escalón."
    )

    pdf.section("5. Punto de saturación")
    pdf.body(
        "El último escalón que cumple los tres criterios es el 1: 10 usuarios y "
        "72 peticiones por segundo. El p95 del APM es 278 ms, el error es 0 % y el caudal "
        "todavía está en su máximo. En el escalón 2, con 25 usuarios, el caudal baja a "
        "47 peticiones por segundo y el p95 sube a 959 ms. Ahí ya fallan dos criterios."
    )

    pdf.section("6. Ficha del equipo")
    pdf.bullet("Equipo: Apple M2 Max, 12 núcleos, 32 GB de RAM, macOS 26.7.1.")
    pdf.bullet(
        "Docker Desktop 23.0.5, con 4 CPU y 7,7 GB de RAM asignados a la máquina virtual. "
        "Los contenedores no ven los 12 núcleos ni los 32 GB."
    )
    pdf.bullet("mysql: límite 1 CPU y 1 GB. max_connections = 151. Pool de la API: el de TypeORM, 10 conexiones.")
    pdf.bullet("api (api-nest): límite 1 CPU y 512 MB.")
    pdf.bullet("consumer: límite 0,5 CPU y 512 MB. No entra en esta prueba.")
    pdf.bullet("rabbitmq: límite 0,5 CPU y 512 MB.")
    pdf.bullet("signoz: límite 1 CPU y 1 GB. clickhouse: límite 1 CPU y 2 GB. otel-collector: límite 0,5 CPU y 512 MB.")
    pdf.bullet("k6: límite 2 CPU y 1 GB, por encima de la API, para que el generador no sea el tope.")
    pdf.body(
        "Lo que SigNoz sí registró del proceso Node durante la prueba: el heap usado "
        "no pasó de unos 68 MB, frente al límite de 512 MB del contenedor. "
        "La utilización del event loop llegó a 1,0 en todos los escalones y su retraso p99 "
        "pasó de 54 ms en el escalón 1 a 217 ms en el 6. Eso no es un porcentaje de CPU "
        "del contenedor; docker stats no se guardó."
    )

    pdf.section("7. Gráficas")
    pdf.body(
        "Las tres gráficas usan los usuarios de cada escalón y los valores de la tabla. "
        "La de error agrega la serie de k6 para mostrar el 1,37 % del escalón 6, "
        "que el APM no cuenta como error de servidor."
    )
    for title, filename in (
        ("Usuarios frente a peticiones por segundo.", "usuarios_vs_peticiones.png"),
        ("Usuarios frente a latencia p95. La línea roja es el criterio de 500 ms.", "usuarios_vs_p95.png"),
        ("Usuarios frente a tasa de error. La línea roja es el criterio de 1 %.", "usuarios_vs_error.png"),
    ):
        pdf.shot(title, CHARTS / filename)

    pdf.section("8. Capturas del APM")
    pdf.body(
        "Panel del servicio api-nest, percentiles, tasa de error y una traza de "
        "GET /clients tomada al cierre de la prueba (26 de octubre de 2026, 10:30:28). "
        "Esa traza dura 14,91 s. El tramo findAll dura 14,89 s y el SELECT dura 406 ms."
    )
    for title, filename in (
        ("Panel del servicio api-nest durante la prueba.", "signoz panel servicio api-nest.png"),
        ("Latencia por percentiles (p50, p90 y p99).", "signoz latencia percentiles api-nest.png"),
        ("Tasa de error del servicio, pegada a 0 %.", "signoz tasa de error api-nest.png"),
        (
            "Traza GET /clients: 14,91 s en total, SELECT de 406 ms.",
            "signoz traza get clients.png",
        ),
    ):
        image = POSTMAN / filename
        if image.exists():
            pdf.shot(title, image)
        else:
            pdf.body(f"Falta la captura: {filename}")

    pdf.section("9. Preguntas de análisis")
    pdf.body(
        "1. Lo primero que se degradó al cruzar el punto de saturación fue la latencia, "
        "no la tasa de error. Entre 10 y 25 usuarios el p95 pasa de 278 ms a 959 ms y "
        "el caudal deja de subir. El error del APM sigue en 0 % hasta el final. k6 solo "
        "ve fallos del cliente en el escalón de 400 usuarios, cuando la espera ya va "
        "en decenas de segundos. Ese orden indica que la API sigue aceptando el trabajo "
        "y lo termina en HTTP 200, pero lo encola: responde tarde antes de empezar a fallar."
    )
    pdf.body(
        "2. La proporción sí cambió con la carga, y se midió en GET /clients, que es el 70 % "
        "del escenario. En el escalón 1 el p50 de la petición es 37 ms y el del SELECT es "
        "22 ms: alrededor del 60 % del tiempo está en la consulta. En el escalón 6 el p50 "
        "de la petición es 15.050 ms y el del SELECT es 202 ms: alrededor del 1 %. "
        "El tiempo que se agrega al subir usuarios se queda en la aplicación. La traza de "
        "las 10:30, con 14,91 s y un SELECT de 406 ms, es un caso de ese tramo."
    )
    pdf.body(
        "3. El throughput no siguió creciendo. El máximo es el escalón 1, con 72 peticiones "
        "por segundo. Después baja en cada escalón: 47, 38, 31, 27 y 24 peticiones por segundo."
    )
    pdf.body(
        "4. La memoria no se agotó: el heap de Node se quedó cerca de 68 MB y el contenedor "
        "de la API tiene 512 MB. El tope de conexiones de MySQL es 151 y el SELECT p50 solo "
        "pasó de 22 ms a 202 ms, así que la consulta no es la espera de 15 s. "
        "No hay una muestra de CPU del contenedor ni de conexiones activas, porque no se "
        "corrió docker stats en cada escalón. Con lo que sí quedó, el recurso que impone "
        "el límite es la API: un solo proceso Node limitado a 1 CPU. El event loop llegó "
        "a utilización 1,0 y, en cuanto los usuarios pasan de 10, el caudal baja y la espera "
        "crece dentro de la petición, no dentro del SELECT."
    )
    pdf.body(
        "5. El cambio concreto es paginar GET /clients. Esa operación es el 70 % de la carga "
        "y devuelve la tabla completa. Durante la prueba los POST fueron agrandando la tabla, "
        "y las trazas muestran que el SELECT se mantuvo corto mientras la petición pasó "
        "de 37 ms a 15 s. Devolver una página reduce el trabajo por petición en el proceso "
        "que ya no acepta más caudal. El siguiente ajuste, si después de paginar el límite "
        "sigue siendo la API, es subir su tope de 1 CPU."
    )

    pdf.section("10. Declaración de uso de inteligencia artificial")
    pdf.body(
        "Se utilizó Cursor, con el modelo Grok, como asistencia durante este taller."
    )
    pdf.bullet("Montar SigNoz, el colector OpenTelemetry y la instrumentación de la API y del consumidor.")
    pdf.bullet("Escribir el escenario k6 y los límites de CPU y memoria de los contenedores.")
    pdf.bullet("Ejecutar la prueba de unos 20 minutos y leer las trazas en ClickHouse.")
    pdf.bullet("Tomar las capturas de SigNoz en tamaño de escritorio y guardarlas en postman/.")
    pdf.bullet("Redactar este informe, la tabla, las tres gráficas y las respuestas de análisis.")
    pdf.body(
        "Los números de la tabla no se estimaron: salen de las trazas de la corrida del "
        "26 de octubre de 2026 y del contador de iteraciones de k6. Las celdas de CPU, "
        "memoria y conexiones quedaron vacías a propósito, porque esa muestra no se tomó. "
        "El estudiante asume la responsabilidad del código entregado, de la medición y "
        "de la comprensión de la solución."
    )

    pdf.output(str(OUT))
    print(f"PDF generado: {OUT}")


if __name__ == "__main__":
    build()
