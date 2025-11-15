import asyncio, random
from asyncua import Server

async def main():
    server = Server()
    await server.init()
    endpoint = "opc.tcp://0.0.0.0:4842/plantas/"
    server.set_endpoint(endpoint)
    server.set_server_name("Servidor Plantas")
    idx = await server.register_namespace("http://invernadero.org/plantas")

    async with server:
        print(f"Servidor Plantas escuchando en {endpoint}")
        plantas = ["Tomates", "Pimientos"]
        plantas_objs = {}
        for planta in plantas:
            obj = await server.nodes.objects.add_object(idx, planta)
            plantas_objs[planta] = {
                "obj": obj,
                "Crecimiento": await obj.add_variable(idx, "Crecimiento", 15.0),
                "CantidadFrutos": await obj.add_variable(idx, "CantidadFrutos", 0),
                "CalidadFrutos": await obj.add_variable(idx, "CalidadFrutos", 0.0),
                "EspeciePlanta": await obj.add_variable(idx, "EspeciePlanta", planta),
                "NivelSalud": await obj.add_variable(idx, "NivelSalud", 85.0)
            }
            for var_name in plantas_objs[planta]:
                if var_name != "obj":
                    await plantas_objs[planta][var_name].set_writable()

        while True:
            for planta, datos in plantas_objs.items():
                await datos["Crecimiento"].write_value(round(10 + random.uniform(0, 5),2))
                await datos["CantidadFrutos"].write_value(random.randint(0, 10))
                await datos["CalidadFrutos"].write_value(round(random.uniform(0, 100),2))
                await datos["NivelSalud"].write_value(round(random.uniform(70,100),2))
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
