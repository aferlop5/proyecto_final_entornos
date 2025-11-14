# **Greenhouse System – Sprint 2**

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

## Futuras Ampliaciones

Actualmente **no existen funciones GET** para recuperar datos.  
Si se necesitasen, se podrían implementar en `database_handler.py` e importarlas donde fuesen necesarias.


## Pasos para la ejecución (Sensores, 3 terminales)

### 1. Clonar el repositorio
```bash
git clone https://github.com/aferlop5/proyecto_final_entornos
```

### 2. Entrar en la carpeta del proyecto y de greenhouse
```bash
cd proyecto_final_entornos/greenhouse_system
```

### 3. Crear entorno virtual
```bash
python3 -m venv .venv
```

### 4. Activar entorno virtual
```bash
source .venv/bin/activate
```

### 5. Instalar dependencias (en una sola terminal, ANTES de activar el entorno en las demás)
```bash
pip install -r requirements.txt
```

### 6. Ejecutar servidores en terminales separadas 

OJO: Con el entorno virtual activo en las tres terminales.

- Terminal 1: Servidor Clima
```bash
python servidores/servidor_clima.py
```

- Terminal 2: Servidor Riego
```bash
python servidores/servidor_riego.py
```

- Terminal 3: Servidor Plantas
```bash
python servidores/servidor_plantas.py
```

## Pasos para la ejecución (Database, 1 terminal)

### 1. Levantar base de datos MySQL con Docker
```bash
docker run -d \
  --name greenhouse-db \
  -e MYSQL_ROOT_PASSWORD=rootpass \
  -p 3306:3306 \
  -v greenhouse_data:/var/lib/mysql \
  mysql:8
```

### 2. Entrar en la carpeta del proyecto y de greenhouse
```bash
cd proyecto_final_entornos/greenhouse_system
```

### 3. Crear entorno virtual
```bash
python3 -m venv .venv
```

### 4. Activar entorno virtual
```bash
source .venv/bin/activate
```

### 5. Configurar la base de datos (solo una vez)
```bash
python database/database_setup.py
```

### 6. Acceder a la base de datos:

```bash
mysql -h 127.0.0.1 -P 3306 -u root -p
```

Con la contraseña "rootpass"

### 7. Dentro de la base de datos:

```bash
USE greenhouse;
```

Hay cinco tablas: riego_data, clima_data, plantas_data, resultados_funciones y alertas_criticas.
Para ver los datos (ejemplo):

```bash
SELECT * FROM clima_data LIMIT 10;
```

CTRL + D para salir


## Pasos para la ejecución (Middleware, 2 terminales)

### 1. Entrar en la carpeta del proyecto y de greenhouse
```bash
cd proyecto_final_entornos/greenhouse_system
```

### 2. Crear entorno virtual
```bash
python3 -m venv .venv
```

### 3. Activar entorno virtual
```bash
source .venv/bin/activate
```

### 4. Ejecutar servidores en terminales separadas 

OJO: Primero el servidor.

- Terminal 1: Servidor
```bash
python middleware/middleware_servidor.py
```

- Terminal 2: Cliente
```bash
python middleware/middleware_cliente.py
```
