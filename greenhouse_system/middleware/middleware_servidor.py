import asyncio
import json
import signal
import sys
from datetime import datetime
from pathlib import Path

import database_handler as db
import algoritmos


def _ensure_package_root() -> None:
    """Garantiza que el paquete `greenhouse_system` sea importable.

    Cuando se ejecuta este script como archivo dentro del propio directorio
    `greenhouse_system/`, el import absoluto falla porque Python no ve el
    directorio padre en `sys.path`. Añadimos el padre si es necesario.
    """
    if "greenhouse_system" in sys.modules:
        return
    try:
        import greenhouse_system  # type: ignore # noqa:F401
        return
    except ModuleNotFoundError:
        parent = Path(__file__).resolve().parents[1]  # directorio greenhouse_system
        project_root = parent.parent  # padre que contiene greenhouse_system
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        try:
            import greenhouse_system  # type: ignore # noqa:F401
        except ModuleNotFoundError:
            pass


_ensure_package_root()

from greenhouse_system.informes.latex_generator import ReportGenerator  # noqa:E402

HOST = "127.0.0.1"
PORT = 5000


class GracefulShutdown:
    def __init__(self, report_generator: ReportGenerator | None = None):
        self.report_generator = report_generator or ReportGenerator()
        self.server = None
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def register_server(self, server) -> None:
        self.server = server

    def shutdown(self, signum, frame):
        print("Generando informe final...")
        try:
            result = self.report_generator.generate_daily_report("informe_final", compile_pdf=True)
            pdf_path = result.get("pdf")
            tex_path = result.get("tex")
            if pdf_path:
                print(f"Informe PDF generado en {pdf_path}")
            if tex_path:
                print(f"Informe LaTeX disponible en {tex_path}")
        except Exception as exc:  # pragma: no cover - logging en parada
            print(f"Error al generar el informe final: {exc}")
        if self.server:
            self.server.close()
        sys.exit(0)


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
                    problema = algoritmos.alerta_critica(
                        clima.get("Temperatura"),
                        clima.get("CO2"),
                        planta.get("NivelSalud"),
                        clima.get("IntensidadLuz")
                    )

                    # Si hay un problema (string), insertar; si es None, no hacer nada
                    if problema is not None:
                        db.insertar_alerta(
                            zona,
                            especie,
                            problema
                        )

        except json.JSONDecodeError:
            print("Mensaje recibido no es JSON:", message)

    writer.close()
    await writer.wait_closed()
    print(f"Conexión cerrada {addr}")


async def main(shutdown_handler: GracefulShutdown | None = None):
    shutdown_handler = shutdown_handler or GracefulShutdown()
    server = await asyncio.start_server(handle_client, HOST, PORT)
    addr = server.sockets[0].getsockname()
    print(f"Middleware servidor escuchando en {addr}")

    shutdown_handler.register_server(server)

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    shutdown_handler = GracefulShutdown()
    asyncio.run(main(shutdown_handler))
