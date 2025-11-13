import mysql.connector
from datetime import datetime

CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "rootpass",
    "database": "greenhouse",
    "port": 3306
}

class DatabaseManager:
    def __init__(self):
        self.cnx = mysql.connector.connect(**CONFIG)
        self.cursor = self.cnx.cursor(dictionary=True)

    def insertar_datos_sensores(self, origen, datos):
        for nombre, valor in datos.items():
            # Convertir cualquier tipo complejo a string
            if not isinstance(valor, str):
                valor = str(valor)
            sql = ("INSERT INTO sensor_data (origen, nombre_variable, valor, unidad) "
                "VALUES (%s, %s, %s, %s)")
            unidad = "N/A"
            self.cursor.execute(sql, (origen, nombre, valor, unidad))
        self.cnx.commit()

    def obtener_historico(self, horas=24):
        sql = "SELECT * FROM sensor_data WHERE timestamp >= NOW() - INTERVAL %s HOUR"
        self.cursor.execute(sql, (horas,))
        return self.cursor.fetchall()

    def registrar_alerta(self, tipo, severidad, mensaje):
        sql = "INSERT INTO system_alerts (tipo, severidad, mensaje) VALUES (%s, %s, %s)"
        self.cursor.execute(sql, (tipo, severidad, mensaje))
        self.cnx.commit()

    def cerrar(self):
        self.cursor.close()
        self.cnx.close()

# Comprobación rápida
if __name__ == "__main__":
    db = DatabaseManager()
    db.insertar_datos_sensores("clima", {"Temperatura": 23, "Humedad": 65})
    print(db.obtener_historico(1))
    db.registrar_alerta("CLIMA", "ADVERTENCIA", "Temperatura alta")
    db.cerrar()