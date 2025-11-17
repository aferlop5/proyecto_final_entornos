# **Greenhouse System – Sprint 3**

## Sensores

El sistema se alimenta de tres archivos **.xml**, cada uno asociado a un servidor OPC UA que publica datos cada **3 segundos** dentro de rangos lógicos.

### **Servidor de Clima**
Variables:  
**Temperatura**, **Humedad**, **CO₂**, **IntensidadLuz**, **Presión**, **Zona**

### **Servidor de Sistema de Riego**
Variables:  
**pH**, **Conductividad**, **Flujo**, **Nivel_deposito**, **Caudal_historico**

### **Servidor de Estado de Plantas**
Variables:  
**Especie**, **Crecimiento**, **Cantidad_frutos**, **Calidad_frutos**, **Nivel_salud**

Los servidores publican los datos en endpoints OPC UA con el formato:  
`opc.tcp://0.0.0.0:4841/<nombre_servidor>/`

Desde el Sprint 3 todos los servidores actualizan sus variables **cada 2 segundos** para una visualización más ágil en el dashboard.

---

## Base de Datos

La base de datos está formada por **5 tablas**:

- **3 tablas** almacenan los datos *crudos* provenientes de los sensores.  
- **1 tabla** almacena los datos ya procesados por el servidor.  
- **1 tabla** registra las alertas o emergencias detectadas.

El sistema utiliza **Docker + MySQL**, recomendado sobre **WSL 22.04**.  
La descripción completa de las tablas puede consultarse en `database_setup.py`.

---

## Middleware

El módulo **middleware_cliente**:

- Lee los datos de los tres endpoints OPC UA.  
- Construye un **JSON** con toda la información.  
- Envía ese JSON al **middleware_servidor** mediante **socket TCP**.

El módulo **middleware_servidor**:

1. Inserta los valores crudos en las tres primeras tablas.  
2. Procesa los datos mediante las funciones de `algoritmos.py` y guarda los resultados en la cuarta tabla.  
3. Ejecuta la función de emergencias (también en `algoritmos.py`) e inserta los eventos detectados en la quinta tabla.

---

## Sprint 3 – Panel de Control Web

Se añade un dashboard web basado en **Dash + Plotly** que muestra en tiempo real los KPIs principales, gráficas históricas y alertas activas:

- Carpeta `dashboard/` con los módulos `app.py`, `layout.py`, `callbacks.py`, `data_fetcher.py` y estilos en `assets/style.css`.
- El dashboard refresca la información cada 2 segundos empleando consultas a MySQL mediante `DataFetcher`.
- Visualizaciones específicas:
  - Clima: gauge de temperatura, líneas para humedad/CO₂/presión y zona activa.
  - Riego: indicadores de pH y conductividad, barra de nivel del depósito y líneas de flujo/caudal.
  - Plantas: barras de progreso de crecimiento/salud e indicadores de cantidad y calidad de frutos.
  - Alertas: panel coloreado según severidad.

> Nota: `requirements.txt` incluye ahora `dash` y `plotly`. Instálalas dentro del entorno virtual antes de levantar el dashboard.


## Guía de ejecución actualizada (Sprint 3)

### Preparar entorno (una sola vez por sesión)

```bash
cd /home/Agusti/tercero/primer_quatri/entornos/proyecto_final/proyecto_final_entornos/greenhouse_system
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Base de datos

```bash
docker run -d --name greenhouse-db -e MYSQL_ROOT_PASSWORD=rootpass -p 3306:3306 -v greenhouse_data:/var/lib/mysql mysql:8
cd /home/Agusti/tercero/primer_quatri/entornos/proyecto_final/proyecto_final_entornos/greenhouse_system
source .venv/bin/activate
python3 database/database_setup.py
```

Si el contenedor ya existe de ejecuciones anteriores, simplemente vuelve a iniciarlo con:

```bash
docker start greenhouse-db
```

### Sensores OPC UA (3 terminales, siempre dentro de `.../greenhouse_system` con el venv activo)

```bash
# Terminal A
python3 servidores/servidor_clima.py

# Terminal B
python3 servidores/servidor_riego.py

# Terminal C
python3 servidores/servidor_plantas.py
```

### Middleware (2 terminales adicionales, mismo directorio y venv)

```bash
# Terminal D (servidor primero)
python3 middleware/middleware_servidor.py

# Terminal E
python3 middleware/middleware_cliente.py
```

### Dashboard web (1 terminal más)

```bash
cd /home/Agusti/tercero/primer_quatri/entornos/proyecto_final/proyecto_final_entornos/greenhouse_system
source .venv/bin/activate
python3 -m dashboard.app
```

Abrir `http://127.0.0.1:8050` en el navegador.

### Verificación opcional en MySQL

```bash
mysql -h 127.0.0.1 -P 3306 -u root -p
USE greenhouse;
SELECT * FROM clima_data ORDER BY timestamp DESC LIMIT 5;
```
