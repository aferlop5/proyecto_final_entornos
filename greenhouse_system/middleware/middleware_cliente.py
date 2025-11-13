import asyncio
from asyncua import Client

SERVIDORES = {
    "clima": "opc.tcp://localhost:4841/clima/",
    "riego": "opc.tcp://localhost:4842/riego/",
    "plantas": "opc.tcp://localhost:4843/plantas/"
}

class GreenhouseClient:
    def __init__(self):
        self.clients = {}

    async def conectar_servidores(self):
        for nombre, endpoint in SERVIDORES.items():
            client = Client(endpoint)
            await client.connect()
            print(f"Conectado a {nombre} en {endpoint}")
            self.clients[nombre] = client

    async def leer_datos_tiempo_real(self):
        datos = {}
        for nombre, client in self.clients.items():
            root = client.nodes.objects
            var_data = {}
            hijos = await root.get_children()
            for hijo in hijos:
                try:
                    props = await hijo.get_children()
                    for var in props:
                        nombre_var = await var.read_browse_name()
                        valor = await var.read_value()
                        var_data[nombre_var.Name] = valor
                except Exception:
                    pass
            datos[nombre] = var_data
        return datos

    async def desconectar(self):
        for client in self.clients.values():
            await client.disconnect()

# Prueba rápida BORRAR PARA UN FUTURO USO
if __name__ == "__main__":
    async def test():
        cliente = GreenhouseClient()
        await cliente.conectar_servidores()
        datos = await cliente.leer_datos_tiempo_real()
        print(datos)
        await cliente.desconectar()
    asyncio.run(test())