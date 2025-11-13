import mysql.connector

CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "rootpass",
    "database": "greenhouse",
    "port": 3306
}

TABLES = {}

# Tabla para Clima
TABLES['clima_data'] = (
    "CREATE TABLE IF NOT EXISTS clima_data ("
    "  id INT AUTO_INCREMENT PRIMARY KEY,"
    "  temperatura FLOAT,"
    "  humedad FLOAT,"
    "  co2 FLOAT,"
    "  intensidad_luz FLOAT,"
    "  zona VARCHAR(32),"
    "  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP"
    ") ENGINE=InnoDB"
)

# Tabla para Plantas
TABLES['plant_data'] = (
    "CREATE TABLE IF NOT EXISTS plant_data ("
    "  id INT AUTO_INCREMENT PRIMARY KEY,"
    "  especie VARCHAR(64),"
    "  crecimiento FLOAT,"
    "  cantidad_frutos INT,"
    "  calidad_frutos FLOAT,"
    "  humedad_objetivo FLOAT,"
    "  ph_objetivo FLOAT,"
    "  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP"
    ") ENGINE=InnoDB"
)

# Tabla para Riego
TABLES['riego_data'] = (
    "CREATE TABLE IF NOT EXISTS riego_data ("
    "  id INT AUTO_INCREMENT PRIMARY KEY,"
    "  ph FLOAT,"
    "  conductividad FLOAT,"
    "  flujo FLOAT,"
    "  nivel_deposito FLOAT,"
    "  tipo_nutriente VARCHAR(64),"
    "  estado_sistema VARCHAR(32),"
    "  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP"
    ") ENGINE=InnoDB"
)

def crear_base_datos():
    try:
        # Conectar al servidor sin base de datos
        cnx = mysql.connector.connect(
            host=CONFIG["host"],
            user=CONFIG["user"],
            password=CONFIG["password"],
            port=CONFIG["port"]
        )
        cursor = cnx.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {CONFIG['database']} DEFAULT CHARACTER SET 'utf8mb4'")
        cursor.close()
        cnx.close()

        # Conectar ya a la base de datos creada
        cnx = mysql.connector.connect(**CONFIG)
        cursor = cnx.cursor()
        for name, ddl in TABLES.items():
            cursor.execute(ddl)
        cnx.commit()
        cursor.close()
        cnx.close()
        print("Base de datos y tablas creadas correctamente.")
    except mysql.connector.Error as err:
        print("Error:", err)

if __name__ == "__main__":
    crear_base_datos()
