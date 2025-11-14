import mysql.connector

CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "rootpass",
    "database": "greenhouse",
    "port": 3306
}

def conectar():
    return mysql.connector.connect(**CONFIG)

def ejecutar_insert(query, valores):
    try:
        cnx = conectar()
        cursor = cnx.cursor()
        cursor.execute(query, valores)
        cnx.commit()
        cursor.close()
        cnx.close()
        print("Inserción realizada correctamente.")
    except mysql.connector.Error as err:
        print("Error al insertar:", err)

# 1. Inserción en clima_data
def insertar_clima(zona, temperatura, humedad, co2, intensidad_luz, presion):
    query = ("INSERT INTO clima_data "
             "(zona, temperatura, humedad, co2, intensidad_luz, presion) "
             "VALUES (%s, %s, %s, %s, %s, %s)")
    valores = (zona, temperatura, humedad, co2, intensidad_luz, presion)
    ejecutar_insert(query, valores)

# 2. Inserción en plantas_data
def insertar_planta(especie, crecimiento, cantidad_frutos, calidad_frutos, nivel_salud):
    query = ("INSERT INTO plantas_data "
             "(especie, crecimiento, cantidad_frutos, calidad_frutos, nivel_salud) "
             "VALUES (%s, %s, %s, %s, %s)")
    valores = (especie, crecimiento, cantidad_frutos, calidad_frutos, nivel_salud)
    ejecutar_insert(query, valores)

# 3. Inserción en riego_data
def insertar_riego(ph, conductividad, flujo, nivel_deposito, caudal_historico):
    query = ("INSERT INTO riego_data "
             "(ph, conductividad, flujo, nivel_deposito, caudal_historico) "
             "VALUES (%s, %s, %s, %s, %s)")
    valores = (ph, conductividad, flujo, nivel_deposito, caudal_historico)
    ejecutar_insert(query, valores)

# 4. Inserción en resultados_funciones
def insertar_resultado_funcion(zona, especie, indice_estres, rendimiento_frutos, eficiencia_luz, necesidad_riego, ajuste_nutricion):
    query = ("INSERT INTO resultados_funciones "
             "(zona, especie, indice_estres, rendimiento_frutos, eficiencia_luz, necesidad_riego, ajuste_nutricion) "
             "VALUES (%s, %s, %s, %s, %s, %s, %s)")
    valores = (zona, especie, indice_estres, rendimiento_frutos, eficiencia_luz, necesidad_riego, ajuste_nutricion)
    ejecutar_insert(query, valores)

# 5. Inserción en alertas_criticas
def insertar_alerta(zona, especie, tipo_alerta):
    query = ("INSERT INTO alertas_criticas "
            "(zona, especie, tipo_alerta) "
            "VALUES (%s, %s, %s)")
    valores = (zona, especie, tipo_alerta)
    ejecutar_insert(query, valores)
