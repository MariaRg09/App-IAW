CREATE TABLE usuarios (
id INT AUTO_INCREMENT PRIMARY KEY,
nombre VARCHAR(100) NOT NULL,
contraseña VARCHAR(255) NOT NULL
);

CREATE TABLE taquillas (
id INT AUTO_INCREMENT PRIMARY KEY,
numero INT UNIQUE NOT NULL,
estado ENUM('libre', 'ocupada') DEFAULT 'libre'
);

CREATE TABLE prestamos (
id INT AUTO_INCREMENT PRIMARY KEY,
usuario_id INT,
taquilla_id INT,
fecha_prestamo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
fecha_devolucion TIMESTAMP NULL,
FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
FOREIGN KEY (taquilla_id) REFERENCES taquillas(id)
);
