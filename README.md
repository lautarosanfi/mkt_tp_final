# TP Final — Ecosistema de Datos (EcoBottle AR)

> **Introducción al Marketing Online y los Negocios Digitales — Trabajo Práctico Final**  
> Mini–ecosistema de datos comercial (online + offline) + dashboard de KPIs.

## 0) Contenidos
- [0) Contenidos](#0-contenidos)
- [1) Descripción y Objetivos](#1-descripción-y-objetivos)
- [2) Diccionario de Datos y Modelo](#2-diccionario-de-datos-y-modelo)
- [3) Estructura del Repositorio](#3-estructura-del-repositorio)
- [4) Requisitos e Instalación](#4-requisitos-e-instalación)
- [5) Pipeline ETL (scripts)](#5-pipeline-etl-scripts)
- [6) Cómo ejecutar el proyecto](#6-cómo-ejecutar-el-proyecto)
- [7) Dashboard en Looker Studio](#7-dashboard-en-looker-studio)
- [8) Buenas prácticas de repositorio](#8-buenas-prácticas-de-repositorio)
- [9) Créditos y Licencia](#9-créditos-y-licencia)

---

## 1) Descripción y Objetivos

Este proyecto implementa un *data warehouse* (DW) liviano en formato CSV a partir de datos RAW provistos, y construye un tablero con **KPIs** para el área comercial: **Ventas**, **Usuarios Activos**, **Ticket Promedio**, **NPS**, **Ventas por Provincia** y **Ranking Mensual por Producto**. El caso de uso es **EcoBottle AR** (ventas online y 4 tiendas físicas).

**Entregables principales**:
- Scripts de carga/transformación (ETL) que generan dimensiones y hechos en `DW/`.
- **README** (este documento) con instrucciones, supuestos, diccionario y consultas.
- **Dashboard** final en Looker Studio con filtros por fecha, canal, provincia y producto.

---

## 2) Diccionario de Datos y Modelo

> **Nota:** A continuación se incluye íntegramente el diseño de modelo estrella y el diccionario de datos preparado para este trabajo.  
> Si preferís verlo como documento aparte, puede moverse a `/docs/diccionario.md`.

### 📖 2. Diccionario de Datos y Modelo

A continuación, se detalla el Esquema Estrella (modelo Kimball) diseñado para este proyecto. Se definen los supuestos clave, las dimensiones de conformación y las tablas de hechos que almacenarán las métricas del negocio.

#### Supuestos y Decisiones de Modelado

1.  **Claves (Keys):**
    * **Surrogate Keys (SK):** Se generan claves sustitutas (ej: `cliente_sk`, `producto_sk`) para las dimensiones principales (`Dim_Cliente`, `Dim_Producto`, `Dim_Geografia`). Esto permite manejar cambios a lo largo del tiempo (Slowly Changing Dimensions) y desvincular el DW de las claves operacionales de `RAW`.
    * **Business Keys (BK):** Se conservan las claves originales (ej: `customer_id`, `product_id`) como atributos en las dimensiones para trazabilidad y referencia.
    * **Fact Keys:** Las tablas de hechos usan las PK originales del sistema `RAW` (ej: `order_id`, `session_id`) como su propia Primary Key, ya que el grano es el mismo.

2.  **Dimensión de Tiempo (`Dim_Tiempo`):**
    * Esta es una **dimensión de conformación** generada por el script de ETL, ya que no existe en los datos `RAW`.
    * Todas las tablas de hechos se vinculan a esta dimensión a través de sus respectivos campos de fecha (ej: `order_date`, `started_at`, `paid_at`).
    * La PK (`tiempo_id`) es un entero con formato `YYYYMMDD` para facilitar los `JOINs`.

3.  **Manejo de Nulos / Anónimos:**
    * Las tablas `web_session` y `nps_response` permiten un `customer_id` nulo.
    * Para manejar esto, `Dim_Cliente` contendrá un registro especial (ej: `cliente_sk = -1`) con el valor "Cliente Desconocido / Anónimo". Las FKs en `Fact_Sesiones` y `Fact_NPS` apuntarán a este registro cuando el `customer_id` sea `NULL`.

4.  **Denormalización en Dimensiones:**
    * **`Dim_Producto`:** Se denormaliza uniendo `product` con `product_category` para incluir el nombre de la categoría y su padre en la misma fila.
    * **`Dim_Geografia`:** Se denormaliza uniendo `address` con `province` para tener la información de provincia directamente en la dimensión geográfica.

5.  **Definición de KPIs (Dominios):**
    * **Ventas ($M):** Se calculan como `SUM(total_amount)` de `Fact_Pedidos` donde el `status` sea 'PAID' o 'FULFILLED'.
    * **Usuarios Activos (nK):** `COUNT(DISTINCT cliente_sk)` de `Fact_Sesiones`. Se excluye al cliente "Desconocido".
    * **Ticket Promedio ($K):** `SUM(total_amount) / COUNT(DISTINCT order_id)` para los pedidos con status 'PAID' o 'FULFILLED'.
    * **NPS (ptos.):** `((Promotores - Detractores) / Total Respuestas) * 100`. (Promotores: 9-10, Detractores: 0-6).

---

### DIMENSIONES (Dims)

Estas tablas describen el contexto ("quién, qué, dónde, cuándo") de los hechos.

#### Dim_Tiempo
* **PK:** `tiempo_id` (INT)
* **Atributos:** `fecha` (DATE), `anio` (SMALLINT), `mes` (TINYINT), `nombre_mes` (VARCHAR), `dia` (TINYINT), `trimestre` (TINYINT), `dia_semana` (TINYINT).

#### Dim_Cliente
* **PK:** `cliente_sk` (BIGINT AUTO_INCREMENT)
* **Atributos:** `customer_id` (INT, Business Key), `email` (VARCHAR), `first_name` (VARCHAR), `last_name` (VARCHAR), `phone` (VARCHAR), `status` (CHAR), `created_at` (TIMESTAMP).

#### Dim_Geografia
* **PK:** `geografia_sk` (BIGINT AUTO_INCREMENT)
* **Atributos:** `address_id` (INT, Business Key), `line1` (VARCHAR), `line2` (VARCHAR), `city` (VARCHAR), `postal_code` (VARCHAR), `country_code` (CHAR), `nombre_provincia` (VARCHAR).

#### Dim_Producto
* **PK:** `producto_sk` (BIGINT AUTO_INCREMENT)
* **Atributos:** `product_id` (INT, Business Key), `sku` (VARCHAR), `nombre_producto` (VARCHAR), `list_price` (DECIMAL), `status_producto` (CHAR), `nombre_categoria` (VARCHAR), `nombre_categoria_padre` (VARCHAR).

#### Dim_Canal
* **PK:** `canal_id` (INT)
* **Atributos:** `code` (VARCHAR), `name` (VARCHAR).

#### Dim_Tienda
* **PK:** `tienda_id` (INT)
* **FK:** `geografia_sk` (ref: `Dim_Geografia.geografia_sk`)
* **Atributos:** `nombre_tienda` (VARCHAR).

---

### HECHOS (Facts)

Estas tablas registran los procesos de negocio y sus métricas. La consigna pide crear todas las tablas de hechos posibles.

#### 1. Fact_Pedidos
Registra las cabeceras de las órdenes de venta. Es la fuente principal para el KPI de Ventas Totales y Ticket Promedio.
* **Grano:** Una fila por cabecera de pedido (`sales_order`).
* **Dimensiones (FKs):**
    * `tiempo_id` (ref: `Dim_Tiempo`, por `order_date`)
    * `cliente_sk` (ref: `Dim_Cliente`)
    * `canal_id` (ref: `Dim_Canal`)
    * `tienda_id` (ref: `Dim_Tienda`, NULO si es online)
    * `geografia_billing_sk` (ref: `Dim_Geografia`, por `billing_address_id`)
    * `geografia_shipping_sk` (ref: `Dim_Geografia`, por `shipping_address_id`)
* **Medidas:** `subtotal`, `tax_amount`, `shipping_fee`, `total_amount`.
* **Atributos Degenerados:** `order_id` (PK), `status`, `currency_code`.

#### 2. Fact_Ventas_Detalle
Registra el detalle de productos en cada orden. Es la fuente para el Ranking de Productos.
* **Grano:** Una fila por ítem de producto dentro de un pedido (`sales_order_item`).
* **Dimensiones (FKs):**
    * `order_id` (ref: `Fact_Pedidos.order_id`)
    * `producto_sk` (ref: `Dim_Producto`)
    * `tiempo_id` (ref: `Dim_Tiempo`, por `order_date` de la cabecera)
* **Medidas:** `quantity`, `unit_price`, `discount_amount`, `line_total`.
* **Atributos Degenerados:** `order_item_id` (PK).

#### 3. Fact_Pagos
Registra las transacciones de pago asociadas a las órdenes.
* **Grano:** Una fila por transacción de pago (`payment`).
* **Dimensiones (FKs):**
    * `order_id` (ref: `Fact_Pedidos.order_id`)
    * `tiempo_id` (ref: `Dim_Tiempo`, por `paid_at`)
* **Medidas:** `amount`.
* **Atributos Degenerados:** `payment_id` (PK), `method`, `status`, `transaction_ref`.

#### 4. Fact_Envios
Registra la información logística de los envíos.
* **Grano:** Una fila por envío (`shipment`).
* **Dimensiones (FKs):**
    * `order_id` (ref: `Fact_Pedidos.order_id`)
    * `tiempo_shipped_id` (ref: `Dim_Tiempo`, por `shipped_at`)
    * `tiempo_delivered_id` (ref: `Dim_Tiempo`, por `delivered_at`)
* **Medidas:** `dias_en_transito` (Calculada en ETL: `delivered_at` - `shipped_at`).
* **Atributos Degenerados:** `shipment_id` (PK), `carrier`, `tracking_number`, `status`.

#### 5. Fact_Sesiones
Registra las sesiones de navegación web. Es la fuente para el KPI de Usuarios Activos.
* **Grano:** Una fila por sesión web (`web_session`).
* **Dimensiones (FKs):**
    * `cliente_sk` (ref: `Dim_Cliente`, puede ser "Desconocido")
    * `tiempo_id` (ref: `Dim_Tiempo`, por `started_at`)
* **Medidas:** `contador_sesion` (Valor: 1), `duracion_sesion_seg` (Calculada en ETL: `ended_at` - `started_at`).
* **Atributos Degenerados:** `session_id` (PK), `source`, `device`.

#### 6. Fact_NPS
Registra las respuestas a las encuestas de Net Promoter Score.
* **Grano:** Una fila por respuesta de encuesta (`nps_response`).
* **Dimensiones (FKs):**
    * `cliente_sk` (ref: `Dim_Cliente`, puede ser "Desconocido")
    * `canal_id` (ref: `Dim_Canal`)
    * `tiempo_id` (ref: `Dim_Tiempo`, por `responded_at`)
* **Medidas:** `score`.
* **Atributos Degenerados:** `nps_id` (PK), `comment` (TEXT).

---

## 3) Estructura del Repositorio

```
.
├── raw/                      # CSVs de origen (proporcionados)
├── DW/                       # Salida del DW (archivos .csv generados por ETL)
├── 01_crear_dim_tiempo.py    # Genera Dim_Tiempo (YYYYMMDD, nombres de mes/día)
├── 02_crear_dimensiones.py   # Genera Dim_Canal, Dim_Cliente, Dim_Geografia, Dim_Producto, Dim_Tienda
├── 03_crear_hechos.py        # Genera Fact_Pedidos, Fact_Ventas_Detalle, Fact_Pagos, Fact_Envios, Fact_Sesiones, Fact_NPS
├── requirements.txt          # Dependencias mínimas para ejecutar los scripts
└── README.md                 # Este documento
```

> **Importante:** asegurate de que todos los CSVs provistos estén bajo `raw/` antes de ejecutar los scripts.

---

## 4) Requisitos e Instalación

**Versión recomendada de Python:** 3.10+  
**SO:** Windows / macOS / Linux

### Entorno virtual (recomendado)
```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS / Linux
source .venv/bin/activate
```

### Dependencias
```text
# requirements.txt
pandas>=2.0.0
python-dateutil>=2.8.2  # (transitiva de pandas, útil por seguridad)
duckdb>=1.0.0           # opcional, para ejecutar consultas SQL directas sobre CSV
```

Instalación:
```bash
pip install -r requirements.txt
```

---

## 5) Pipeline ETL (scripts)

1) **01_crear_dim_tiempo.py**  
Genera la tabla `DW/Dim_Tiempo.csv` con atributos de fecha (id `YYYYMMDD`, año, mes, nombre de mes, día, trimestre, día de semana). Respeta rango `START_DATE`–`END_DATE`.  
Variables clave:
- `START_DATE = "2023-01-01"`  
- `END_DATE   = "2025-12-31"`  
- `OUTPUT_DIR = "DW"`  
- `OUTPUT_FILE = os.path.join(OUTPUT_DIR, "Dim_Tiempo.csv")`

