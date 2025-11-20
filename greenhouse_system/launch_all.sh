#!/bin/bash

# Obtener ruta absoluta del directorio donde está este script
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"

# Activar entorno virtual si existe
if [ -d "$BASE_DIR/.venv" ]; then
    # shellcheck source=/dev/null
    source "$BASE_DIR/.venv/bin/activate"
    echo "Entorno virtual activado (.venv)"
else
    echo "[AVISO] No se encontró .venv. Usando python del sistema."
fi

# Función para liberar puertos ocupados
kill_port() {
    PORT=$1
    echo "Comprobando puerto $PORT..."
    PIDS=$(sudo lsof -ti:$PORT)
    if [ -n "$PIDS" ]; then
        echo "Puerto $PORT ocupado por PID(s): $PIDS. Matando proceso(s)..."
        sudo kill -9 $PIDS
        sleep 1
    fi
}

echo "=== Lanzando sistema completo ==="
echo "Directorio base: $BASE_DIR"
echo ""

# Liberar puertos que usamos
kill_port 4841
kill_port 4842
kill_port 4843
kill_port 5000

echo "Puertos libres. Continuando..."
echo ""

###############################
# 1. Servidores OPC UA
###############################
echo "Lanzando servidores OPC UA..."

python3 "$BASE_DIR/servidores/servidor_clima.py" &
PID_CLIMA=$!

python3 "$BASE_DIR/servidores/servidor_riego.py" &
PID_RIEGO=$!

python3 "$BASE_DIR/servidores/servidor_plantas.py" &
PID_PLANTAS=$!

echo "Servidores OPC UA en ejecución:"
echo " - clima:   $PID_CLIMA"
echo " - riego:   $PID_RIEGO"
echo " - plantas: $PID_PLANTAS"

sleep 3

###############################
# 2. Middleware: servidor
###############################
echo "Lanzando middleware_servidor.py..."
python3 "$BASE_DIR/middleware/middleware_servidor.py" &
PID_MW_SERV=$!

echo "middleware_servidor PID: $PID_MW_SERV"
sleep 3

###############################
# 3. Middleware: cliente
###############################
echo "Lanzando middleware_cliente.py..."
python3 "$BASE_DIR/middleware/middleware_cliente.py" &
PID_MW_CLIENT=$!

echo "middleware_cliente PID: $PID_MW_CLIENT"
echo ""
echo "=== Todos los servicios están en ejecución ==="
echo "Pulsa CTRL+C para cerrar todo de forma segura."
echo ""

################################
# Manejar CTRL+C y matar todo
################################
trap "echo 'Cerrando servicios...'; \
      kill $PID_CLIMA $PID_RIEGO $PID_PLANTAS $PID_MW_SERV $PID_MW_CLIENT 2>/dev/null; \
      exit 0" SIGINT

wait
