import socket
import threading
from database.db_manager import authenticate_user as db_authenticate_user

# List to store connected clients
connected_clients = []

# Function to handle communication with a client
def handle_client(client_socket, addr):
    print(f"Connected by {addr}")
    connected_clients.append((client_socket, addr))  # Add client to the list
    try:
        while True:
            message = client_socket.recv(1024).decode()
            if not message:
                print(f"Connection closed by {addr}")
                break

            print(f"Message from {addr}: {message}")

            # Handle LOGIN command
            if message.startswith("LOGIN::"):
                _, username, password = message.split("::")
                if db_authenticate_user(username, password):
                    client_socket.send("LOG_AUTH".encode())
                else:
                    client_socket.send("LOG_DECL".encode())
            else:
                client_socket.send("Unknown command.".encode())
    except ConnectionResetError:
        print(f"Connection reset by {addr}")
    finally:
        # Remove client from the list when disconnected
        connected_clients.remove((client_socket, addr))
        client_socket.close()

# Function to broadcast a message to all connected clients
def broadcast_message(message):
    for client_socket, addr in connected_clients:
        try:
            client_socket.send(message.encode())
        except Exception as e:
            print(f"Failed to send message to {addr}: {e}")

# Function to display connected clients
def view_connected_clients():
    print("Connected clients:")
    for _, addr in connected_clients:
        print(f" - {addr}")

# Main server setup
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 8080))
server.listen(20)
print("Server is listening on port 9999...")

# Thread to accept new clients
def accept_clients():
    while True:
        client, addr = server.accept()
        print(f"New connection from {addr}")
        client_thread = threading.Thread(target=handle_client, args=(client, addr))
        client_thread.start()

# Start the client-accepting thread
accept_thread = threading.Thread(target=accept_clients)
accept_thread.start()

def authenticate_user(username, password):
    """
    Authenticate a user by verifying their credentials against the database.
    """
    if db_authenticate_user(username, password):
        print(f"User '{username}' authenticated successfully.")
        return True
    else:
        print(f"Authentication failed for user '{username}'.")
        return False

# Command loop for the server admin
while True:
    command = input("Enter a command (broadcast/view/exit): ").strip().lower()
    if command == "broadcast":
        message = input("Enter the message to broadcast: ")
        broadcast_message(message)
    elif command == "view":
        view_connected_clients()
    elif command == "exit":
        print("Shutting down the server...")
        server.close()
        break
    else:
        print("Unknown command. Available commands: broadcast, view, exit.")