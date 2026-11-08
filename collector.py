import asyncio, os, time
from asyncua import Client
from influxdb_client import InfluxDBClient, Point, WritePrecision

OPC_URL = "opc.tcp://localhost:4840/teststand/"
NS_URI = "http://example.com/teststand"
POLL_HZ = 10

INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = os.environ["INFLUX_TOKEN"]
ORG = "teststand"
BUCKET = "telemetry"

async def connect_with_backoff(url: str) -> Client:
    delay = 1.0
    while True:
        client = Client(url)
        try:
            await client.connect()
            print("connected to PLC")
            return client
        except Exception as e:
            print(f"connect failed ({e}); retrying in {delay:.0f}s")
            await asyncio.sleep(delay)
            delay = min(delay * 2, 30.0)

async def poll_loop(client: Client, writer, nodes, names):
    period = 1.0 / POLL_HZ
    while True:
        tick = time.monotonic()
        values = await asyncio.gather(*(n.read_value() for n in nodes))
        now_ns = time.time_ns()
        points = [
            Point("sensor").tag("channel", name)
                           .field("value", float(v))
                           .time(now_ns, WritePrecision.NS)
            for name, v in zip(names, values)
        ]
        writer.write(bucket=BUCKET, org=ORG, record=points)
        await asyncio.sleep(max(0.0, period - (time.monotonic() - tick)))

async def main():
    influx = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
    writer = influx.write_api()  # batching writer, doesn't block the poll loop
    try:
        while True:
            client = await connect_with_backoff(OPC_URL)
            try:
                idx = await client.get_namespace_index(NS_URI)
                stand = await client.nodes.objects.get_child(f"{idx}:TestStand")
                nodes = await stand.get_children()
                names = [(await n.read_browse_name()).Name for n in nodes]
                await poll_loop(client, writer, nodes, names)
            except Exception as e:
                print(f"lost connection: {e}; reconnecting")
            finally:
                try:
                    await client.disconnect()
                except Exception:
                    pass
    finally:
        writer.close()
        influx.close()

if __name__ == "__main__":
    asyncio.run(main())