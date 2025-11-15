"""Utility helpers to access greenhouse metrics from MySQL."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Optional

import mysql.connector
from mysql.connector import Error

try:  # Prefer shared configuration defined during sprints anteriores
    from database.database_setup import CONFIG as DEFAULT_CONFIG  # type: ignore
except Exception:  # pragma: no cover - fallback only used if import fails
    DEFAULT_CONFIG = {
        "host": "127.0.0.1",
        "user": "root",
        "password": "rootpass",
        "database": "greenhouse",
        "port": 3306,
    }


class DataFetcher:
    """Encapsulates read-only interactions with la base de datos."""

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
        """Return the most recent registros de clima, riego y plantas."""
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
            # Mantener trazas en consola para depuración rápida
            print(f"[DataFetcher] Error reading latest sensor data: {err}")
        return payload

    def get_recent_data(self, table: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Return historical registros ordered from newest to oldest."""
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
            print(f"[DataFetcher] Error reading recent data from {table}: {err}")
        return rows

    def get_processed_data(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Return últimos resultados procesados del middleware."""
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
            print(f"[DataFetcher] Error reading processed data: {err}")
        return rows

    def get_active_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Return alertas no resueltas (o todas si no existe columna resolved)."""
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
            print(f"[DataFetcher] Error reading alerts: {err}")
        return alerts

    def _column_exists(self, cursor, table: str, column: str) -> bool:
        query = (
            "SELECT COUNT(*) as total FROM information_schema.columns "
            "WHERE table_schema = %s AND table_name = %s AND column_name = %s"
        )
        cursor.execute(query, (self._config["database"], table, column))
        result = cursor.fetchone()
        return bool(result and result.get("total"))
