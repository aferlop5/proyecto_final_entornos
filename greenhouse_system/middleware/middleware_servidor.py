import asyncio
import json
from datetime import datetime
import database_handler as db
import algoritmos

HOST = "127.0.0.1"
PORT = 5000

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Conexión desde {addr}")

    while True:
        data = await reader.read(4096)
        if not data:
            break
        message = data.decode()
        try:
            json_data = json.loads(message)
            print("----- JSON recibido -----")
            print(json.dumps(json_data, indent=2))
            print("-------------------------\n")

            # ---- Inserción de datos crudos ----
            for zona, values in json_data.get("clima", {}).items():
                db.insertar_clima(
                    zona,
                    values.get("Temperatura"),
                    values.get("Humedad"),
                    values.get("CO2"),
                    values.get("IntensidadLuz"),
                    values.get("Presion", 1013)  # Valor por defecto si no existe
                )

            for especie, values in json_data.get("plantas", {}).items():
                db.insertar_planta(
                    especie,
                    values.get("Crecimiento"),
                    values.get("CantidadFrutos"),
                    values.get("CalidadFrutos"),
                    values.get("NivelSalud")
                )

            for riego_name, values in json_data.get("riego", {}).items():
                db.insertar_riego(
                    values.get("pH"),
                    values.get("Conductividad"),
                    values.get("Flujo"),
                    values.get("NivelDeposito"),
                    values.get("CaudalHistorico")
                )

            # ---- Procesamiento de algoritmos ----
            hora_actual = datetime.now().hour
            for zona, clima in json_data.get("clima", {}).items():
                for especie, planta in json_data.get("plantas", {}).items():
                    # Índice de estrés
                    estres = algoritmos.indice_estres(
                        clima.get("Temperatura"),
                        clima.get("Humedad"),
                        clima.get("CO2"),
                        planta.get("NivelSalud")
                    )
                    # Rendimiento de frutos
                    rendimiento = algoritmos.rendimiento_frutos(
                        planta.get("CantidadFrutos"),
                        planta.get("CalidadFrutos"),
                        planta.get("Crecimiento")
                    )
                    # Eficiencia de luz
                    eficiencia = algoritmos.eficiencia_luz(
                        clima.get("IntensidadLuz"),
                        hora_actual,
                        planta.get("Crecimiento")
                    )
                    # Necesidad de riego
                    necesidad = algoritmos.necesidad_riego(
                        json_data["riego"]["Riego"].get("NivelDeposito"),
                        json_data["riego"]["Riego"].get("Flujo"),
                        clima.get("Temperatura"),
                        clima.get("Humedad")
                    )
                    # Ajuste nutrición
                    ajuste = algoritmos.ajuste_nutricion(
                        planta.get("NivelSalud"),
                        json_data["riego"]["Riego"].get("pH"),
                        json_data["riego"]["Riego"].get("Conductividad")
                    )

                    # Insertar resultados
                    db.insertar_resultado_funcion(
                        zona,
                        especie,
                        estres,
                        rendimiento,
                        eficiencia,
                        necesidad,
                        ajuste
                    )

                    # ---- Alertas críticas ----
                    if algoritmos.alerta_critica(
                        clima.get("Temperatura"),
                        clima.get("CO2"),
                        planta.get("NivelSalud"),
                        clima.get("IntensidadLuz")
                    ):
                        db.insertar_alerta(
                            zona,
                            especie,
                            "CONDICION_CRITICA",
                            True,
                        )

        except json.JSONDecodeError:
            print("Mensaje recibido no es JSON:", message)

    writer.close()
    await writer.wait_closed()
    print(f"Conexión cerrada {addr}")


async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    addr = server.sockets[0].getsockname()
    print(f"Middleware servidor escuchando en {addr}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
