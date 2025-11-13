# Greenhouse System - Sprint 1

## Descripción
El Sprint 1 tiene como objetivo levantar la infraestructura del sistema, incluyendo los tres servidores OPC UA que simulan los subsistemas del invernadero:

- **Servidor Clima Interior** - Temperatura, Humedad, CO₂ e Intensidad de Luz.
- **Servidor Sistema de Riego** - pH, Conductividad, Flujo y Nivel de Depósito.
- **Servidor Estado Plantas** - Crecimiento, Salud y Etapa de Desarrollo.

Cada servidor se ejecuta de manera independiente (cada uno en una terminal) y genera datos simulados en tiempo real.

## Estructura de Carpetas

```
greenhouse_system/
├── servidores/
│   ├── servidor_clima.py
│   ├── servidor_riego.py
│   └── servidor_plantas.py
├── models/
│   ├── ClimaModel.xml
│   ├── RiegoModel.xml
│   └── PlantasModel.xml
├── database/
│   └── database_setup.py
└── requirements.txt
```


## Pasos para la ejecución

### 1. Clonar el repositorio
```bash
git clone https://github.com/aferlop5/proyecto_final_entornos
```

### 2. Entrar en la carpeta del proyecto
```bash
cd proyecto_final_entornos
```

### 3. Levantar base de datos MySQL con Docker
```bash
docker run -d --name greenhouse-db \
  -e MYSQL_ROOT_PASSWORD=rootpass \
  -e MYSQL_DATABASE=greenhouse \
  -p 3306:3306 \
  -v greenhouse_mysql_data:/var/lib/mysql \
  mysql:8.0
```

### 4. Crear entorno virtual
```bash
python3 -m venv .venv
```

### 5. Activar entorno virtual
```bash
source .venv/bin/activate
```

### 6. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 7. Configurar la base de datos solo una vez
```bash
python database/database_setup.py
```

### 8. Ejecutar servidores en terminales separadas 

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

### 9. Acceder a la base de datos:

```bash
mysql -h 127.0.0.1 -P 3306 -u root -p
```

Con la contraseña "rootpass"

```bash
USE greenhouse;
```

Hay tres tablas (clima_data, riego_data, plant_data)

```bash
SELECT * FROM clima_data LIMIT 10;
```

CTRL + D para salir