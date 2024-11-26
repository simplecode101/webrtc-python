import asyncio
import websockets

# 存储所有连接的客户端
connected_clients = set()

async def broadcast(message):
    # 向所有连接的客户端广播消息
    if connected_clients:  # 确保有客户端连接
        await asyncio.wait([client.send(message) for client in connected_clients])

async def handler(websocket):
    # 将新连接的客户端添加到集合中
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Received message: {message}")
            await broadcast(message)  # 广播接收到的消息
    finally:
        # 移除断开的客户端
        connected_clients.remove(websocket)

async def main():
    # 启动 WebSocket 服务器
    async with websockets.serve(handler, "localhost", 8765):
        print("WebSocket server started on ws://localhost:8765")
        await asyncio.Future()  # 运行直到被取消

# 启动事件循环
if __name__ == "__main__":
    asyncio.run(main())
