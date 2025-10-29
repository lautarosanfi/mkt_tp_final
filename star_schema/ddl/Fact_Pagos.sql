-- Dimensiones para Fact_Pagos
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
CREATE TABLE Fact_Pagos (
    payment_id BIGINT NOT NULL PRIMARY KEY COMMENT 'PK de RAW.payment',
    order_id BIGINT NOT NULL COMMENT 'FK a Fact_Pedidos',
    tiempo_id INT COMMENT 'tiempo_id de paid_at',
    amount DECIMAL(12,2),
    method VARCHAR(20),
    status VARCHAR(20),
    transaction_ref VARCHAR(80),
    FOREIGN KEY (order_id) REFERENCES Fact_Pedidos(order_id),
    FOREIGN KEY (tiempo_id) REFERENCES Dim_Tiempo(tiempo_id)
);