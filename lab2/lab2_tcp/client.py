import socket
import threading
import time

def client_task(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(('127.0.0.1', 65432))
        sock.sendall(command.encode('utf-8'))
        response = sock.recv(1024)
        print(f"Server response to '{command}': {response.decode('utf-8')}\n")

if __name__ == "__main__":
    time.sleep(1)
    client_commands = ["read", "write", "read", "write", "read", "read"]
    client_threads = []

    for command in client_commands:
        t = threading.Thread(target=client_task, args=(command,))
        client_threads.append(t)
        t.start()

    for t in client_threads:
        t.join()
