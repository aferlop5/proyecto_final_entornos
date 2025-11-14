import asyncio
import json
from asyncua import Client, ua

MIDDLEWARE_SERVER_IP = "127.0.0.1"
MIDDLEWARE_SERVER_PORT = 5000

# Endpoints de los servidores OPC UA
ENDPOINTS = {
    "clima": "opc.tcp://127.0.0.1:4841/clima/",
    "plantas": "opc.tcp://127.0.0.1:4842/plantas/",
    "riego": "opc.tcp://127.0.0.1:4843/riego/"
}

def serialize_value(value):
    """Convierte valores no serializables a formato JSON seguro"""
    if isinstance(value, (int, float, str, bool)):
        return value
    elif hasattr(value, "isoformat"):  # datetime
        return value.isoformat()
    else:
        return str(value)

async def read_relevant_variables(client, relevant_nodes):
    """Lee solo los nodos de interés definidos en relevant_nodes"""
    data = {}
    objects = await client.nodes.objects.get_children()
    for obj in objects:
        name = await obj.read_browse_name()
        node_name = name.Name

        # Solo procesar nodos que están en relevant_nodes
        if node_name in relevant_nodes:
            data[node_name] = {}
            for var in await obj.get_children():
                var_class = await var.read_node_class()
                if var_class == ua.NodeClass.Variable:
                    var_name = (await var.read_browse_name()).Name
                    value = await var.read_value()
                    data[node_name][var_name] = serialize_value(value)
    return data

async def send_to_server(json_data):
    reader, writer = await asyncio.open_connection(MIDDLEWARE_SERVER_IP, MIDDLEWARE_SERVER_PORT)
    writer.write(json_data.encode())
    await writer.drain()
    writer.close()
    await writer.wait_closed()

async def main():
    async with Client(ENDPOINTS["clima"]) as clima_client, \
               Client(ENDPOINTS["plantas"]) as plantas_client, \
               Client(ENDPOINTS["riego"]) as riego_client:

        print("Middleware cliente conectado a servidores OPC UA")
        
        # Definir solo los nodos que nos interesan
        relevant_clima = ["Zona_A", "Zona_B"]
        relevant_plantas = ["Tomates", "Pimientos"]
        relevant_riego = ["Riego"]

        while True:
            clima_data = await read_relevant_variables(clima_client, relevant_clima)
            plantas_data = await read_relevant_variables(plantas_client, relevant_plantas)
            riego_data = await read_relevant_variables(riego_client, relevant_riego)

            payload = {
                "clima": clima_data,
                "plantas": plantas_data,
                "riego": riego_data,
                "timestamp": str(asyncio.get_event_loop().time())
            }

            json_payload = json.dumps(payload)
            await send_to_server(json_payload)
            print(f"Enviado: {json.dumps(payload, indent=2)}\n")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
