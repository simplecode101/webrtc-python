import asyncio
import websockets

async def client():
    async with websockets.connect("ws://localhost:8765") as websocket:
        print("Connected to the server.")
        while True:
            message = input("Enter a message to send (or 'exit' to quit): ")
            if message.lower() == 'exit':
                print("Exiting...")
                break
            await websocket.send(message)
            print(f"Sent message: {message}")

            response = await websocket.recv()
            print(f"Received echo: {response}")

if __name__ == "__main__":
    asyncio.run(client())
