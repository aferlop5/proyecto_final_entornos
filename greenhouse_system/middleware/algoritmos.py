# 1. Función para calcular un índice de estrés de la planta
def indice_estres(temperatura, humedad, co2, nivel_salud):
    """
    Combina temperatura, humedad, CO2 y nivel de salud para dar un índice de estrés.
    Devuelve un float entre 0 (sin estrés) y 1 (estrés máximo)
    """
    temp_factor = max(0, min((temperatura - 20) / 4, 1))
    hum_factor = max(0, min(abs(humedad - 65) / 20, 1))
    co2_factor = max(0, min(abs(co2 - 450) / 200, 1))
    salud_factor = max(0, 1 - nivel_salud/100)
    
    estres = (temp_factor + hum_factor + co2_factor + salud_factor) / 4
    return round(estres, 2)


# 2. Función para estimar el rendimiento de frutos
def rendimiento_frutos(cantidad_frutos, calidad_frutos, crecimiento):
    """
    Combina cantidad de frutos, calidad y crecimiento para dar una estimación de rendimiento.
    Devuelve float representando "frutos efectivos"
    """
    return round(cantidad_frutos * (calidad_frutos / 100) * (crecimiento / 15), 2)


# 3. Función para calcular eficiencia de luz según hora
def eficiencia_luz(intensidad_luz, hora, crecimiento):
    """
    Combina intensidad de luz, hora y crecimiento para dar eficiencia fotosintética
    Devuelve float 0-1
    """
    if 8 <= hora <= 18:
        eficiencia = min(1, intensidad_luz / 1000 * (crecimiento / 15))
    else:
        eficiencia = min(0.2, intensidad_luz / 200 * (crecimiento / 15))
    return round(eficiencia, 2)


# 4. Función para evaluar necesidades de riego
def necesidad_riego(nivel_deposito, flujo, temperatura, humedad):
    """
    Combina nivel del depósito, flujo de riego, temperatura y humedad.
    Devuelve boolean: True si es necesario aumentar riego, False si está OK
    """
    riesgo_sequedad = (30 - nivel_deposito)/30 + max(0, (25 - humedad)/25) + max(0, (temperatura - 22)/5)
    return riesgo_sequedad > 1


# 5. Función que combina salud, pH y conductividad para dar una recomendación
def ajuste_nutricion(nivel_salud, ph, conductividad):
    """
    Combina salud de la planta, pH del agua y conductividad.
    Devuelve un string corto con recomendación: 'OK', 'Ajustar pH', 'Ajustar Nutrientes'
    """
    if ph < 5.8 or ph > 6.2:
        return "Ajustar pH"
    elif conductividad < 1.2 or conductividad > 1.8:
        return "Ajustar Nutrientes"
    elif nivel_salud < 75:
        return "Revisar salud"
    else:
        return "OK"


# 6. Sistema de alerta de condiciones críticas
import random

def alerta_critica(temperatura, co2, nivel_salud, luz):
    """
    Devuelve True si se detecta una situación de riesgo para el cultivo.
    Se combina el valor de los sensores con una pequeña probabilidad para situaciones inesperadas.
    """
    # Temperatura ligeramente fuera de rango óptimo
    if temperatura < 20 or temperatura > 24:
        return True

    # CO2 fuera de rango medio
    if co2 < 400 or co2 > 500:
        return True

    # Nivel de salud bajo
    if nivel_salud < 75:
        return True

    # Luz baja (solo de noche o situaciones anómalas)
    if luz < 50:
        return True

    # Pequeña probabilidad de alerta inesperada (5%)
    if random.random() < 0.05:
        return True

    return False


