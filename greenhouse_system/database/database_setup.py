import mysql.connector

CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "rootpass",
    "database": "greenhouse",
    "port": 3306
}

TABLES = {}

TABLES['clima_data'] = (
    "CREATE TABLE IF NOT EXISTS clima_data ("
    "  id INT AUTO_INCREMENT PRIMARY KEY,"
    "  zona VARCHAR(32),"
    "  temperatura FLOAT,"
    "  humedad FLOAT,"
    "  co2 FLOAT,"
    "  intensidad_luz FLOAT,"
    "  presion FLOAT,"
    "  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP"
    ") ENGINE=InnoDB"
)

TABLES['plantas_data'] = (
    "CREATE TABLE IF NOT EXISTS plantas_data ("
    "  id INT AUTO_INCREMENT PRIMARY KEY,"
    "  especie VARCHAR(64),"
    "  crecimiento FLOAT,"
    "  cantidad_frutos INT,"
    "  calidad_frutos FLOAT,"
    "  nivel_salud FLOAT,"
    "  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP"
    ") ENGINE=InnoDB"
)

TABLES['riego_data'] = (
    "CREATE TABLE IF NOT EXISTS riego_data ("
    "  id INT AUTO_INCREMENT PRIMARY KEY,"
    "  ph FLOAT,"
    "  conductividad FLOAT,"
    "  flujo FLOAT,"
    "  nivel_deposito FLOAT,"
    "  caudal_historico FLOAT,"
    "  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP"
    ") ENGINE=InnoDB"
)

TABLES['resultados_funciones'] = (
    "CREATE TABLE IF NOT EXISTS resultados_funciones ("
    "  id INT AUTO_INCREMENT PRIMARY KEY,"
    "  zona VARCHAR(32),"
    "  especie VARCHAR(64),"
    "  indice_estres FLOAT,"
    "  rendimiento_frutos FLOAT,"
    "  eficiencia_luz FLOAT,"
    "  necesidad_riego BOOLEAN,"
    "  ajuste_nutricion VARCHAR(32),"
    "  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP"
    ") ENGINE=InnoDB"
)

TABLES['alertas_criticas'] = (
    "CREATE TABLE IF NOT EXISTS alertas_criticas ("
    "  id INT AUTO_INCREMENT PRIMARY KEY,"
    "  zona VARCHAR(32),"
    "  especie VARCHAR(64),"
    "  tipo_alerta VARCHAR(64),"
    "  valor_alerta BOOLEAN,"
    "  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP"
    ") ENGINE=InnoDB"
)


def crear_base_datos():
    try:
        # Crear la BD si no existe
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

        # Crear las tablas
        cnx = mysql.connector.connect(**CONFIG)
        cursor = cnx.cursor()
        for name, ddl in TABLES.items():
            print(f"Creando tabla {name}...")
            cursor.execute(ddl)
        cnx.commit()
        cursor.close()
        cnx.close()
        print("Base de datos y tablas creadas correctamente.")
    except mysql.connector.Error as err:
        print("Error:", err)

if __name__ == "__main__":
    crear_base_datos()
