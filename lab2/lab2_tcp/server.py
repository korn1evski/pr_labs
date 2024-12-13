import socket
import threading
import time
import random

file_lock = threading.Lock()
write_in_progress = threading.Event()

FILE_PATH = "shared_file.txt"

class TCPServer:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server listening on {self.host}:{self.port}")

    def start(self):
        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                print(f"Accepted connection from {client_address}")
                client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_handler.start()
        except KeyboardInterrupt:
            print("Shutting down the server.")
        finally:
            self.server_socket.close()

    def handle_client(self, client_socket):
        with client_socket:
            while True:
                message = client_socket.recv(1024).decode('utf-8')
                command = message.strip().lower()

                if command == "read":
                    self.handle_read(client_socket)
                elif command == "write":
                    self.handle_write(client_socket)
                elif command == "exit":
                    client_socket.sendall(b"Goodbye!")
                    break
                else:
                    client_socket.sendall(b"Unknown command. Use 'read', 'write', or 'exit'.")

    def handle_read(self, client_socket):
        if write_in_progress.is_set():
            client_socket.sendall(b"Write operation in progress. Please try again later.")
        else:
            try:
                with open(FILE_PATH, 'r') as file:
                    data = file.read()
                    client_socket.sendall(data.encode('utf-8'))
            except FileNotFoundError:
                client_socket.sendall(b"File not found. No data to read.")

    def handle_write(self, client_socket):
        write_in_progress.set()
        with file_lock:
            time.sleep(random.randint(1, 2))
            data_to_write = f"Data written at {time.ctime()} by {threading.current_thread().name}\n"
            with open(FILE_PATH, 'a') as file:
                file.write(data_to_write)
            client_socket.sendall(b"Write operation completed successfully.")
        write_in_progress.clear()

if __name__ == "__main__":
    server = TCPServer()
    server.start()