2) **02_crear_dimensiones.py**  
Crea las dimensiones a partir de los CSV de `raw/`:
- **Dim_Canal** (`channel.csv` → `canal_id`, `canal_code`, `canal_nombre`)  
- **Dim_Cliente** (`customer.csv` → genera `cliente_sk` incremental, agrega fila *Cliente Anónimo* con `cliente_sk=-1`)  
- **Dim_Geografia** (`address.csv` + `province.csv` → agrega `nombre_provincia`, genera `geografia_sk`)  
- **Dim_Producto** (`product.csv` + `product_category.csv` + categoría padre → `producto_sk`, `nombre_categoria`, `nombre_categoria_padre`)  
- **Dim_Tienda** (`store.csv` + *lookup* de `Dim_Geografia` para `geografia_sk`)  

3) **03_crear_hechos.py**  
Genera los hechos consumiendo dimensiones y tablas RAW:
- **Fact_Pedidos** (convierte `order_date` a `tiempo_id`, mapea `customer_id` a `cliente_sk`, `billing/shipping` a `geografia_*_sk`).
- **Fact_Ventas_Detalle** (une con `Fact_Pedidos` para traer `tiempo_id` del pedido y mapea `product_id` a `producto_sk`).
- **Fact_Pagos** (convierte `paid_at` a `tiempo_id`).
- **Fact_Envios** (convierte `shipped_at`/`delivered_at` y calcula `dias_en_transito`).
- **Fact_Sesiones** (convierte `started_at` a `tiempo_id`, mapea `customer_id` a `cliente_sk` y usa `-1` para anónimos; calcula `duracion_sesion_seg` y `contador_sesion=1`).
- **Fact_NPS** (convierte `responded_at` a `tiempo_id`, mapea `customer_id` a `cliente_sk` y renombra `channel_id` → `canal_id`).

