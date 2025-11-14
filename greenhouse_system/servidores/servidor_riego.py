import asyncio, random
from asyncua import Server

async def main():
    server = Server()
    await server.init()
    endpoint = "opc.tcp://0.0.0.0:4843/riego/"
    server.set_endpoint(endpoint)
    server.set_server_name("Servidor Riego")
    idx = await server.register_namespace("http://invernadero.org/riego")

    async with server:
        print(f"Servidor Riego escuchando en {endpoint}")
        obj = await server.nodes.objects.add_object(idx, "Riego")
        riego_obj = {
            "obj": obj,
            "pH": await obj.add_variable(idx, "pH", 6.5),
            "Conductividad": await obj.add_variable(idx, "Conductividad", 1.8),
            "Flujo": await obj.add_variable(idx, "Flujo", 2.0),
            "NivelDeposito": await obj.add_variable(idx, "NivelDeposito", 80.0),
            "CaudalHistorico": await obj.add_variable(idx, "CaudalHistorico", 1.5)
        }
        for var_name in riego_obj:
            if var_name != "obj":
                await riego_obj[var_name].set_writable()

        while True:
            await riego_obj["pH"].write_value(round(6 + random.uniform(-0.5,0.5),2))
            await riego_obj["Conductividad"].write_value(round(1.5 + random.uniform(-0.3,0.3),2))
            await riego_obj["Flujo"].write_value(round(1.8 + random.uniform(-0.5,0.5),2))
            await riego_obj["NivelDeposito"].write_value(round(50 + random.uniform(0,50),2))
            await riego_obj["CaudalHistorico"].write_value(round(random.uniform(1,3),2))
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
