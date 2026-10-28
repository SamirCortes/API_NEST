#!/usr/bin/env python3
"""Informe del taller de investigación 2: cotización comparativa en la nube."""

from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "Informe_Cotizacion_Nube.pdf"
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_B = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_I = "/System/Library/Fonts/Supplemental/Arial Italic.ttf"
H = 730


def money(value):
    rounded = round(value + 1e-9, 2)
    text = f"{rounded:,.2f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def row_sum(rows, index):
    return sum(rows[i][1][index] for i in range(len(rows)))


# Cada tupla: (etiqueta, [aws, azure, gcp, vultr])
LINES = []


def add(label, values):
    LINES.append((label, values))


# AWS sa-east-1, lista de precios con vigencia 2026-10-01. Horas: 730.
aws_fe = 0.0672 * H + 50 * 0.152
aws_be = 2 * (0.1344 * H + 50 * 0.152)
aws_rb = aws_fe
aws_my = 0.280 * H + 100 * 0.219
aws_lb = 0.034 * H + 1000 * 0.011
aws_mon = 5 * 0.90 + 5 * 0.0408 + 40 * 0.30
aws_reg = 20 * 0.10
aws_egr = (500 - 100) * 0.25
aws_oth = 0.093 * H + 20 * 0.093 + 3 * 0.005 * H
aws_dep = 2.5 * 0.25

# Azure Brazil South, Retail Prices API, 27/10/2026.
az_fe = 0.0672 * H + 8.96
az_be = 2 * (0.134 * H + 8.96)
az_rb = az_fe
az_my = 0.28 * H + 100 * 0.2185
az_cu = (1000 * 8 * 10**9) / (H * 3600) / 1e6 / 2.22
az_lb = 0.40 * H + az_cu * 0.0144 * H
az_mon = 5 * 4.60 + 10 * 0.10
az_reg = (730 / 24) * 0.1666 + 10 * 0.10
az_egr = (500 - 100) * 0.181
az_oth = 2 * 0.005 * H
az_dep = aws_dep

# Google Cloud southamerica-east1.
gcp_vm = 0.1064 * H
gcp_disk = 50 * 0.17
gcp_fe = gcp_vm + gcp_disk
gcp_be = 2 * (gcp_vm + gcp_disk)
gcp_rb = gcp_fe
gcp_my = 0.2605 * H + 100 * 0.17
gcp_lb = 0.025 * H + 1000 * 0.008
gcp_mon = 0.0
gcp_reg = 19.5 * 0.10
gcp_egr = 500 * 0.19
gcp_nat = 3 * 0.0014 * H + 20 * 0.045 + 0.005 * H
gcp_oth = gcp_nat + 0.005 * H
gcp_dep = aws_dep

# Vultr São Paulo. El mes publicado ya es el tope de una instancia encendida.
vu_fe = 40.0
vu_be = 120.0
vu_rb = 40.0
vu_my = 720.0
vu_lb = 10.0
vu_mon = 0.0
vu_reg = 20 * 0.25
vu_egr = 0.0
vu_oth = 0.03 * 672
vu_dep = aws_dep

add("Frontend", [aws_fe, az_fe, gcp_fe, vu_fe])
add("Backend (2 instancias)", [aws_be, az_be, gcp_be, vu_be])
add("RabbitMQ", [aws_rb, az_rb, gcp_rb, vu_rb])
add("MySQL gestionado", [aws_my, az_my, gcp_my, vu_my])
add("Balanceador de carga", [aws_lb, az_lb, gcp_lb, vu_lb])
add("Monitoreo y alertas", [aws_mon, az_mon, gcp_mon, vu_mon])
add("Registro de imágenes", [aws_reg, az_reg, gcp_reg, vu_reg])
add("Transferencia de salida", [aws_egr, az_egr, gcp_egr, vu_egr])
add("Otros (IP, NAT, respaldos)", [aws_oth, az_oth, gcp_oth, vu_oth])
add("Despliegue automatizado", [aws_dep, az_dep, gcp_dep, vu_dep])

TOTALS = [row_sum(LINES, i) for i in range(4)]
ANNUAL = [value * 12 for value in TOTALS]


