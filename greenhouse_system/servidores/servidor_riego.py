# servidores/servidor_riego.py
import asyncio, random
from asyncua import Server

async def main():
    server = Server()
    await server.init()
    endpoint = "opc.tcp://0.0.0.0:4842/riego/"
    server.set_endpoint(endpoint)
    server.set_server_name("Servidor Sistema Riego")

    idx = await server.register_namespace("http://invernadero.org/riego")

    try:
        await server.import_xml("models/RiegoModel.xml")
    except Exception:
        pass

    async with server:
        print(f"Servidor riego escuchando en {endpoint}")

        # Crear objeto manualmente
        riego_obj = await server.nodes.objects.add_object(idx, "SistemaRiego")

        # Variables operacionales
        ph = await riego_obj.add_variable(idx, "pH", 6.5)
        conductividad = await riego_obj.add_variable(idx, "Conductividad", 1.8)
        flujo = await riego_obj.add_variable(idx, "Flujo", 2.0)
        nivel_deposito = await riego_obj.add_variable(idx, "NivelDeposito", 80.0)

        # Propiedades
        tipo_nutriente = await riego_obj.add_property(idx, "TipoNutriente", "Solución Hidropónica Base")
        estado_sistema = await riego_obj.add_property(idx, "EstadoSistema", "OPERATIVO")

        await ph.set_writable()
        await conductividad.set_writable()
        await flujo.set_writable()
        await nivel_deposito.set_writable()

        while True:
            ph_val = 6.5 + random.uniform(-0.3, 0.3)
            cond_val = 1.8 + random.uniform(-0.5, 0.5)
            flujo_val = 2.0 + random.uniform(-1.0, 1.0)
            nivel_val = 80 + random.uniform(-5, 5)

            await ph.write_value(float(round(ph_val, 2)))
            await conductividad.write_value(float(round(cond_val, 2)))
            await flujo.write_value(float(round(flujo_val, 2)))
            await nivel_deposito.write_value(float(round(nivel_val, 2)))

            await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
