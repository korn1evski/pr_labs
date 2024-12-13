import asyncio
import websockets
import json
import os
from threading import Lock

file_lock = Lock()
shared_file = "shared_chat_data.txt"
connected_clients = set()

def save_message(data):
    with file_lock:
        with open(shared_file, "a") as f:
            f.write(json.dumps(data) + "\n")

def load_previous_messages():
    if not os.path.exists(shared_file):
        return []
    with file_lock:
        with open(shared_file, "r") as f:
            return [json.loads(line.strip()) for line in f.readlines()]

async def chat_room_handler(websocket):
    connected_clients.add(websocket)
    try:
        previous_messages = load_previous_messages()
        await websocket.send(json.dumps({"type": "history", "messages": previous_messages}))
        async for message in websocket:
            message_data = json.loads(message)
            message_data['sender'] = websocket.remote_address[1]
            save_message(message_data)
            await asyncio.wait([client.send(json.dumps(message_data)) for client in connected_clients if client != websocket])
    except websockets.exceptions.ConnectionClosed:
        print("A client has disconnected")
    finally:
        connected_clients.remove(websocket)

async def start_websocket_server():
    async with websockets.serve(chat_room_handler, "localhost", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(start_websocket_server())