class Informe(FPDF):
    def header(self):
        self.set_font("Arial", "B", 9)
        self.set_text_color(80, 80, 80)
        self.cell(
            0,
            6,
            "FET - Optativa IV | Taller de investigación 2 - Cotizacion en la nube",
            align="C",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        self.ln(1)

    def footer(self):
        self.set_y(-12)
        self.set_font("Arial", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"Página {self.page_no()}/{{nb}}", align="C")

    def section(self, title):
        self.ln(1)
        self.set_x(self.l_margin)
        self.set_font("Arial", "B", 13)
        self.set_text_color(20, 60, 120)
        self.multi_cell(0, 7, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def body(self, text):
        self.set_x(self.l_margin)
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 5.4, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def bullet(self, text):
        self.set_x(self.l_margin)
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 5.4, f"- {text}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def table(self, headers, rows, widths, font=7):
        self.set_font("Arial", "B", font)
        self.set_fill_color(20, 60, 120)
        self.set_text_color(255, 255, 255)
        for index, header in enumerate(headers):
            self.cell(widths[index], 7, header, border=1, fill=True, align="C")
        self.ln()
        self.set_text_color(0, 0, 0)
        self.set_font("Arial", "", font)
        for row_index, row in enumerate(rows):
            if row_index >= len(rows) - 2:
                self.set_font("Arial", "B", font)
            else:
                self.set_font("Arial", "", font)
            for index, cell in enumerate(row):
                align = "L" if index == 0 else "R"
                self.cell(widths[index], 6.2, cell, border=1, align=align)
            self.ln()
        self.ln(2)

    def shot(self, title, path):
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
    pdf = Informe(format="A4")
    pdf.add_font("Arial", "", FONT)
    pdf.add_font("Arial", "B", FONT_B)
    pdf.add_font("Arial", "I", FONT_I)
    pdf.alias_nb_pages()
    pdf.set_margins(14, 14, 14)
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()

    pdf.set_font("Arial", "B", 15)
    pdf.multi_cell(
        0,
        7,
        "Cotización comparativa del despliegue en nube de un sistema dockerizado",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(
        0,
        6,
        "Taller de investigación n.o 2\n"
        "Optativa IV - Sistemas de Tiempo Real Distribuidos\n"
        "Fundación Escuela Tecnológica de Neiva (FET)\n"
        "Elaborado por: Edwin Samir Cortés Olaya y Jorge Armando Olaya Ortiz\n"
        "Docente: Juan Carlos Polanía Cortés\n"
        "Consulta de precios: 27 de octubre de 2026. Montos en USD, sin IVA.",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.ln(1)

    low = min(TOTALS)
    high = max(TOTALS)
    gap = (high - low) / low * 100
    names = ["AWS", "Azure", "Google Cloud", "Vultr"]
    cheapest = names[TOTALS.index(low)]
    dearest = names[TOTALS.index(high)]

    pdf.section("1. Conclusión")
    pdf.body(
        f"Con la especificación común y pago bajo demanda, la opción más baja es "
        f"{cheapest}, con {money(low)} USD al mes ({money(low * 12)} USD al año). "
        f"La más alta es {dearest}, con {money(high)} USD al mes. La diferencia es "
        f"{money(gap)} por ciento. En Azure el balanceador de capa 7 explica casi toda "
        f"esa distancia: el cargo fijo de Application Gateway queda en {money(az_lb)} USD, "
        f"frente a {money(aws_lb)} USD en AWS y {money(gcp_lb)} USD en Google Cloud."
    )
    pdf.body(
        "La recomendacion es Google Cloud en São Paulo, con las máquinas, el Cloud SQL "
        "zonal y el balanceador HTTP de este informe, mientras el tráfico de salida siga "
        "cerca de 500 GB al mes. Deja de ser la opción más baja si el tráfico sube a 2 TB "
        "y, sobre todo, si se acepta en Vultr el plan de MySQL de 2 vCPU y 50 GB, que no "
        "cumple el disco de 100 GB pedido. Ese caso se detalla en el analisis."
    )

    pdf.section("2. Especificación comun y supuestos")
    pdf.body(
        "Las cuatro cotizaciones usan la misma carga: un frontend de 2 vCPU y 4 GB, "
        "dos backends de 2 vCPU y 8 GB, un RabbitMQ de 2 vCPU y 4 GB, discos de 50 GB "
        "en esas instancias, MySQL gestionado de 2 vCPU y 8 GB con 100 GB y respaldo "
        "de 7 días sin alta disponibilidad, un balanceador HTTP con 1 TB procesado, "
        "10 GB de registros, 50 métricas, 10 alertas por correo, 20 GB de imágenes y "
        "500 GB de salida a internet. El mes de operación es de 730 horas, salvo Vultr, "
        "que factura el mes completo con tope de 672 horas y por eso se usa el precio "
        "mensual publicado. La región es la más cercana a Colombia que ofrece cada uno. "
        "Cuando no existe el tamaño exacto, se toma el inmediatamente superior y se declara."
    )
    pdf.bullet("Arquitectura de red, igual en los cuatro: el frontend tiene IP pública. Los dos backends, RabbitMQ y MySQL van en red privada. Una pasarela NAT les da salida. No hay trafico entre zonas porque todo queda en una sola zona.")
    pdf.bullet("El tráfico de 1 TB del balanceador y los 500 GB de salida a internet se cotizan como rubros distintos, como pide la tabla. Parte de esos bytes puede ser el mismo paquete visto dos veces; el análisis lo advierte.")
    pdf.bullet("Por la NAT se asumen 20 GB al mes de parches y bajada de imágenes. No estan dentro de los 500 GB de salida de los usuarios.")
    pdf.bullet("Los precios de lista estan en dólares y no incluyen IVA de Colombia (19 por ciento). Ninguna calculadora consultada lo agrega para una factura local.")
    pdf.bullet("No se descuenta credito de prueba ni la capa gratuita de los primeros 12 meses. Si se usa una franquicia permanente, se dice cual es.")
    pdf.bullet("1 TB de trafico procesado se toma como 1.000 GB, no como 1.024 GiB.")

    pdf.section("3. Equivalencias por proveedor")
    pdf.bullet("AWS, São Paulo (sa-east-1). Frontend y RabbitMQ: t3.medium, 2 vCPU y 4 GB, mas 50 GB gp3. Backends: dos t3.large, 2 vCPU y 8 GB, mas 50 GB gp3 cada uno. MySQL: RDS db.t3.large, una zona, 100 GB gp3, retención de respaldos 7 días. Balanceador: Application Load Balancer. Registro: ECR. Monitoreo: CloudWatch y una notificación por correo en SNS.")
    pdf.bullet("Azure, Brazil South. Frontend y RabbitMQ: Standard_B2s, 2 vCPU y 4 GB. Backends: dos Standard_B2ms, 2 vCPU y 8 GB. El disco de 50 GB no existe: el Standard SSD E6 LRS es de 64 GB y es el tamaño siguiente. MySQL Flexible Server Burstable B2ms, 100 GB, sin zona redundante. Balanceador: Application Gateway, cargo fijo Standard de 0,40 USD por hora y unidad de capacidad de 0,0144 USD por hora, leidos en la API de precios al por menor.")
    pdf.bullet("Google Cloud, São Paulo (southamerica-east1). No se uso un tipo de 4 GB dedicado. Frontend y RabbitMQ suben a e2-standard-2, que trae 2 vCPU y 8 GB. Los backends usan el mismo tipo, que si coincide. MySQL: el db-n1-standard-2 de la region trae 7,5 GB, por debajo de 8 GB. Se toma el siguiente, db-n1-highmem-2, con 2 vCPU y 13 GB, a 0,2605 USD por hora. Disco SSD de referencia: 0,17 USD por GB al mes, tarifa publicada en la página de Cloud SQL. Balanceador HTTP regional: 0,025 USD por hora por la regla de reenvio y 0,008 USD por GB procesado de entrada.")
    pdf.bullet("Vultr, São Paulo, cuarta nube. Frontend y RabbitMQ: plan voc-c-2c-4gb-50s-amd, 2 vCPU, 4 GB y 50 GB, 40 USD al mes. Backends: dos voc-g-2c-8gb-50s-amd, 2 vCPU, 8 GB y 50 GB, 60 USD cada uno. MySQL gestionado no tiene 2 vCPU, 8 GB y 100 GB. El plan de 2 vCPU, 8 GB y 50 GB cuesta 180 USD y se queda corto de disco. El inmediatamente superior que si cubre 100 GB es 8 vCPU, 32 GB y 160 GB, sin replicas, a 720 USD. Ese es el valor de la tabla. El balanceador gestionado de Vultr es de capa 4, no de capa 7, a 10 USD al mes, y no cobra el tráfico que pasa por el. No hay registro de imágenes: los 20 GB se cotizan en GitHub Packages.")

    pdf.section("4. Tabla comparativa mensual")
    pdf.body("Montos en dólares por mes. El anual es el mensual por 12.")
    headers = ["Concepto", "AWS", "Azure", "Google", "Vultr"]
    widths = [62, 29, 29, 29, 29]
    rows = []
    for label, values in LINES:
        rows.append([label] + [money(value) for value in values])
    rows.append(["TOTAL MENSUAL"] + [money(value) for value in TOTALS])
    rows.append(["TOTAL ANUAL"] + [money(value) for value in ANNUAL])
    pdf.table(headers, rows, widths, font=8)

    pdf.section("5. Comparacion no monetaria")
    headers = ["Aspecto", "AWS", "Azure", "Google", "Vultr"]
    rows = [
        ["Region", "São Paulo", "Brazil South", "São Paulo", "São Paulo"],
        ["RabbitMQ", "VM propia", "VM propia", "VM propia", "VM propia"],
        ["MySQL", "RDS zonal", "Flexible zonal", "Cloud SQL zonal", "Gestionado, salto de tamano"],
        ["Balanceador", "HTTP, capa 7", "HTTP, capa 7", "HTTP, capa 7", "Capa 4, no es HTTP"],
        ["Despliegue", "GitHub o CodeBuild", "GitHub o Pipelines", "GitHub o Cloud Build", "Solo GitHub"],
        ["Capa gratuita permanente", "100 GB de salida, 10 métricas, 10 alarmas, 5 GB de logs", "100 GB de salida y 5 GB de logs", "50 GB de logs y 0,5 GB de registro", "Ancho de banda incluido en el plan"],
    ]
    pdf.table(headers, rows, [32, 37, 37, 37, 35], font=6.5)
    pdf.body(
        "Ninguna de las cuatro cotizaciones usa RabbitMQ gestionado. Amazon MQ existe "
        "en AWS, pero el broker no se vende en el tamano fijo de 2 vCPU, 4 GB y 50 GB "
        "de la especificación, asi que las cuatro quedan con el broker instalado en la "
        "maquina. Eso implica parches, disco persistente y recuperacion a cargo de quien "
        "opera el sistema, no del proveedor."
    )

    pdf.section("6. Costos que no están en la portada")
    pdf.bullet(f"Salida a internet. AWS: los primeros 100 GB del mes son gratuitos de forma permanente y el resto, en São Paulo, sale a 0,25 USD por GB. 400 GB por 0,25 son {money(aws_egr)} USD. Azure, con la ruta por la red de Microsoft, que es la predeterminada: también 100 GB gratis y luego 0,181 USD por GB, {money(az_egr)} USD. La ruta por internet publico bajaria a 0,12 USD por GB, pero hay que elegirla. Google, hacia Sudamerica: 0,19 USD por GB desde el primer GB, {money(gcp_egr)} USD. Vultr no cobra los 500 GB: cada instancia Optimized incluye 5.120 GB y la cuenta suma 2 TB gratis. El excedente seria 0,01 USD por GB.")
    pdf.bullet("Trafico entre zonas: 0 USD en los cuatro, porque la cotizacion es de una sola zona. En Azure el GB entre zonas de la misma region esta a 0,01 USD; no se usa.")
    pdf.bullet(f"IP pública. AWS cobra 0,005 USD por hora también si esta en uso. Se cuentan tres: frontend, NAT y balanceador, {money(3 * 0.005 * H)} USD, ya dentro de otros costos. Azure Standard IPv4 estatica: el mismo 0,005 USD por hora. Se cuentan dos, {money(az_oth)} USD, porque el frontend del gateway no salio como IP aparte. Google cobra la IP en uso; la regla del balanceador no paga otra IP. Vultr incluye una IPv4 en el plan.")
    pdf.bullet(f"NAT. AWS: 0,093 USD por hora mas 0,093 USD por GB. Con 20 GB son {money(0.093 * H + 20 * 0.093)} USD. Google, con el ejemplo de la página de precios: 0,0014 USD por hora por cada VM que la usa, 0,045 USD por GB y 0,005 USD por hora de la IP, {money(gcp_nat)} USD. Vultr: 0,03 USD por hora por 672 horas, {money(vu_oth)} USD. En Azure la API de precios no devolvio un medidor llamado NAT Gateway para Brazil South el 27 de octubre de 2026. No se inventa esa cifra. El total de Azure no la trae y puede subir unas decenas de dólares si el medidor aparece aparte.")
    pdf.bullet("Respaldos. En RDS el almacenamiento de backup es gratis hasta el tamano de la base, 100 GB. Con 7 días se asume que cabe y el extra es 0. En Azure el GB de backup LRS vale 0,095 USD, pero solo por encima del almacenamiento aprovisionado; también queda en 0. En Cloud SQL la pagina marca gratis la recuperacion a un punto en el tiempo hasta 7 días en la edicion Enterprise. En Vultr el plan gestionado no separa la retención; no se suma un 20 por ciento, que es el recargo de las copias automaticas de una VM, no de la base gestionada.")
    pdf.bullet(f"Registros. CloudWatch en São Paulo cobra 0,90 USD por GB ingerido y 0,0408 USD por GB al mes guardado. La franquicia permanente deja libres 5 GB de ingesta, 5 GB de archivo, 10 métricas y 10 alarmas. De los 10 GB se pagan 5, de las 50 métricas se pagan 40 a 0,30 USD, y las 10 alarmas quedan en 0. Total {money(aws_mon)} USD. El correo de SNS cabe en las primeras 1.000 notificaciónes, que son gratis. Azure Log Analytics cobra 4,60 USD por GB ingerido y regala 5 GB; las 10 alertas de metrica salen a 0,10 USD cada una. Total {money(az_mon)} USD. La retención de 30 dias no se cobra aparte. Google Logging regala 50 GB al mes, asi que 10 GB salen en 0. Vultr no vende ese paquete: el monitoreo basico va dentro de la VM y la celda queda en 0, con el hueco declarado.")

    pdf.section("7. Despliegue automatizado")
    pdf.body(
        "El flujo esta en .github/workflows/deploy.yml. En cada push a main, un ejecutor "
        "Linux de GitHub con 2 nucleos (ubuntu-latest) baja el codigo, construye la imagen, "
        "la publica y actualiza el despliegue. El supuesto obligatorio es 60 ejecuciones "
        "al mes, 12 minutos cada una, 720 minutos, repositorio privado, y 3 GB de artefactos."
    )
    pdf.body(
        "Se consulta el plan GitHub Free el 27 de octubre de 2026 (GitHub, 2026). "
        "Incluye 2.000 minutos al mes y 500 MB de almacenamiento compartido entre "
        "artefactos y GitHub Packages. El minuto adicional del Linux de 2 nucleos cuesta "
        "0,006 USD. Los 720 minutos caben en los 2.000, asi que los minutos salen en 0. "
        "Duplicar a 120 ejecuciones son 1.440 minutos y siguen dentro de la franquicia, "
        "también en 0. El minuto que si se cobraria, a partir del minuto 2.001, vale 0,006 USD."
    )
    pdf.body(
        f"Los artefactos si se pasan: 3 GB menos 0,5 GB incluidos son 2,5 GB a 0,25 USD "
        f"por GB al mes, {money(aws_dep)} USD. Ese valor es el de la fila de despliegue "
        "en las cuatro columnas, porque el flujo elegido es GitHub Actions en todas. "
        "En Vultr, además, los 20 GB de imágenes van a GitHub Packages y se suman en la "
        f"fila del registro, a 0,25 USD por GB, porque Vultr no tiene registro propio. "
        "La franquicia de 500 MB ya se uso en los artefactos."
    )
    pdf.body(
        "El mismo flujo en la integracion del proveedor, en vez de GitHub, quedaria asi. "
        "AWS CodeBuild, maquina Linux general1.small de 2 vCPU: 0,005 USD por minuto, "
        "720 por 0,005 son 3,60 USD. No se resta la prueba de 100 minutos, porque es de "
        "los primeros 12 meses y no es permanente. Azure Pipelines, con el plan gratuito, "
        "incluye 1.800 minutos al mes de agente hospedado por Microsoft; 720 caben y el "
        "costo es 0. Google Cloud Build incluye 2.500 minutos al mes; 720 caben y el "
        "costo es 0. Vultr no tiene un servicio equivalente: el flujo seguiria en GitHub."
    )
    pdf.body(
        "Publicar la imagen dentro de la region no es salida a internet. La bajada de la "
        "imagen hacia las instancias privadas entra en los 20 GB que ya se cargaron a la NAT. "
        "No se suma otro rubro de trafico por el despliegue."
    )

    pdf.section("8. De donde sale cada cifra")
    pdf.bullet("AWS. Archivos de lista de precios de EC2, RDS, VPC, CloudWatch y ECR para sa-east-1, con fecha de vigencia 1 de octubre de 2026, consultados el 27 de octubre de 2026. t3.medium 0,0672 USD por hora. t3.large 0,1344. gp3 0,152 USD por GB al mes. RDS MySQL db.t3.large Single-AZ 0,280 USD por hora. gp3 de RDS 0,219 USD por GB. ALB 0,034 USD por hora y 0,011 USD por LCU-hora. Con 1.000 GB en el mes, el LCU de bytes es 1.000 por 0,011. NAT 0,093 USD por hora y por GB. IPv4 en uso 0,005 USD por hora. Salida: 0,25 USD por GB después del GB 1 en la lista, y 100 GB permanentes gratis segun la página de EC2. ECR 0,10 USD por GB.")
    pdf.bullet("Azure. API de precios al por menor, region brazilsouth, tipo Consumption, el 27 de octubre de 2026. B2s 0,0672 USD por hora. B2ms 0,134. Disco E6 LRS 8,96 USD al mes. MySQL Flexible B2ms 0,28 USD por hora. Almacenamiento 0,2185 USD por GB. Salida por la red de Microsoft: 0 hasta 100 GB y 0,181 USD desde ahi. IP Standard 0,005 USD por hora. Registro Basic 0,1666 USD por dia mas 0,10 USD por GB por encima de los 10 GB incluidos. Logs 4,60 USD por GB. Alerta de metrica 0,10 USD al mes. Gateway: medidor Standard Fixed Cost 0,40 USD por hora y Standard Capacity Units 0,0144 USD por hora. La unidad de capacidad se estima con el rendimiento: 1.000 GB al mes son 3,04 Mbps, y cada unidad cubre 2,22 Mbps, asi que hacen falta 1,37 unidades.")
    pdf.bullet("Google. e2-standard-2 en southamerica-east1: 0,1064 USD por hora (indice de precios de la region, 27 de octubre de 2026). Cloud SQL db-n1-highmem-2 en la misma region: 0,2605 USD por hora. SSD 0,17 USD por GB al mes, página de Cloud SQL. Salida, balanceador, NAT e IP: página de precios de red de Google Cloud, consultada el mismo dia. La tabla de salida que incluye a São Paulo cobra 0,19 USD por GB hacia Sudamerica. El ejemplo de Cloud NAT de esa pagina usa 0,0014 USD por hora por VM, 0,045 USD por GB y 0,005 USD por hora de IP. Logging: 50 GB de ingesta gratis al mes. Artifact Registry: 0,10 USD por GB después de 0,5 GB.")
    pdf.bullet("Vultr. API publica de planes con ubicacion sao, y la página de precios, el 27 de octubre de 2026. MySQL de 8 vCPU, 32 GB, 160 GB y 0 replicas: 720 USD. Balanceador: 10 USD al mes. NAT: 0,03 USD por hora. El mes de facturacion de estas instancias se capa en 672 horas. Ancho de banda de sobra: 0,01 USD por GB solo si se pasa la cuota. Preguntas frecuentes de Vultr para el excedente, la capa del balanceador y el mes de 672 horas.")
    pdf.body(
        "Las capturas de AWS salen de la calculadora pública (calculator.aws), región "
        "South America (São Paulo), Linux, uso constante y pago bajo demanda, el 27 de "
        "octubre de 2026. La barra inferior muestra el total mensual del servicio. "
        "Las de Vultr salen de la página pública de precios, en la familia Optimized "
        "Cloud Compute. Azure y Google no quedaron en una captura de este informe: "
        "sus cifras siguen saliendo de la API y de las páginas citadas arriba, no de "
        "un pantallazo. No se guardó el enlace para compartir de la calculadora de AWS."
    )
    shots = ROOT / "docs" / "cotizacion"
    pdf.shot(
        "Figura 1. AWS, frontend. Calculadora pública, 27 de octubre de 2026. "
        "São Paulo, Linux, 1 instancia, uso constante. Total mensual 56,66 USD.",
        shots / "aws calculadora frontend region sao paulo.png",
    )
    pdf.shot(
        "Figura 2. AWS, frontend. Instancia elegida t3.medium, 2 vCPU y 4 GB, "
        "disco gp3. Bajo demanda 49,06 USD y disco 7,60 USD. Total 56,66 USD.",
        shots / "aws calculadora frontend t3 medium.png",
    )
    pdf.shot(
        "Figura 3. AWS, backend. São Paulo, Linux, 2 instancias, uso constante. "
        "Total mensual 211,42 USD. 27 de octubre de 2026.",
        shots / "aws calculadora backend region sao paulo.png",
    )
    pdf.shot(
        "Figura 4. AWS, backend. Instancia t3.large, 2 vCPU y 8 GB, cantidad 2. "
        "Total mensual 211,42 USD.",
        shots / "aws calculadora backend t3 large sao paulo.png",
    )
    pdf.shot(
        "Figura 5. AWS, RabbitMQ. São Paulo, Linux, 1 instancia. El tipo de esa "
        "misma pantalla es t3.medium, 2 vCPU y 4 GB, el de la figura 2. Total 56,66 USD.",
        shots / "aws calculadora rabbitmq sao paulo.png",
    )
    pdf.shot(
        "Figura 6. Vultr, Optimized Cloud Compute, CPU Optimized. 2 vCPU, 4 GB, "
        "50 GB y 5 TB, 40,00 USD al mes. Sirve para el frontend y para RabbitMQ. "
        "Página de precios, 27 de octubre de 2026.",
        shots / "vultr optimized cpu 2 vcpu 4 gb 50 gb.png",
    )
    pdf.shot(
        "Figura 7. Vultr, Optimized Cloud Compute, General Purpose. 2 vCPU, 8 GB "
        "y 50 GB, 60,00 USD al mes. Son las dos instancias del backend. "
        "Página de precios, 27 de octubre de 2026.",
        shots / "vultr optimized general purpose 2 vcpu 8 gb.png",
    )
    pdf.shot(
        "Figura 8. Vultr, MySQL gestionado, Optimized Cloud Compute. El plan de "
        "2 vCPU, 8 GB y 50 GB sin réplicas cuesta 180 USD y no cumple el disco de 100 GB.",
        shots / "vultr mysql gestionado planes.png",
    )
    pdf.shot(
        "Figura 9. Vultr, MySQL gestionado. El plan que sí cubre 100 GB es el de "
        "8 vCPU, 32 GB y 160 GB, sin réplicas, a 720 USD al mes.",
        shots / "vultr mysql gestionado plan 720.png",
    )

    pdf.section("9. Analisis")
    aws_compute = aws_fe + aws_be + aws_rb
    az_compute = az_fe + az_be + az_rb
    gcp_compute = gcp_fe + gcp_be + gcp_rb
    vu_compute = vu_fe + vu_be + vu_rb
    pdf.body(
        f"1. Entre {dearest} ({money(high)} USD) y {cheapest} ({money(low)} USD) hay "
        f"{money(gap)} por ciento. El componente que explica la mayor parte es el balanceador. "
        f"Azure suma {money(az_lb)} USD por el cargo fijo de Application Gateway. "
        f"Google suma {money(gcp_lb)} USD y AWS {money(aws_lb)} USD por el mismo papel. "
        f"La resta de los balanceadores, unos {money(az_lb - gcp_lb)} USD, cubre casi toda "
        f"la distancia entre el total mas alto y el más bajo. El segundo salto grande esta "
        f"en Vultr, y no es el balanceador: es MySQL, por subir de un plan de 2 vCPU y 50 GB "
        f"(180 USD, que no cumple) a uno de 8 vCPU, 32 GB y 160 GB (720 USD)."
    )
    pdf.body(
        f"2. El computo de las instancias, con su disco, pesa asi sobre el total: "
        f"AWS {money(100 * aws_compute / TOTALS[0])} por ciento "
        f"({money(aws_compute)} de {money(TOTALS[0])}), "
        f"Azure {money(100 * az_compute / TOTALS[1])} por ciento, "
        f"Google {money(100 * gcp_compute / TOTALS[2])} por ciento y "
        f"Vultr {money(100 * vu_compute / TOTALS[3])} por ciento. "
        f"En AWS y en Google el computo es una parte grande, pero MySQL y la salida también "
        f"pesan. En Azure el computo no es lo que manda: el gateway es más caro que las "
        f"cuatro máquinas juntas. En Vultr el computo de frontend, backends y RabbitMQ "
        f"son 200 USD, y MySQL son 720 USD. El gasto no está en las máquinas del CRUD."
    )
    egr_2tb = [
        (2000 - 100) * 0.25,
        (2000 - 100) * 0.181,
        2000 * 0.19,
        0.0,
    ]
    tot_2tb = [TOTALS[i] - [aws_egr, az_egr, gcp_egr, vu_egr][i] + egr_2tb[i] for i in range(4)]
    order_500 = ", ".join(names[i] for i in sorted(range(4), key=lambda i: TOTALS[i]))
    order_2000 = ", ".join(names[i] for i in sorted(range(4), key=lambda i: tot_2tb[i]))
    pdf.body(
        f"3. Si, Vultr cobra la salida de otra manera: 500 GB caben en la cuota y el rubro "
        f"es 0, mientras AWS cobra {money(aws_egr)} USD, Azure {money(az_egr)} USD y Google "
        f"{money(gcp_egr)} USD. AWS es el GB más caro de los tres que si facturan (0,25 USD "
        f"después de 100 GB). Con 2 TB al mes la salida pasaria a {money(egr_2tb[0])} USD en AWS, "
        f"{money(egr_2tb[1])} en Azure, {money(egr_2tb[2])} en Google y seguiria en 0 en Vultr, "
        f"porque 2 TB siguen dentro de los 5,12 TB de cada instancia. El orden con 500 GB es "
        f"{order_500}. Con 2 TB seria {order_2000}. Vultr adelanta a Google porque deja de "
        f"pagar un rubro que en los otros crece, aunque su MySQL siga en 720 USD."
    )
    pdf.body(
        "4. El proveedor más caro es Azure. Los tamanos B2s y B2ms son de rafaga y la API "
        "de precios consultada no trae una tarifa de un ano para ellos ni para el Application "
        "Gateway. El rubro que más pesa, el gateway, se queda en pago por uso. Por eso un "
        "compromiso de un ano, con los productos de esta cotizacion, no baja el total: sigue "
        f"en {money(TOTALS[1])} USD al mes. Si mas adelante se cambiaran las máquinas a una "
        "familia que si tenga reserva, el descuento pegaria en el computo y en MySQL, no en "
        "los cerca de 300 USD del balanceador, y Azure seguiria por encima de Google."
    )
    pdf.body(
        "5. Con esta especificación los cuatro instalan RabbitMQ en una maquina propia. "
        "AWS es el unico que además vende el broker gestionado, Amazon MQ, pero en tipos de "
        "broker distintos al de 2 vCPU, 4 GB y 50 GB, asi que no entra en la tabla. Azure, "
        "Google y Vultr no tienen un RabbitMQ gestionado de primera mano. La diferencia, "
        "mas alla del precio, es quien responde cuando el disco se llena o el proceso se cae: "
        "en la maquina propia es la operacion del sistema; en Amazon MQ seria el proveedor, "
        "con otro tamaño y otra factura. El precio de la fila RabbitMQ no compra esa operacion."
    )
    half = 365 / 730
    pdf.body(
        "6. Si el sistema solo estuviera encendido 12 horas al dia, serian 365 horas en vez "
        "de 730. Bajan el frontend, los backends, RabbitMQ, la NAT, las IP que solo se cobran "
        "con la maquina encendida y el computo de MySQL, porque RDS, Flexible Server y Cloud "
        "SQL se pueden detener y dejan de cobrar la hora. No bajan los discos, el almacenamiento "
        "de la base, el registro de imágenes, la salida a internet (se mantienen los 500 GB del "
        "enunciado) ni el cargo fijo del balanceador si el servicio sigue creado. En Vultr el "
        "precio mensual es un tope: apagar 12 horas sí baja la factura, porque alli se cobra "
        "la hora hasta llegar a ese tope. Un orden de magnitud, solo en las máquinas de AWS, "
        f"el computo de instancias pasaria de {money(aws_compute)} USD a cerca de "
        f"{money(aws_compute * half)} USD. La salida de {money(aws_egr)} USD no se mueve."
    )
    pdf.body(
        "7. Recomiendo Google Cloud en São Paulo para esta especificación y estos supuestos: "
        "pago por uso, una sola zona, usuarios en Colombia y 500 GB de salida al mes. Es el "
        "total más bajo que además tiene balanceador HTTP y un MySQL gestionado cercano a "
        "2 vCPU y 8 GB. Deja de serlo si el tráfico de salida se acerca a 2 TB, porque Vultr "
        "incluye ese ancho de banda, o si se acepta el MySQL de Vultr de 50 GB a 180 USD en "
        "lugar del plan de 720 USD. Tambien deja de serlo si Azure reemplaza Application "
        "Gateway por un balanceador más simple: el resto de Azure ya esta en el mismo rango "
        "que AWS. No recomendaria Vultr como está en la tabla, aunque las máquinas salen "
        "baratas, porque el MySQL que cumple los 100 GB multiplica el tamano y el balanceador "
        "no es de capa 7."
    )

    pdf.section("10. Referencias")
    pdf.body(
        "Amazon Web Services. (2026). AWS price list: Amazon EC2, Amazon RDS, Amazon VPC, "
        "Amazon CloudWatch y Amazon ECR, region South America (São Paulo), oferta con vigencia "
        "del 1 de octubre de 2026. https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/"
    )
    pdf.body(
        "Amazon Web Services. (2026). Amazon EC2 on-demand pricing. "
        "https://aws.amazon.com/ec2/pricing/on-demand/"
    )
    pdf.body(
        "Amazon Web Services. (2026). Amazon CloudWatch pricing. "
        "https://aws.amazon.com/cloudwatch/pricing/"
    )
    pdf.body(
        "GitHub. (2026). GitHub Actions billing. "
        "https://docs.github.com/en/billing/concepts/product-billing/github-actions"
    )
    pdf.body(
        "GitHub. (2026). Actions runner pricing. "
        "https://docs.github.com/en/billing/reference/actions-minute-multipliers"
    )
    pdf.body(
        "Google Cloud. (2026). Virtual Private Cloud pricing. "
        "https://cloud.google.com/vpc/network-pricing"
    )
    pdf.body(
        "Google Cloud. (2026). Cloud SQL pricing. https://cloud.google.com/sql/pricing"
    )
    pdf.body(
        "Microsoft. (2026). Azure Retail Prices API. "
        "https://prices.azure.com/api/retail/prices"
    )
    pdf.body(
        "Vultr. (2026). Pricing. https://www.vultr.com/pricing/"
    )
    pdf.body(
        "Vultr. (2026). Frequently asked questions. https://www.vultr.com/resources/faq/"
    )
    pdf.body(
        "Vultr. (2026). Plans API, region sao. https://api.vultr.com/v2/plans"
    )

    pdf.section("11. Declaracion de uso de inteligencia artificial")
    pdf.body(
        "Se utilizó Cursor, con el modelo Grok, para leer el taller, consultar las listas de "
        "precios y la API de Azure, calcular los totales, tomar las capturas de la calculadora "
        "de AWS y de la página de precios de Vultr, y redactar este informe y el archivo "
        ".github/workflows/deploy.yml."
    )
    pdf.bullet("La herramienta armó las consultas a los archivos de precios de AWS y a la API de Azure, y leyó las páginas de GitHub, Google Cloud y Vultr.")
    pdf.bullet("Los montos no se estimaron a ojo: cada uno sale de una tarifa citada en la sección 8. Donde la fuente no devolvió el medidor, la celda no se rellenó con un número inventado. Es el caso de la NAT de Azure.")
    pdf.bullet("Las figuras 1 a 5 son la calculadora de AWS y las figuras 6 a 9 son la página de precios de Vultr. Azure y Google no tienen captura en este informe.")
    pdf.body(
        "Edwin Samir Cortés Olaya y Jorge Armando Olaya Ortiz revisan las tarifas, la elección de Vultr como cuarta nube "
        "y la recomendación, y responden por el documento."
    )

    pdf.output(str(OUT))
    print(f"PDF: {OUT}")
    print("TOTALES", [round(v, 2) for v in TOTALS])
    print("GAP", round(gap, 2))
    print("AZ_CU", round(az_cu, 3), "AZ_LB", round(az_lb, 2))


if __name__ == "__main__":
    build()
