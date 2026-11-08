import asyncio, random, time
from asyncua import Server
from sim.signals import CHANNELS

URI = "http://example.com/teststand"
ENDPOINT = "opc.tcp://0.0.0.0:4840/teststand/"

async def main():
    server = Server()
    await server.init()
    server.set_endpoint(ENDPOINT)
    idx = await server.register_namespace(URI)

    stand = await server.nodes.objects.add_object(idx, "TestStand")
    nodes = {}
    for ch in CHANNELS:
        nodes[ch.name] = await stand.add_variable(idx, ch.name, 0.0)

    start = time.monotonic()
    async with server:
        print("OPC UA server running at", ENDPOINT)
        while True:
            t = time.monotonic() - start
            for ch in CHANNELS:
                if random.random() < ch.dropout_prob:
                    continue  # skipped update: the value goes stale
                value = ch.fn(t) + random.gauss(0, ch.noise_std)
                await nodes[ch.name].write_value(value)
            await asyncio.sleep(0.1)  # 10 Hz

if __name__ == "__main__":
    asyncio.run(main())