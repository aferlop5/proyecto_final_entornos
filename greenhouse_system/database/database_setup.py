from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Optional

import mysql.connector
from mysql.connector import Error

CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "rootpass",
    "database": "greenhouse",
    "port": 3306
}

DEFAULT_CONFIG: Dict[str, Any] = CONFIG.copy()

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


class DataFetcher:
    """Encapsula operaciones de lectura contra la base de datos del invernadero."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self._config = config or DEFAULT_CONFIG

    @contextmanager
    def _connection(self):
        cnx = mysql.connector.connect(**self._config)
        try:
            yield cnx
        finally:
            cnx.close()

    def _fetchone(self, cursor, query: str, params: Optional[Iterable[Any]] = None) -> Optional[Dict[str, Any]]:
        cursor.execute(query, params or ())
        row = cursor.fetchone()
        return self._normalise_row(row) if row else None

    def _fetchall(self, cursor, query: str, params: Optional[Iterable[Any]] = None) -> List[Dict[str, Any]]:
        cursor.execute(query, params or ())
        rows = cursor.fetchall() or []
        return [self._normalise_row(row) for row in rows if row]

    def _normalise_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        normalised: Dict[str, Any] = {}
        for key, value in row.items():
            if isinstance(value, datetime):
                normalised[key] = value.isoformat()
            elif isinstance(value, Decimal):
                normalised[key] = float(value)
            else:
                normalised[key] = value
        return normalised

    def get_latest_sensor_data(self) -> Dict[str, Optional[Dict[str, Any]]]:
        """Devuelve los registros más recientes de clima, riego y plantas."""
        latest_queries = {
            "clima": "SELECT * FROM clima_data ORDER BY timestamp DESC LIMIT 1",
            "riego": "SELECT * FROM riego_data ORDER BY timestamp DESC LIMIT 1",
            "plantas": "SELECT * FROM plantas_data ORDER BY timestamp DESC LIMIT 1",
        }
        payload: Dict[str, Optional[Dict[str, Any]]] = {key: None for key in latest_queries}
        try:
            with self._connection() as cnx:
                cursor = cnx.cursor(dictionary=True)
                for key, query in latest_queries.items():
                    payload[key] = self._fetchone(cursor, query)
                cursor.close()
        except Error as err:
            # Mantener trazas simples para depuración de despliegues.
            print(f"[DataFetcher] Error leyendo los datos más recientes: {err}")
        return payload

    def get_recent_data(self, table: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Devuelve registros históricos ordenados de más nuevo a más antiguo."""
        allowed_tables = {"clima_data", "riego_data", "plantas_data"}
        if table not in allowed_tables:
            raise ValueError(f"Tabla no permitida: {table}")

        query = f"SELECT * FROM {table} ORDER BY timestamp DESC LIMIT %s"
        rows: List[Dict[str, Any]] = []
        try:
            with self._connection() as cnx:
                cursor = cnx.cursor(dictionary=True)
                rows = self._fetchall(cursor, query, (limit,))
                cursor.close()
        except Error as err:
            print(f"[DataFetcher] Error leyendo datos recientes de {table}: {err}")
        return rows

    def get_processed_data(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Devuelve resultados procesados por el middleware."""
        query = (
            "SELECT zona, especie, indice_estres, rendimiento_frutos, eficiencia_luz, "
            "necesidad_riego, ajuste_nutricion, timestamp "
            "FROM resultados_funciones ORDER BY timestamp DESC LIMIT %s"
        )
        rows: List[Dict[str, Any]] = []
        try:
            with self._connection() as cnx:
                cursor = cnx.cursor(dictionary=True)
                rows = self._fetchall(cursor, query, (limit,))
                cursor.close()
        except Error as err:
            print(f"[DataFetcher] Error leyendo datos procesados: {err}")
        return rows

    def get_active_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Devuelve alertas no resueltas, si la columna existe."""
        alerts: List[Dict[str, Any]] = []
        try:
            with self._connection() as cnx:
                cursor = cnx.cursor(dictionary=True)
                resolved_exists = self._column_exists(cursor, "alertas_criticas", "resolved")
                if resolved_exists:
                    query = (
                        "SELECT zona, especie, tipo_alerta, timestamp FROM alertas_criticas "
                        "WHERE resolved = FALSE ORDER BY timestamp DESC LIMIT %s"
                    )
                    alerts = self._fetchall(cursor, query, (limit,))
                else:
                    query = (
                        "SELECT zona, especie, tipo_alerta, timestamp FROM alertas_criticas "
                        "ORDER BY timestamp DESC LIMIT %s"
                    )
                    alerts = self._fetchall(cursor, query, (limit,))
                cursor.close()
        except Error as err:
            print(f"[DataFetcher] Error leyendo alertas: {err}")
        return alerts

    def _column_exists(self, cursor, table: str, column: str) -> bool:
        query = (
            "SELECT COUNT(*) as total FROM information_schema.columns "
            "WHERE table_schema = %s AND table_name = %s AND column_name = %s"
        )
        cursor.execute(query, (self._config["database"], table, column))
        result = cursor.fetchone()
        return bool(result and result.get("total"))

if __name__ == "__main__":
    crear_base_datos()
