-- Dimensiones para Fact_Ventas_Detalle
CREATE TABLE Dim_Tiempo (
    tiempo_id INT NOT NULL PRIMARY KEY COMMENT 'Formato YYYYMMDD',
    fecha DATE NOT NULL,
    anio SMALLINT NOT NULL,
    mes TINYINT NOT NULL,
    dia TINYINT NOT NULL,
    trimestre TINYINT NOT NULL,
    nombre_mes VARCHAR(20) NOT NULL,
    dia_semana TINYINT NOT NULL
);

CREATE TABLE Dim_Producto (
    producto_sk BIGINT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL COMMENT 'Business Key de RAW.product',
    sku VARCHAR(40),
    nombre_producto VARCHAR(120),
    list_price DECIMAL(12,2),
    status_producto CHAR(1),
    nombre_categoria VARCHAR(80),
    nombre_categoria_padre VARCHAR(80),
    UNIQUE(product_id)
);

-- Tabla de Hechos
CREATE TABLE Fact_Ventas_Detalle (
    order_item_id BIGINT NOT NULL PRIMARY KEY COMMENT 'PK de RAW.sales_order_item',
    order_id BIGINT NOT NULL COMMENT 'FK a Fact_Pedidos',
    producto_sk BIGINT,
    tiempo_id INT COMMENT 'tiempo_id de la orden',
    quantity INT,
    unit_price DECIMAL(12,2),
    discount_amount DECIMAL(12,2),
    line_total DECIMAL(12,2),
    FOREIGN KEY (order_id) REFERENCES Fact_Pedidos(order_id),
    FOREIGN KEY (producto_sk) REFERENCES Dim_Producto(producto_sk),
    FOREIGN KEY (tiempo_id) REFERENCES Dim_Tiempo(tiempo_id)
);