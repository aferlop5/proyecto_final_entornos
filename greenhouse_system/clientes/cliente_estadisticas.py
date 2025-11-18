"""Cliente interactivo para análisis estadístico del sistema de invernadero.

Ejecutar desde la terminal:
    python cliente_estadisticas.py
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional

import matplotlib.pyplot as plt
import mysql.connector
import pandas as pd
import seaborn as sns

from greenhouse_system.middleware import database_handler

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "resultados_cliente_estadisticas"
MAX_DIAS = 365

COLORES: Dict[str, str] = {
    "temperatura": "#FF6B6B",
    "humedad": "#4ECDC4",
    "crecimiento": "#45B7D1",
    "ph": "#96CEB4",
    "alerta_critica": "#FF5252",
    "alerta_advertencia": "#FFB142",
    "co2": "#FFA07A",
    "intensidad_luz": "#FFD93D",
    "presion": "#6C5B7B",
    "conductividad": "#1A535C",
    "flujo": "#FF9F1C",
    "nivel_deposito": "#2EC4B6",
    "caudal_historico": "#5C6BC0",
    "cantidad_frutos": "#F28482",
    "calidad_frutos": "#9B5DE5",
    "nivel_salud": "#00BBF9",
    "indice_estres": "#FF0054",
    "rendimiento_frutos": "#7209B7",
    "eficiencia_luz": "#3A0CA3",
}

VARIABLES_DISPONIBLES: Dict[str, str] = {
    "temperatura": "clima_data",
    "humedad": "clima_data",
    "co2": "clima_data",
    "intensidad_luz": "clima_data",
    "presion": "clima_data",
    "ph": "riego_data",
    "conductividad": "riego_data",
    "flujo": "riego_data",
    "nivel_deposito": "riego_data",
    "caudal_historico": "riego_data",
    "crecimiento": "plantas_data",
    "cantidad_frutos": "plantas_data",
    "calidad_frutos": "plantas_data",
    "nivel_salud": "plantas_data",
}


class UserCancelled(Exception):
    """Señala que el usuario solicitó cancelar la operación."""
    pass


def configurar_entorno() -> None:
    """Configura estilos globales para gráficos y crea carpetas necesarias."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({
        "figure.dpi": 120,
        "savefig.dpi": 300,
        "axes.titlesize": 14,
        "axes.labelsize": 12,
    })


def mostrar_progreso(etapa: str) -> None:
    """Imprime un mensaje de progreso."""
    print(f"\n🔄 {etapa}...")


def conectar_bd():
    """Obtiene una conexión a la base de datos gestionando errores."""
    try:
        return database_handler.conectar()
    except mysql.connector.Error as error:
        print(f"❌ Error de conexión: {error}")
        return None


def consultar_dataframe(query: str, params: Optional[tuple] = None) -> pd.DataFrame:
    """Ejecuta una consulta SQL y devuelve un DataFrame."""
    conexion = conectar_bd()
    if conexion is None:
        raise RuntimeError("No se pudo establecer la conexión con la base de datos.")

    try:
        df = pd.read_sql(query, conexion, params=params)
    finally:
        conexion.close()

    for columna in df.columns:
        if "timestamp" in columna:
            df[columna] = pd.to_datetime(df[columna])
    return df


def sanitizar(fragmento: str) -> str:
    """Limpia un fragmento para uso en nombres de archivo."""
    limpio = "".join(ch if ch.isalnum() or ch in ("-", "_") else "" for ch in fragmento.lower())
    return limpio or "valor"


def construir_nombre_archivo(tipo: str, parametros: Iterable[str], extension: str) -> str:
    """Construye un nombre de archivo con timestamp y metadatos."""
    partes = [sanitizar(tipo)]
    partes.extend(sanitizar(str(par)) for par in parametros if par)
    partes.append(datetime.now().strftime("%Y%m%d_%H%M%S"))
    return "_".join(partes) + f".{extension}"