---

## 6) Cómo ejecutar el proyecto

Con el entorno activado y dependencias instaladas:

```bash
# 1) Asegurá los CSV de RAW en ./raw
# 2) Generá Dim_Tiempo
python ETL/01_crear_dim_tiempo.py

# 3) Generá dimensiones
python ETL/02_crear_dimensiones.py

# 4) Generá hechos
python ETL/03_crear_hechos.py
```

Si todo sale bien, tendrás en `DW/` los CSV finales, listos para ser consumidos por Looker Studio (o por SQL vía DuckDB).

---

## 7) Dashboard en Looker Studio

1. **Preparar fuentes**: subir la carpeta `DW/` a Google Drive (o montar un conector a archivos locales) y crear una **fuente de datos** por cada CSV: `Dim_Tiempo`, `Dim_Canal`, `Dim_Cliente`, `Dim_Geografia`, `Dim_Producto`, `Dim_Tienda`, `Fact_Pedidos`, `Fact_Ventas_Detalle`, `Fact_Pagos`, `Fact_Envios`, `Fact_Sesiones`, `Fact_NPS`.
2. **Campos calculados** (ejemplos):
   - `Ventas`: `CASE WHEN status IN ('PAID','FULFILLED') THEN total_amount ELSE 0 END` (agregación: SUM).
   - `Ticket Promedio`: `SUM(Ventas) / COUNT_DISTINCT(order_id)`.
   - `Usuarios Activos`: usar lógica de la consulta 7.2 (o construir dos vistas separadas).
   - `NPS`: `((% Promotores) - (% Detractores)) * 100` con bins por score.
