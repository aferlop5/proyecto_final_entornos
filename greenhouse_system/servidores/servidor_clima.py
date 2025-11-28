import asyncio, random, datetime
from asyncua import Server

async def main():
    server = Server()
    await server.init()
    endpoint = "opc.tcp://0.0.0.0:4841/clima/"
    server.set_endpoint(endpoint)
    server.set_server_name("Servidor Clima")
    idx = await server.register_namespace("http://invernadero.org/clima")

    async with server:
        print(f"Servidor Clima escuchando en {endpoint}")
        zonas = ["Zona_A", "Zona_B"]
        clima_objs = {}
        for zona in zonas:
            obj = await server.nodes.objects.add_object(idx, zona)
            clima_objs[zona] = {
                "obj": obj,
                "Temperatura": await obj.add_variable(idx, "Temperatura", 23.0),
                "Humedad": await obj.add_variable(idx, "Humedad", 65.0),
                "CO2": await obj.add_variable(idx, "CO2", 450.0),
                "IntensidadLuz": await obj.add_variable(idx, "IntensidadLuz", 800.0),
                "Presion": await obj.add_variable(idx, "Presion", 1013.0)
            }
            for var_name in clima_objs[zona]:
                if var_name != "obj":
                    await clima_objs[zona][var_name].set_writable()

        while True:
            hora = datetime.datetime.now().hour
            for zona, datos in clima_objs.items():
                await datos["Temperatura"].write_value(round(22 + random.uniform(-2.5, 2.5),2))
                await datos["Humedad"].write_value(round(65 + random.uniform(-8, 8),2))
                await datos["CO2"].write_value(round(450 + random.uniform(-55, 55),2))
                light = 800 if 8 <= hora <= 18 else random.uniform(10, 200)
                await datos["IntensidadLuz"].write_value(float(round(light,2)))
                await datos["Presion"].write_value(round(1013 + random.uniform(-5,5),2))
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())