import socket


def retrieve_page_body(host, port, path):
    # Create a standard TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server on the specified host and port
    client_socket.connect((host, port))

    # Send HTTP GET request to the server
    http_request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36\r\nConnection: close\r\n\r\n"
    client_socket.send(http_request.encode())

    # Receive the response
    response = b""
    while True:
        chunk = client_socket.recv(4096)  # Read in chunks of 4KB
        if not chunk:
            break
        response += chunk

    # Close socket
    client_socket.close()

    # Decode response to a string
    response_str = response.decode()

    # Find beginning of response body
    body_index = response_str.find('\r\n\r\n')
    if body_index != -1:
        response_text = response_str[body_index + 4:]  # Extract the body of the response
    else:
        print("Could not find the body of the response.")
        response_text = ""

    return response_text


# Call the function for HTTP on port 80
# print(retrieve_page_body("books.toscrape.com", 80, "/"))
