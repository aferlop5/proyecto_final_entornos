# servidores/servidor_clima.py
import asyncio, random, datetime
from asyncua import Server

async def main():
    server = Server()
    await server.init()
    endpoint = "opc.tcp://0.0.0.0:4841/clima/"
    server.set_endpoint(endpoint)
    server.set_server_name("Servidor Clima Interior")

    idx = await server.register_namespace("http://invernadero.org/clima")

    # Importar XML (opcional, solo para referencia)
    try:
        await server.import_xml("models/ClimaModel.xml")
    except Exception:
        pass

    async with server:
        print(f"Servidor clima escuchando en {endpoint}")

        # Crear objeto manualmente
        clima_obj = await server.nodes.objects.add_object(idx, "ClimaInterior")

        # Variables operacionales
        temperatura = await clima_obj.add_variable(idx, "Temperatura", 23.0)
        humedad = await clima_obj.add_variable(idx, "Humedad", 65.0)
        co2 = await clima_obj.add_variable(idx, "CO2", 450.0)
        luz = await clima_obj.add_variable(idx, "IntensidadLuz", 800.0)

        # Propiedades
        ubicacion = await clima_obj.add_property(idx, "UbicacionZona", "Zona A - Cultivo Principal")
        timestamp = await clima_obj.add_property(idx, "TimestampUltimaActualizacion",
                                                 datetime.datetime.now(datetime.timezone.utc))

        await temperatura.set_writable()
        await humedad.set_writable()
        await co2.set_writable()
        await luz.set_writable()

        while True:
            hora = datetime.datetime.now().hour
            base_temp = 22 + (3 * (1 if 10 <= hora <= 18 else -1))
            temp = base_temp + random.uniform(-1.5, 1.5)
            hum = 65 + random.uniform(-8, 8)
            c = 450 + random.uniform(-50, 200)
            light = 800 if 8 <= hora <= 18 else random.uniform(10, 200)

            await temperatura.write_value(float(round(temp, 2)))
            await humedad.write_value(float(round(hum, 2)))
            await co2.write_value(float(round(c, 2)))
            await luz.write_value(float(round(light, 2)))
            await timestamp.write_value(datetime.datetime.now(datetime.timezone.utc))

            await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
