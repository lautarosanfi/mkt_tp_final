-- Dimensiones para Fact_NPS
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

CREATE TABLE Dim_Canal (
    canal_id INT NOT NULL PRIMARY KEY COMMENT 'PK de RAW.channel',
    code VARCHAR(20) NOT NULL,
    name VARCHAR(50),
    UNIQUE(code)
);

-- Tabla de Hechos
CREATE TABLE Fact_NPS (
    nps_id BIGINT NOT NULL PRIMARY KEY COMMENT 'PK de RAW.nps_response',
    cliente_sk BIGINT,
    canal_id INT,
    tiempo_id INT COMMENT 'tiempo_id de responded_at',
    score SMALLINT,
    comment TEXT,
    FOREIGN KEY (cliente_sk) REFERENCES Dim_Cliente(cliente_sk),
    FOREIGN KEY (canal_id) REFERENCES Dim_Canal(canal_id),
    FOREIGN KEY (tiempo_id) REFERENCES Dim_Tiempo(tiempo_id)
);