def decorar_figura(fig: plt.Figure, titulo: str) -> None:
    """Añade título, pie y logotipo textual a la figura."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    fig.suptitle(titulo, fontsize=16, fontweight="bold")
    fig.text(0.98, 0.02, "Greenhouse System", ha="right", va="bottom", fontsize=9, color="#2C3E50")
    fig.text(0.02, 0.02, f"Generado {timestamp}", ha="left", va="bottom", fontsize=9, color="#555555")


def guardar_figura(fig: plt.Figure, tipo: str, parametros: Iterable[str]) -> Path:
    """Guarda una figura en el directorio de resultados."""
    nombre = construir_nombre_archivo(tipo, parametros, "png")
    ruta = RESULTS_DIR / nombre
    fig.savefig(ruta, bbox_inches="tight")
    plt.close(fig)
    print(f"✅ Gráfico generado: {ruta.relative_to(BASE_DIR)}")
    return ruta


def guardar_dataframe(df: pd.DataFrame, tipo: str, parametros: Iterable[str]) -> Path:
    """Persistente un DataFrame en CSV dentro del directorio de resultados."""
    nombre = construir_nombre_archivo(tipo, parametros, "csv")
    ruta = RESULTS_DIR / nombre
    df.to_csv(ruta, index=False)
    print(f"✅ CSV generado: {ruta.relative_to(BASE_DIR)}")
    return ruta


def imprimir_tabla(df: pd.DataFrame) -> None:
    """Muestra un DataFrame de forma legible en consola."""
    if df.empty:
        print("⚠️ No hay datos para mostrar.")
        return
    with pd.option_context("display.max_rows", None, "display.max_columns", None):
        print(df.to_string(index=False, float_format=lambda x: f"{x:0.2f}"))


def leer_opcion_usuario(mensaje: str, default: Optional[str] = None) -> str:
    """Lee un valor de entrada permitiendo cancelar con 'q'."""
    prompt = mensaje
    if default is not None:
        prompt += f" ({default})"
    prompt += ": "

    while True:
        valor = input(prompt).strip()
        if valor.lower() == "q":
            raise UserCancelled
        if not valor and default is not None:
            return default
        if valor:
            return valor
        print("⚠️ Debe introducir un valor o 'q' para cancelar.")


def obtener_entero(mensaje: str, default: int, minimo: int = 1, maximo: int = MAX_DIAS) -> int:
    """Solicita un entero validando rangos y permitiendo valores por defecto."""
    while True:
        bruto = leer_opcion_usuario(mensaje, str(default))
        try:
            valor = int(bruto)
        except ValueError:
            print("⚠️ Introduzca un número válido.")
            continue
        if not (minimo <= valor <= maximo):
            print(f"⚠️ El número debe estar entre {minimo} y {maximo}.")
            continue
        return valor


def obtener_variable(mensaje: str = "¿Qué variable desea analizar?", *, multiple: bool = False) -> List[str] | str:
    """Solicita variables existentes en la base de datos."""
    disponibles = sorted(VARIABLES_DISPONIBLES.keys())
    print("\nVariables disponibles:")
    print(", ".join(disponibles))

    if multiple:
        while True:
            bruto = leer_opcion_usuario(mensaje)
            variables = [var.strip().lower() for var in bruto.split(",") if var.strip()]
            desconocidos = [var for var in variables if var not in disponibles]
            if desconocidos:
                print(f"⚠️ Variables no reconocidas: {', '.join(desconocidos)}")
                continue
            if len(variables) < 2:
                print("⚠️ Introduzca al menos dos variables para comparar.")
                continue
            return variables
    else:
        while True:
            variable = leer_opcion_usuario(mensaje).lower()
            if variable in disponibles:
                return variable
            print("⚠️ Variable no reconocida. Intente nuevamente.")


def obtener_tipo_grafico() -> str:
    """Solicita un tipo de gráfico válido."""
    tipos = {"linea", "area", "puntos"}
    while True:
        tipo = leer_opcion_usuario("¿Tipo de gráfico? (linea/area/puntos)", "linea").lower()
        if tipo in tipos:
            return tipo
        print("⚠️ Tipo de gráfico no válido.")


def obtener_datos_tabla(tabla: str, dias: int) -> pd.DataFrame:
    """Obtiene los registros de una tabla en el rango de días solicitado."""
    query = (
        f"SELECT * FROM {tabla} "
        "WHERE timestamp >= NOW() - INTERVAL %s DAY "
        "ORDER BY timestamp ASC"
    )
    df = consultar_dataframe(query, (dias,))
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def obtener_series_variable(variable: str, dias: int) -> pd.DataFrame:
    """Recupera una serie temporal para una variable concreta."""
    tabla = VARIABLES_DISPONIBLES[variable]
    df = obtener_datos_tabla(tabla, dias)
    if df.empty or variable not in df.columns:
        return pd.DataFrame(columns=["timestamp", variable])
    serie = df[["timestamp", variable]].dropna()
    serie = serie.sort_values("timestamp")
    return serie


def estadisticas_basicas() -> None:
    dias = obtener_entero("¿Número de días para analizar?", default=7)
    mostrar_progreso("Consultando datos para estadísticas básicas")

    tablas = ["clima_data", "riego_data", "plantas_data"]
    registros: List[pd.DataFrame] = []
    for tabla in tablas:
        df = obtener_datos_tabla(tabla, dias)
        if not df.empty:
            df["tabla"] = tabla
            registros.append(df)

    if not registros:
        print("⚠️ No se encontraron datos en el período solicitado.")
        return

    filas = []
    for df in registros:
        tabla = df["tabla"].iloc[0]
        numeric = df.select_dtypes(include="number").drop(columns=["id"], errors="ignore")
        for columna in numeric.columns:
            serie = numeric[columna].dropna()
            if serie.empty:
                continue
            filas.append({
                "tabla": tabla,
                "variable": columna,
                "media": serie.mean(),
                "maximo": serie.max(),
                "minimo": serie.min(),
                "desviacion": serie.std(ddof=0) if len(serie) > 1 else 0.0,
            })

    if not filas:
        print("⚠️ No se encontraron columnas numéricas para calcular estadísticas.")
        return

    estadisticas = pd.DataFrame(filas).sort_values(["tabla", "variable"]).reset_index(drop=True)
    imprimir_tabla(estadisticas)

    medias = estadisticas.sort_values("media", ascending=False)
    fig, ax = plt.subplots(figsize=(11, 6))
    colores = [COLORES.get(var, "#4E79A7") for var in medias["variable"]]
    ax.barh(medias["variable"], medias["media"], color=colores)
    ax.set_xlabel("Media")
    ax.set_ylabel("Variable")
    ax.grid(alpha=0.2)
    for idx, valor in enumerate(medias["media"]):
        ax.text(valor, idx, f" {valor:0.2f}", va="center")
    decorar_figura(fig, f"Estadísticas básicas últimos {dias} días")
    guardar_figura(fig, "estadisticas_basicas", [f"{dias}dias"])
    guardar_dataframe(estadisticas, "estadisticas_basicas", [f"{dias}dias"])


def tendencias_temporales() -> None:
    variable = obtener_variable()
    dias = obtener_entero("¿Número de días?", default=30)
    tipo = obtener_tipo_grafico()

    mostrar_progreso(f"Generando tendencia para {variable}")
    serie = obtener_series_variable(variable, dias)
    if serie.empty:
        print("⚠️ No hay datos disponibles para la variable en el período seleccionado.")
        return

    serie.set_index("timestamp", inplace=True)
    diaria = serie.resample("D").mean().dropna()
    if diaria.empty:
        print("⚠️ Los datos disponibles no permiten generar la tendencia solicitada.")
        return

    fig, ax = plt.subplots(figsize=(11, 6))
    color = COLORES.get(variable, "#1F77B4")
    fechas = diaria.index
    valores = diaria[variable]

    if tipo == "linea":
        ax.plot(fechas, valores, color=color, marker="o", label=variable.title())
    elif tipo == "area":
        ax.fill_between(fechas, valores, color=color, alpha=0.35)
        ax.plot(fechas, valores, color=color, label=variable.title())
    else:
        ax.scatter(fechas, valores, color=color, label=variable.title())

    ax.set_xlabel("Fecha")
    ax.set_ylabel(variable.replace("_", " ").title())
    ax.legend()
    ax.grid(alpha=0.2)
    decorar_figura(fig, f"Tendencia de {variable.replace('_', ' ')}")
    guardar_figura(fig, "tendencia", [variable, f"{dias}dias", tipo])


def heatmap_correlaciones() -> None:
    dias = obtener_entero("¿Número de días para el análisis de correlaciones?", default=30)
    mostrar_progreso("Calculando correlaciones entre variables")

    tablas = {
        "clima_data": ["temperatura", "humedad", "co2", "intensidad_luz", "presion"],
        "riego_data": ["ph", "conductividad", "flujo", "nivel_deposito", "caudal_historico"],
        "plantas_data": ["crecimiento", "cantidad_frutos", "calidad_frutos", "nivel_salud"],
    }

    combinado: Optional[pd.DataFrame] = None
    for tabla, columnas in tablas.items():
        df = obtener_datos_tabla(tabla, dias)
        if df.empty:
            continue
        df = df.set_index("timestamp").sort_index()
        diario = df.resample("D").mean().drop(columns=["id"], errors="ignore")
        diario = diario[columnas].dropna(how="all")
        if diario.empty:
            continue
        if combinado is None:
            combinado = diario
        else:
            combinado = combinado.join(diario, how="outer")

    if combinado is None or combinado.empty:
        print("⚠️ No se pudieron recuperar datos suficientes para el análisis de correlaciones.")
        return

    combinado = combinado.dropna(axis=1, how="all").dropna(how="any")
    if combinado.empty or combinado.shape[1] < 2:
        print("⚠️ Se requieren al menos dos variables con datos válidos para calcular correlaciones.")
        return

    matriz = combinado.corr(method="pearson")
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(matriz, cmap="coolwarm", annot=True, fmt="0.2f", linewidths=0.5, ax=ax)
    ax.set_title("Matriz de correlaciones")
    decorar_figura(fig, f"Correlaciones últimos {dias} días")
    guardar_figura(fig, "correlaciones", [f"{dias}dias"])


def analisis_alertas() -> None:
    dias = obtener_entero("¿Número de días para analizar alertas?", default=30)
    mostrar_progreso("Obteniendo alertas registradas")

    query = (
        "SELECT zona, especie, tipo_alerta, timestamp "
        "FROM alertas_criticas "
        "WHERE timestamp >= NOW() - INTERVAL %s DAY "
        "ORDER BY timestamp ASC"
    )
    alertas = consultar_dataframe(query, (dias,))
    if alertas.empty:
        print("⚠️ No se registraron alertas en el período seleccionado.")
        return

    conteos = alertas.groupby(["tipo_alerta"]).size().reset_index(name="frecuencia")
    imprimir_tabla(conteos)

    colores = [COLORES.get(tipo, "#FF6B6B") for tipo in conteos["tipo_alerta"]]

    fig_bar, ax_bar = plt.subplots(figsize=(9, 6))
    ax_bar.bar(conteos["tipo_alerta"], conteos["frecuencia"], color=colores)
    ax_bar.set_xlabel("Tipo de alerta")
    ax_bar.set_ylabel("Frecuencia")
    ax_bar.set_xticklabels(conteos["tipo_alerta"], rotation=20)
    decorar_figura(fig_bar, f"Frecuencia de alertas últimos {dias} días")
    guardar_figura(fig_bar, "alertas_frecuencia", [f"{dias}dias"])

    fig_pie, ax_pie = plt.subplots(figsize=(7, 7))
    ax_pie.pie(conteos["frecuencia"], labels=conteos["tipo_alerta"], colors=colores, autopct="%1.1f%%")
    ax_pie.axis("equal")
    decorar_figura(fig_pie, f"Distribución de alertas últimos {dias} días")
    guardar_figura(fig_pie, "alertas_distribucion", [f"{dias}dias"])


def comparativa_variables() -> None:
    variables = obtener_variable(mensaje="¿Variables a comparar separadas por coma?", multiple=True)
    dias = obtener_entero("¿Número de días para comparar?", default=30)
    mostrar_progreso("Generando comparativa normalizada")

    combinado: Optional[pd.DataFrame] = None
    for variable in variables:
        serie = obtener_series_variable(variable, dias)
        if serie.empty:
            print(f"⚠️ Sin datos para {variable}, se omitirá.")
            continue
        serie = serie.set_index("timestamp").resample("D").mean().rename(columns={variable: variable})
        if combinado is None:
            combinado = serie
        else:
            combinado = combinado.join(serie, how="outer")

    if combinado is None or combinado.dropna(how="all").empty:
        print("⚠️ No se encontraron datos suficientes para las variables solicitadas.")
        return

    combinado = combinado.sort_index().interpolate(limit_direction="both")
    normalizado = combinado.apply(lambda col: (col - col.mean()) / col.std(ddof=0) if col.std(ddof=0) else col * 0)
    normalizado = normalizado.dropna(how="all")
    if normalizado.empty:
        print("⚠️ Tras la normalización no quedaron datos suficientes para graficar.")
        return

    fig, ax = plt.subplots(figsize=(11, 6))
    for variable in variables:
        if variable not in normalizado.columns:
            continue
        ax.plot(normalizado.index, normalizado[variable], label=variable.replace("_", " ").title(), color=COLORES.get(variable, None))

    ax.set_xlabel("Fecha")
    ax.set_ylabel("Valor normalizado (z-score)")
    ax.legend()
    ax.grid(alpha=0.2)
    decorar_figura(fig, "Comparativa de variables normalizadas")
    guardar_figura(fig, "comparativa", ["_".join(variables), f"{dias}dias"])


def tabla_resumen_diario() -> None:
    dias = obtener_entero("¿Número de días a resumir?", default=7)
    mostrar_progreso("Construyendo resumen diario")

    resumen: Optional[pd.DataFrame] = None
    tablas = ["clima_data", "riego_data", "plantas_data"]
    for tabla in tablas:
        df = obtener_datos_tabla(tabla, dias)
        if df.empty:
            continue
        diario = df.set_index("timestamp").resample("D").mean().drop(columns=["id"], errors="ignore")
        diario.columns = [f"{tabla}_{col}" for col in diario.columns]
        if resumen is None:
            resumen = diario
        else:
            resumen = resumen.join(diario, how="outer")

    if resumen is None or resumen.empty:
        print("⚠️ No se pudieron generar promedios diarios con los datos disponibles.")
        return

    resumen = resumen.reset_index().rename(columns={"timestamp": "fecha"})
    imprimir_tabla(resumen)
    guardar_dataframe(resumen, "resumen_diario", [f"{dias}dias"])


def analisis_eficiencia() -> None:
    dias = obtener_entero("¿Número de días para analizar eficiencia?", default=30)
    mostrar_progreso("Analizando resultados de eficiencia")

    query = (
        "SELECT zona, especie, indice_estres, rendimiento_frutos, eficiencia_luz, necesidad_riego, ajuste_nutricion, timestamp "
        "FROM resultados_funciones "
        "WHERE timestamp >= NOW() - INTERVAL %s DAY "
        "ORDER BY timestamp ASC"
    )
    datos = consultar_dataframe(query, (dias,))
    if datos.empty:
        print("⚠️ No existen registros de eficiencia en el período seleccionado.")
        return

    datos["necesidad_riego"] = datos["necesidad_riego"].astype(float)
    diario = datos.set_index("timestamp").resample("D").mean(numeric_only=True)

    fig_eff, ax_eff = plt.subplots(figsize=(11, 6))
    ax_eff.plot(diario.index, diario.get("eficiencia_luz"), label="Eficiencia de luz", color=COLORES.get("eficiencia_luz", "#3A0CA3"))
    ax_eff.plot(diario.index, diario.get("rendimiento_frutos"), label="Rendimiento de frutos", color=COLORES.get("rendimiento_frutos", "#7209B7"))
    ax_eff.fill_between(diario.index, diario.get("indice_estres", 0), color=COLORES.get("indice_estres", "#FF0054"), alpha=0.1, label="Índice de estrés")
    ax_eff.set_xlabel("Fecha")
    ax_eff.set_ylabel("Promedio diario")
    ax_eff.legend()
    ax_eff.grid(alpha=0.2)
    decorar_figura(fig_eff, "Evolución de eficiencia del sistema")
    guardar_figura(fig_eff, "eficiencia_temporal", [f"{dias}dias"])

    datos_ordenados = datos.sort_values("timestamp")
    datos_ordenados["delta_min"] = datos_ordenados["timestamp"].diff().dt.total_seconds().div(60.0)
    tiempos = datos_ordenados.dropna(subset=["delta_min"])
    if not tiempos.empty:
        fig_time, ax_time = plt.subplots(figsize=(11, 5))
        ax_time.bar(tiempos["timestamp"], tiempos["delta_min"], color=COLORES.get("conductividad", "#1A535C"))
        ax_time.set_xlabel("Marca de tiempo")
        ax_time.set_ylabel("Minutos entre procesos")
        ax_time.grid(alpha=0.2)
        decorar_figura(fig_time, "Intervalos entre ejecuciones de funciones")
        guardar_figura(fig_time, "tiempos_procesamiento", [f"{dias}dias"])
    else:
        print("ℹ️ Sin suficientes registros para calcular tiempos de procesamiento.")


def analisis_riego() -> None:
    dias = obtener_entero("¿Número de días para analizar riego?", default=30)
    mostrar_progreso("Obteniendo métricas del sistema de riego")

    df = obtener_datos_tabla("riego_data", dias)
    if df.empty:
        print("⚠️ No se registraron datos de riego en el período seleccionado.")
        return

    fig_scatter, ax_scatter = plt.subplots(figsize=(9, 6))
    scatter = ax_scatter.scatter(df["ph"], df["conductividad"], c=df["flujo"], cmap="viridis", edgecolor="k", alpha=0.7)
    ax_scatter.set_xlabel("pH")
    ax_scatter.set_ylabel("Conductividad")
    ax_scatter.grid(alpha=0.2)
    cbar = fig_scatter.colorbar(scatter, ax=ax_scatter)
    cbar.set_label("Flujo")
    decorar_figura(fig_scatter, "Relación pH - Conductividad")
    guardar_figura(fig_scatter, "ph_conductividad", [f"{dias}dias"])

    df.set_index("timestamp", inplace=True)
    diario = df[["nivel_deposito", "flujo"]].resample("D").mean()
    fig_nivel, ax_nivel = plt.subplots(figsize=(11, 5))
    ax_nivel.plot(diario.index, diario["nivel_deposito"], color=COLORES.get("nivel_deposito", "#2EC4B6"), marker="o")
    ax_nivel.set_xlabel("Fecha")
    ax_nivel.set_ylabel("Nivel del depósito")
    ax_nivel.grid(alpha=0.2)
    decorar_figura(fig_nivel, "Evolución del nivel del depósito")
    guardar_figura(fig_nivel, "nivel_deposito", [f"{dias}dias"])

    flujo_stats = diario["flujo"].describe()
    print("\n📋 Patrones de flujo (promedio diario):")
    imprimir_tabla(flujo_stats.reset_index().rename(columns={"index": "indicador", "flujo": "valor"}))


def evolucion_plantas() -> None:
    dias = obtener_entero("¿Número de días para analizar crecimiento?", default=60)
    mostrar_progreso("Recopilando datos de crecimiento y salud")

    plantas = obtener_datos_tabla("plantas_data", dias)
    if plantas.empty:
        print("⚠️ No hay datos de plantas en el rango solicitado.")
        return

    plantas.set_index("timestamp", inplace=True)
    diario_plantas = plantas[["crecimiento", "nivel_salud", "calidad_frutos"]].resample("D").mean()

    fig_crecimiento, ax_crecimiento = plt.subplots(figsize=(11, 5))
    ax_crecimiento.plot(diario_plantas.index, diario_plantas["crecimiento"], color=COLORES.get("crecimiento", "#45B7D1"), marker="o")
    ax_crecimiento.set_xlabel("Fecha")
    ax_crecimiento.set_ylabel("Crecimiento promedio")
    ax_crecimiento.grid(alpha=0.2)
    decorar_figura(fig_crecimiento, "Evolución del crecimiento de plantas")
    guardar_figura(fig_crecimiento, "crecimiento_plantas", [f"{dias}dias"])

    clima = obtener_datos_tabla("clima_data", dias)
    if not clima.empty:
        clima.set_index("timestamp", inplace=True)
        diario_clima = clima[["temperatura", "humedad"]].resample("D").mean()
        combinado = diario_plantas.join(diario_clima, how="inner").dropna()
        fig_salud, ax_salud = plt.subplots(figsize=(9, 6))
        scatter = ax_salud.scatter(
            combinado["temperatura"],
            combinado["nivel_salud"],
            c=combinado["humedad"],
            cmap="coolwarm",
            s=100 * (combinado["calidad_frutos"].fillna(combinado["calidad_frutos"].mean()) / (combinado["calidad_frutos"].max() or 1)),
            edgecolor="k",
            alpha=0.7,
        )
        ax_salud.set_xlabel("Temperatura")
        ax_salud.set_ylabel("Nivel de salud")
        ax_salud.grid(alpha=0.2)
        cbar = fig_salud.colorbar(scatter, ax=ax_salud)
        cbar.set_label("Humedad")
        decorar_figura(fig_salud, "Salud vs. condiciones climáticas")
        guardar_figura(fig_salud, "salud_plantas", [f"{dias}dias"])

        if not combinado.empty:
            correlacion = combinado["crecimiento"].corr(combinado["temperatura"])
            print(f"\n🎯 Correlación crecimiento-temperatura: {correlacion:0.3f}")
    else:
        print("ℹ️ No se encontraron datos climáticos para correlacionar con el crecimiento.")


def mostrar_menu() -> str:
    print(
        """
