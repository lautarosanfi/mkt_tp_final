-- Dimensiones para Fact_Envios
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

-- Tabla de Hechos
CREATE TABLE Fact_Envios (
    shipment_id BIGINT NOT NULL PRIMARY KEY COMMENT 'PK de RAW.shipment',
    order_id BIGINT NOT NULL COMMENT 'FK a Fact_Pedidos',
    tiempo_shipped_id INT,
    tiempo_delivered_id INT,
    dias_en_transito SMALLINT,
    carrier VARCHAR(40),
    tracking_number VARCHAR(60),
    status VARCHAR(20),
    FOREIGN KEY (order_id) REFERENCES Fact_Pedidos(order_id),
    FOREIGN KEY (tiempo_shipped_id) REFERENCES Dim_Tiempo(tiempo_id),
    FOREIGN KEY (tiempo_delivered_id) REFERENCES Dim_Tiempo(tiempo_id)
);