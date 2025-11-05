-- Dimensiones para Fact_Pedidos
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

CREATE TABLE Dim_Geografia (
    geografia_sk BIGINT AUTO_INCREMENT PRIMARY KEY,
    address_id INT NOT NULL COMMENT 'Business Key de RAW.address',
    line1 VARCHAR(120),
    line2 VARCHAR(120),
    city VARCHAR(80),
    postal_code VARCHAR(20),
    country_code CHAR(2),
    nombre_provincia VARCHAR(50),
    UNIQUE(address_id)
);

CREATE TABLE Dim_Tienda (
    tienda_id INT NOT NULL PRIMARY KEY COMMENT 'PK de RAW.store',
    nombre_tienda VARCHAR(80),
    
    -- Campos de geografía desnormalizados
    line1 VARCHAR(120),
    line2 VARCHAR(120),
    city VARCHAR(80),
    postal_code VARCHAR(20),
    country_code CHAR(2),
    nombre_provincia VARCHAR(50)
    
    -- Se elimina la FK a Dim_Geografia:
    -- FOREIGN KEY (geografia_sk) REFERENCES Dim_Geografia(geografia_sk)
);

CREATE TABLE Dim_Canal (
    canal_id INT NOT NULL PRIMARY KEY COMMENT 'PK de RAW.channel',
    code VARCHAR(20) NOT NULL,
    name VARCHAR(50),
    UNIQUE(code)
);

-- Tabla de Hechos
CREATE TABLE Fact_Pedidos (
    order_id BIGINT NOT NULL PRIMARY KEY COMMENT 'PK de RAW.sales_order',
    tiempo_id INT,
    cliente_sk BIGINT,
    canal_id INT,
    tienda_id INT,
    geografia_billing_sk BIGINT,
    geografia_shipping_sk BIGINT,
    subtotal DECIMAL(12,2),
    tax_amount DECIMAL(12,2),
    shipping_fee DECIMAL(12,2),
    total_amount DECIMAL(12,2),
    status VARCHAR(20),
    currency_code CHAR(3),
    FOREIGN KEY (tiempo_id) REFERENCES Dim_Tiempo(tiempo_id),
    FOREIGN KEY (cliente_sk) REFERENCES Dim_Cliente(cliente_sk),
    FOREIGN KEY (canal_id) REFERENCES Dim_Canal(canal_id),
    FOREIGN KEY (tienda_id) REFERENCES Dim_Tienda(tienda_id),
    FOREIGN KEY (geografia_billing_sk) REFERENCES Dim_Geografia(geografia_sk),
    FOREIGN KEY (geografia_shipping_sk) REFERENCES Dim_Geografia(geografia_sk)
);