=== CLIENTE DE ANÁLISIS ESTADÍSTICO ===
1. 📊 Estadísticas descriptivas básicas
2. 📈 Gráfico de tendencias temporales
3. 🔥 Heatmap de correlaciones
4. 🚨 Análisis de alertas frecuentes
5. 🌡️ Comparativa múltiple de variables
6. 📋 Tabla de resumen por día
7. 🎯 Análisis de eficiencia del sistema
8. 💧 Comportamiento del sistema de riego
9. 🌿 Evolución del crecimiento de plantas
0. ❌ Salir
"""
    )
    return leer_opcion_usuario("Seleccione una opción (0-9)")


ACCIONES_MENU: Dict[str, Callable[[], None]] = {
    "1": estadisticas_basicas,
    "2": tendencias_temporales,
    "3": heatmap_correlaciones,
    "4": analisis_alertas,
    "5": comparativa_variables,
    "6": tabla_resumen_diario,
    "7": analisis_eficiencia,
    "8": analisis_riego,
    "9": evolucion_plantas,
}


def ejecutar_menu() -> None:
    configurar_entorno()
    while True:
        try:
            opcion = mostrar_menu()
        except UserCancelled:
            print("\n👋 Operación cancelada por el usuario.")
            return

        if opcion == "0":
            print("\n👋 Hasta pronto.")
            return

        accion = ACCIONES_MENU.get(opcion)
        if not accion:
            print("⚠️ Selección no válida. Intente nuevamente.")
            continue

        try:
            accion()
        except UserCancelled:
            print("\nℹ️ Operación cancelada. No se realizaron cambios.")
        except mysql.connector.Error as error:
            print(f"❌ Error de base de datos: {error}")
        except Exception as error:  # pylint: disable=broad-except
            print(f"❌ Error inesperado: {error}")
        finally:
            input("\nPresione Enter para continuar...")


def main() -> None:
    try:
        ejecutar_menu()
    except KeyboardInterrupt:
        print("\n👋 Interrupción recibida. Saliendo del cliente.")
        sys.exit(0)


if __name__ == "__main__":
    main()
