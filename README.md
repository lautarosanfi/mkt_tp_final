# Trabajo Práctico Final — Introducción al Marketing Online y los Negocios Digitales

## 📖 2. Diccionario de Datos y Modelo

A continuación, se detalla el Esquema Estrella (modelo Kimball) diseñado para este proyecto. Se definen los supuestos clave, las dimensiones de conformación y las tablas de hechos que almacenarán las métricas del negocio.

### Supuestos y Decisiones de Modelado

1.  **Claves (Keys):**
    * **Surrogate Keys (SK):** Se generan claves sustitutas (ej: `cliente_sk`, `producto_sk`) para las dimensiones principales (`Dim_Cliente`, `Dim_Producto`, `Dim_Geografia`). Esto permite manejar cambios a lo largo del tiempo (Slowly Changing Dimensions) y desvincular el DW de las claves operacionales de `RAW`.
    * **Business Keys (BK):** Se conservan las claves originales (ej: `customer_id`, `product_id`) como atributos en las dimensiones para trazabilidad y referencia.
    * **Fact Keys:** Las tablas de hechos usan las PK originales del sistema `RAW` (ej: `order_id`, `session_id`) como su propia Primary Key, ya que el grano es el mismo.

2.  **Dimensión de Tiempo (`Dim_Tiempo`):**
    * Esta es una **dimensión de conformación** generada por el script de ETL, ya que no existe en los datos `RAW`.
    * Todas las tablas de hechos se vinculan a esta dimensión a través de sus respectivos campos de fecha (ej: `order_date`, `started_at`, `paid_at`).
    * La PK (`tiempo_id`) es un entero con formato `YYYYMMDD` para facilitar los `JOINs`.

3.  **Manejo de Nulos / Anónimos:**
    * Las tablas `web_session` y `nps_response` permiten un `customer_id` nulo[cite: 164, 173].
    * Para manejar esto, `Dim_Cliente` contendrá un registro especial (ej: `cliente_sk = -1` o `0`) con el valor "Cliente Desconocido / Anónimo". Las FKs en `Fact_Sesiones` y `Fact_NPS` apuntarán a este registro cuando el `customer_id` sea `NULL`.

4.  **Denormalización en Dimensiones:**
    * **`Dim_Producto`:** Se denormaliza uniendo `product` con `product_category` para incluir el nombre de la categoría y su padre en la misma fila.
    * **`Dim_Geografia`:** Se denormaliza uniendo `address` con `province` para tener la información de provincia directamente en la dimensión geográfica.

5.  **Definición de KPIs (Dominios):**
    * **Ventas ($M):** Se calculan como `SUM(total_amount)` de `Fact_Pedidos` donde el `status` sea 'PAID' o 'FULFILLED'[cite: 179].
    * [cite_start]**Usuarios Activos (nK):** `COUNT(DISTINCT cliente_sk)` de `Fact_Sesiones`[cite: 181]. Se excluye al cliente "Desconocido".
    * [cite_start]**Ticket Promedio (\$K):** `SUM(total_amount) / COUNT(DISTINCT order_id)` para los pedidos con status 'PAID' o 'FULFILLED'[cite: 182].
    * **NPS (ptos.):** `((Promotores - Detractores) / Total Respuestas) * 100`[cite: 183]. (Promotores: 9-10, Detractores: 0-6).

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

Estas tablas registran los procesos de negocio y sus métricas. [cite_start]La consigna pide crear todas las tablas de hechos posibles[cite: 23].

#### 1. Fact_Pedidos
Registra las cabeceras de las órdenes de venta. Es la fuente principal para el KPI de Ventas Totales y Ticket Promedio.
![Esquema Pedidos](star_schema/Fact_Pedidos.png)
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
![Esquema Ventas Detalle](star_schema/Fact_Ventas_Detalle.png)
* **Grano:** Una fila por ítem de producto dentro de un pedido (`sales_order_item`).
* **Dimensiones (FKs):**
    * `order_id` (ref: `Fact_Pedidos.order_id`)
    * `producto_sk` (ref: `Dim_Producto`)
    * `tiempo_id` (ref: `Dim_Tiempo`, por `order_date` de la cabecera)
* **Medidas:** `quantity`, `unit_price`, `discount_amount`, `line_total`.
* **Atributos Degenerados:** `order_item_id` (PK).

#### 3. Fact_Pagos
Registra las transacciones de pago asociadas a las órdenes.
![Esquema Pagos](star_schema/Fact_Pagos.png)
* **Grano:** Una fila por transacción de pago (`payment`).
* **Dimensiones (FKs):**
    * `order_id` (ref: `Fact_Pedidos.order_id`)
    * `tiempo_id` (ref: `Dim_Tiempo`, por `paid_at`)
* **Medidas:** `amount`.
* **Atributos Degenerados:** `payment_id` (PK), `method`, `status`, `transaction_ref`.

#### 4. Fact_Envios
Registra la información logística de los envíos.
![Esquema Envios](star_schema/Fact_Envios.png)
* **Grano:** Una fila por envío (`shipment`).
* **Dimensiones (FKs):**
    * `order_id` (ref: `Fact_Pedidos.order_id`)
    * `tiempo_shipped_id` (ref: `Dim_Tiempo`, por `shipped_at`)
    * `tiempo_delivered_id` (ref: `Dim_Tiempo`, por `delivered_at`)
* **Medidas:** `dias_en_transito` (Calculada en ETL: `delivered_at` - `shipped_at`).
* **Atributos Degenerados:** `shipment_id` (PK), `carrier`, `tracking_number`, `status`.

#### 5. Fact_Sesiones
Registra las sesiones de navegación web. Es la fuente para el KPI de Usuarios Activos.
![Esquema Sesiones](star_schema/Fact_Sesiones.png)
* **Grano:** Una fila por sesión web (`web_session`).
* **Dimensiones (FKs):**
    * `cliente_sk` (ref: `Dim_Cliente`, puede ser "Desconocido")
    * `tiempo_id` (ref: `Dim_Tiempo`, por `started_at`)
* **Medidas:** `contador_sesion` (Valor: 1), `duracion_sesion_seg` (Calculada en ETL: `ended_at` - `started_at`).
* **Atributos Degenerados:** `session_id` (PK), `source`, `device`.

#### 6. Fact_NPS
Registra las respuestas a las encuestas de Net Promoter Score.
![Esquema NPS](star_schema/Fact_NPS.png)
* **Grano:** Una fila por respuesta de encuesta (`nps_response`).
* **Dimensiones (FKs):**
    * `cliente_sk` (ref: `Dim_Cliente`, puede ser "Desconocido")
    * `canal_id` (ref: `Dim_Canal`)
    * `tiempo_id` (ref: `Dim_Tiempo`, por `responded_at`)
* **Medidas:** `score`.
* **Atributos Degenerados:** `nps_id` (PK), `comment` (TEXT).