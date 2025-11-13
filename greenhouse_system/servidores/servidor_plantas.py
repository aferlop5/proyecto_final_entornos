import asyncio, random, datetime
from asyncua import Server

async def main():
    server = Server()
    await server.init()
    endpoint = "opc.tcp://0.0.0.0:4843/plantas/"
    server.set_endpoint(endpoint)
    server.set_server_name("Servidor Estado Plantas")

    idx = await server.register_namespace("http://invernadero.org/plantas")

    async with server:
        print(f"Servidor plantas escuchando en {endpoint}")

        # Crear objeto manualmente bajo Objects
        plantas_obj = await server.nodes.objects.add_object(idx, "EstadoPlantas")

        # Variables operacionales
        crecimiento = await plantas_obj.add_variable(idx, "Crecimiento", 15.0)
        salud = await plantas_obj.add_variable(idx, "Salud", 85.0)

        # Propiedades (opcional)
        especie = await plantas_obj.add_property(idx, "EspeciePlanta", "Tomate")
        dias_siembra = await plantas_obj.add_property(idx, "DiasDesdeSiembra", 0)
        parametros_optimos = await plantas_obj.add_property(idx, "ParametrosOptimos", "{}")

        # Permitir escritura en las variables
        await crecimiento.set_writable()
        await salud.set_writable()

        while True:
            # Simulación dinámica
            current_crec = await crecimiento.get_value()
            crecimiento_val = min(100, current_crec + random.uniform(0, 1))
            await crecimiento.write_value(float(round(crecimiento_val, 2)))

            current_salud = await salud.get_value()
            salud_val = max(0, min(100, current_salud + random.uniform(-5, 5)))
            await salud.write_value(float(round(salud_val, 2)))

            await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
