import socket
import threading

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 4445
BUFFER_SIZE = 1024

# List to keep track of connected clients
clients = []

def handle_client(client_socket):
    print("player connected")
    while True:
        try:
            data = client_socket.recv(BUFFER_SIZE).decode()
            if data:
                broadcast_data(data, client_socket)
                
        except ConnectionResetError:
            remove_client(client_socket)
            break

def broadcast_data(data, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(data.encode())
                print(data)
            except socket.error:
                remove_client(client)

def remove_client(client_socket):
    if client_socket in clients:
        clients.remove(client_socket)
        client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen()

    print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")

    while True:
        client_socket,client_address = server_socket.accept()
        clients.append(client_socket)

        threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == '__main__':
    start_server()
