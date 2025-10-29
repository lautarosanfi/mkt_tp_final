-- Dimensiones para Fact_Sesiones
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

CREATE TABLE Dim_Cliente (
    cliente_sk BIGINT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL COMMENT 'Business Key de RAW.customer',
    email VARCHAR(120) NOT NULL,
    first_name VARCHAR(80),
    last_name VARCHAR(80),
    phone VARCHAR(30),
    status CHAR(1),
    created_at TIMESTAMP,
    UNIQUE(customer_id)
);

-- Tabla de Hechos
CREATE TABLE Fact_Sesiones (
    session_id BIGINT NOT NULL PRIMARY KEY COMMENT 'PK de RAW.web_session',
    cliente_sk BIGINT,
    tiempo_id INT COMMENT 'tiempo_id de started_at',
    contador_sesion TINYINT DEFAULT 1,
    duracion_sesion_seg INT,
    source VARCHAR(50),
    device VARCHAR(30),
    FOREIGN KEY (cliente_sk) REFERENCES Dim_Cliente(cliente_sk),
    FOREIGN KEY (tiempo_id) REFERENCES Dim_Tiempo(tiempo_id)
);