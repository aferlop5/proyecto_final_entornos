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

        # Lista de especies a simular
        especies = [
            {"nombre": "Tomate", "humedad_obj": 70.0, "ph_obj": 6.5},
            {"nombre": "Lechuga", "humedad_obj": 65.0, "ph_obj": 6.0},
            {"nombre": "Pimiento", "humedad_obj": 68.0, "ph_obj": 6.2}
        ]

        objetos_plantas = []

        for especie_info in especies:
            obj = await server.nodes.objects.add_object(idx, f"Planta_{especie_info['nombre']}")
            
            # Variables dinámicas
            crecimiento = await obj.add_variable(idx, "Crecimiento", random.uniform(10, 20))
            cantidad_frutos = await obj.add_variable(idx, "CantidadFrutos", 0)
            calidad_frutos = await obj.add_variable(idx, "CalidadFrutos", 0.0)

            # Variable estática
            especie_var = await obj.add_variable(idx, "EspeciePlanta", especie_info["nombre"])

            # Propiedades constantes
            humedad_obj = await obj.add_property(idx, "HumedadObjetivo", especie_info["humedad_obj"])
            ph_obj = await obj.add_property(idx, "PHObjetivo", especie_info["ph_obj"])

            # Hacer variables dinámicas escribibles
            await crecimiento.set_writable()
            await cantidad_frutos.set_writable()
            await calidad_frutos.set_writable()

            objetos_plantas.append({
                "crecimiento": crecimiento,
                "cantidad_frutos": cantidad_frutos,
                "calidad_frutos": calidad_frutos
            })

        # Loop de actualización de valores
        while True:
            for planta in objetos_plantas:
                # Crecimiento: +0.1 a +0.5 cm por ciclo, hasta 100 cm
                current_crec = await planta["crecimiento"].get_value()
                new_crec = min(100, current_crec + random.uniform(0.1, 0.5))
                await planta["crecimiento"].write_value(float(round(new_crec, 2)))

                # Cantidad de frutos: aleatorio entre 0 y 20, aumenta gradualmente
                current_frutos = await planta["cantidad_frutos"].get_value()
                new_frutos = min(20, current_frutos + random.randint(0, 2))
                await planta["cantidad_frutos"].write_value(int(new_frutos))

                # Calidad frutos: entre 50 y 100, variación aleatoria
                current_calidad = await planta["calidad_frutos"].get_value()
                new_calidad = max(50, min(100, current_calidad + random.uniform(-2, 2)))
                await planta["calidad_frutos"].write_value(float(round(new_calidad, 2)))

            await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