3. **Filtros / Segmentos**: Fecha (`Dim_Tiempo`), Canal (`Dim_Canal`), Provincia (`Dim_Geografia`), Producto (`Dim_Producto`).
4. **Vistas mínimas**:
   - Serie temporal + tarjeta de **Ventas**.
   - Serie temporal + tarjeta de **Usuarios Activos**.
   - Tarjeta de **Ticket Promedio**.
   - Tarjeta + tendencia de **NPS**.
   - **Ventas por Provincia** (mapa o barras).
   - **Ranking mensual por Producto** (Top N).
5. **Meta del trimestre (ejemplo de negocio)**: crecer 15% en ventas en Córdoba y reducir tiempos de entrega en Mendoza → monitorear **Ventas por Provincia** (filtro Córdoba) y **dias_en_transito** (en `Fact_Envios`).

---

## 8) Buenas prácticas de repositorio

- **Entorno virtual** y `requirements.txt` versionado.
- **Conventional Commits** (ejemplo):
  - `feat(etl): agrega cálculo de dias_en_transito en Fact_Envios`
  - `fix(dim_producto): corrige nulos en nombre_categoria`
  - `docs(readme): agrega instrucciones de Looker Studio`
- **Estructura clara de carpetas** (`raw/`, `DW/`, `scripts/`, `docs/`).
- **Control por consola**: creación de ramas, commits, *tags* de entregas, *merge* sin fast-forward cuando aplique.

---

## 9) Créditos y Licencia

- **Autor/a**: Lautaro Sanfilippo 
- **Materia**: Introducción al Marketing Online y los Negocios Digitales  
- **Licencia**: MIT

---
