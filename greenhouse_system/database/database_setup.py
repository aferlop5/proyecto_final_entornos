# database/database_setup.py
import mysql.connector
from mysql.connector import errorcode

CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "rootpass",
    "database": "greenhouse",
    "port": 3306
}

TABLES = {}

TABLES['sensor_data'] = (
    "CREATE TABLE IF NOT EXISTS sensor_data ("
    "  id INT AUTO_INCREMENT PRIMARY KEY,"
    "  origen VARCHAR(64),"
    "  nombre_variable VARCHAR(64),"
    "  valor FLOAT,"
    "  unidad VARCHAR(32),"
    "  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP"
    ") ENGINE=InnoDB"
)

TABLES['plant_states'] = (
    "CREATE TABLE IF NOT EXISTS plant_states ("
    "  id INT AUTO_INCREMENT PRIMARY KEY,"
    "  especie VARCHAR(64),"
    "  dias_desde_siembra INT,"
    "  crecimiento FLOAT,"
    "  salud FLOAT,"
    "  etapa VARCHAR(32),"
    "  parametros_optimos JSON,"
    "  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP"
    ") ENGINE=InnoDB"
)

TABLES['optimizations'] = (
    "CREATE TABLE IF NOT EXISTS optimizations ("
    "  id INT AUTO_INCREMENT PRIMARY KEY,"
    "  algoritmo VARCHAR(64),"
    "  parametros TEXT,"
    "  fitness FLOAT,"
    "  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP"
    ") ENGINE=InnoDB"
)

TABLES['system_alerts'] = (
    "CREATE TABLE IF NOT EXISTS system_alerts ("
    "  id INT AUTO_INCREMENT PRIMARY KEY,"
    "  tipo VARCHAR(32),"
    "  severidad VARCHAR(16),"
    "  mensaje TEXT,"
    "  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP"
    ") ENGINE=InnoDB"
)

def crear_base_datos():
    try:
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
