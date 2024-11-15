import asyncio
import websockets
import json
import os
from threading import Lock

# Shared resources
file_lock = Lock()
shared_file = "shared_chat_data.txt"
connected_clients = set()

# Function to save message to the shared file
def save_message(data):
    with file_lock:
        with open(shared_file, "a") as f:
            f.write(json.dumps(data) + "\n")

# Function to load all previous messages from the shared file
def load_previous_messages():
    if not os.path.exists(shared_file):
        return []
    with file_lock:
        with open(shared_file, "r") as f:
            return [json.loads(line.strip()) for line in f.readlines()]

# Chat Room WebSocket Handler
async def chat_room_handler(websocket):
    # Add the new client
    connected_clients.add(websocket)
    try:
        # Send all previous messages to the newly connected client
        previous_messages = load_previous_messages()
        await websocket.send(json.dumps({"type": "history", "messages": previous_messages}))

        # Handle incoming messages from this client
        async for message in websocket:
            message_data = json.loads(message)
            # Add sender information to the message
            message_data['sender'] = websocket.remote_address[1]  # Using port as a simple identifier

            # Save the message to the shared file
            save_message(message_data)

            # Broadcast the message to all connected clients
            await asyncio.wait([client.send(json.dumps(message_data)) for client in connected_clients if client != websocket])
    except websockets.exceptions.ConnectionClosed:
        print("A client has disconnected")
    finally:
        # Remove the client from connected clients
        connected_clients.remove(websocket)

# Run WebSocket Server
async def start_websocket_server():
    async with websockets.serve(chat_room_handler, "localhost", 8765):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(start_websocket_server())