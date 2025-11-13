import asyncio, random, datetime
from asyncua import Server

async def main():
    server = Server()
    await server.init()
    endpoint = "opc.tcp://0.0.0.0:4841/clima/"
    server.set_endpoint(endpoint)
    server.set_server_name("Servidor Clima Interior")

    idx = await server.register_namespace("http://invernadero.org/clima")

    async with server:
        print(f"Servidor clima escuchando en {endpoint}")

        # Crear objetos para Zona A y Zona B
        zonas = ["Zona A - Cultivo Principal", "Zona B - Cultivo Secundario"]
        clima_objs = {}
        for zona in zonas:
            obj = await server.nodes.objects.add_object(idx, zona.replace(" ", "_"))
            clima_objs[zona] = {
                "obj": obj,
                "Temperatura": await obj.add_variable(idx, "Temperatura", 23.0),
                "Humedad": await obj.add_variable(idx, "Humedad", 65.0),
                "CO2": await obj.add_variable(idx, "CO2", 450.0),
                "IntensidadLuz": await obj.add_variable(idx, "IntensidadLuz", 800.0),
                "UbicacionZona": await obj.add_property(idx, "UbicacionZona", zona),
                "TimestampUltimaActualizacion": await obj.add_property(
                    idx, "TimestampUltimaActualizacion", datetime.datetime.now(datetime.timezone.utc)
                )
            }

            # Variables escribibles
            for var_name in ["Temperatura", "Humedad", "CO2", "IntensidadLuz"]:
                await clima_objs[zona][var_name].set_writable()

        # Loop de simulación
        while True:
            hora = datetime.datetime.now().hour
            for zona, datos in clima_objs.items():
                # Simulación de clima
                base_temp = 22 + (3 * (1 if 10 <= hora <= 18 else -1))
                temp = base_temp + random.uniform(-1.5, 1.5)
                hum = 65 + random.uniform(-8, 8)
                co2_val = 450 + random.uniform(-50, 200)
                light = 800 if 8 <= hora <= 18 else random.uniform(10, 200)

                await datos["Temperatura"].write_value(float(round(temp, 2)))
                await datos["Humedad"].write_value(float(round(hum, 2)))
                await datos["CO2"].write_value(float(round(co2_val, 2)))
                await datos["IntensidadLuz"].write_value(float(round(light, 2)))
                await datos["TimestampUltimaActualizacion"].write_value(
                    datetime.datetime.now(datetime.timezone.utc)
                )

            await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
