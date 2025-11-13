import asyncio
from middleware_cliente import GreenhouseClient
from database_handler import DatabaseManager
from algoritmos import ControladorPID

async def loop_principal():
    db = DatabaseManager()
    cliente = GreenhouseClient()
    await cliente.conectar_servidores()
    pid = ControladorPID()

    try:
        while True:
            datos = await cliente.leer_datos_tiempo_real()
            for origen, vars in datos.items():
                db.insertar_datos_sensores(origen, vars)

                # Alerta simple
                if "Temperatura" in vars and (vars["Temperatura"] > 30 or vars["Temperatura"] < 15):
                    db.registrar_alerta(origen, "ALERTA", f"Temperatura crítica: {vars['Temperatura']}")

            await asyncio.sleep(5)
    except KeyboardInterrupt:
        print("Cerrando middleware...")
    finally:
        await cliente.desconectar()
        db.cerrar()

if __name__ == "__main__":
    asyncio.run(loop_principal())
