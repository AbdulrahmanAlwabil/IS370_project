import socket
import threading
import pickle
from encryption import Encryptor
from client import Client
from database.db_manager import (
        authenticate_user as db_authenticate_user,
        create_message as db_create_message,
        create_user as db_create_user,
        create_group as db_create_group,
        add_user_to_group as db_add_user_to_group,
        get_chat_history as db_get_chat_history,
        get_contacts as db_get_contacts,
        get_user_groups as db_get_user_groups,
        get_group_members as db_get_group_members
    )

# List to store connected clients
connected_clients = []
username_to_socket = {} 
socket_to_encryptor = {}

# Function to handle communication with a client
def handle_client(client_socket, addr):
    print(f"Connected by {addr}")
    connected_clients.append((client_socket, addr))  # Add client to the list
    encryptor = Encryptor()  # Initialize encryptor for this connection
    client_object = None

    try:
        while True:
            encrypted_message = client_socket.recv(4096)
            if not encrypted_message:
                print(f"Connection closed by {addr}")
                break

            # Decrypt the received message
            message = encryptor.decrypt_to_string(encrypted_message)
            print(f"Decrypted message from {addr}: {message}")

            ### Handle LOGIN command ###
            if message.startswith("LOGIN::"):
                _, username, password = message.split("::")
                if db_authenticate_user(username, password):
                    response = "LOG_AUTH"
                    username_to_socket[username] = client_socket
                    socket_to_encryptor[client_socket] = encryptor
                else:
                    response = "LOG_DECL"
                # Encrypt the response
                client_socket.send(encryptor.encrypt(response))
            
            elif message.startswith("SIGNUP::"):
                _, username, password = message.split("::")
                result = db_create_user(username, password)
                if "registered" in result:
                    response = "SIGN_AUTH"
                else:
                    response = "SIGN_DECL"
                client_socket.send(encryptor.encrypt(response))
                

            elif message.startswith(
                "UNICAST-MSG::"
            ):  # UNICAST-MSG::MSG::FROM-USERNAME::TO-USERNAME
                _, msg, sender, receiver = message.split("::")
                db_create_message(sender, receiver, "unicast", msg)
                response = "MSG-SENT"
                client_socket.send(encryptor.encrypt(response))
                 # Forward the message to the recipient if they're online
                if receiver in username_to_socket:
                    recipient_socket = username_to_socket[receiver]
                    recipient_encryptor = socket_to_encryptor[recipient_socket]
                    # Format message for recipient: NEW-MSG::message::sender
                    notification = f"NEW-MSG::{msg}::{sender}"
                    recipient_socket.send(recipient_encryptor.encrypt(notification))
                
                
            elif message.startswith(
                "MULTICAST-MSG::"
            ):  # MULTICAST-MSG::MSG::FROM-USERNAME::GROUP-USERNAME
                _, msg, sender, group = message.split("::")
                db_create_message(sender, group, "multicast", msg)
                response = "MSG-SENT"
                client_socket.send(encryptor.encrypt(response))
                
                 # Forward to all group members who are online
                group_members = db_get_group_members(group)  # You need to implement this
                for member in group_members:
                    if member != sender and member in username_to_socket:
                        member_socket = username_to_socket[member]
                        member_encryptor = socket_to_encryptor[member_socket]
                        notification = f"NEW-GROUP-MSG::{msg}::{sender}::{group}"
                        member_socket.send(member_encryptor.encrypt(notification))
                            
                
            elif message.startswith("BROADCAST-MSG::"):
                _, msg, sender = message.split(
                    "::"
                )  # BROADCAST-MSG::MSG::FROM-USERNAME
                db_create_message(sender, None, "broadcast", msg)
                response = "MSG-SENT"
                client_socket.send(encryptor.encrypt(response))
            elif message.startswith(
                "GET-HISTORY::"
            ):  # GET-HISTORY::FROM-USERNAME::TO-USERNAME::TYPE
                _, sender, receiver, c_type = message.split("::")
                chat_list = db_get_chat_history(sender, receiver, c_type)

                data = pickle.dumps(chat_list)
                encrypted_data = encryptor.encrypt(data)
                client_socket.sendall(encrypted_data)
            elif message.startswith("GET-CONTACTS::"):
                _, sender = message.split("::")
                contact_list = db_get_contacts(sender)

                data = pickle.dumps(contact_list)
                encrypted_data = encryptor.encrypt(data)
                client_socket.sendall(encrypted_data)
            elif message.startswith("GET-GROUPS::"):  # GET-GROUPS::USERNAME
                _, username = message.split("::")

                groups = db_get_user_groups(username)
                data = pickle.dumps(groups)
                encrypted_data = encryptor.encrypt(data)
                client_socket.sendall(encrypted_data)
            elif message.startswith("CREATE-GROUP::"):
                _, group_name, creator, members_str = message.split("::")
                members = members_str.split("|")

                # Create the group
                db_create_group(group_name)

                # Add creator and all members to the group
                for username in [creator] + members:
                    db_add_user_to_group(username, group_name)

                response = "GROUP-CREATED-SUCCESS"
                client_socket.send(encryptor.encrypt(response))
            else:
                response = "Unknown request from client."
                client_socket.send(encryptor.encrypt(response))
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    # In the finally block of handle_client:
    finally:
        connected_clients.remove((client_socket, addr))
        # Remove the username mapping
        for username, sock in list(username_to_socket.items()):
            if sock == client_socket:
                del username_to_socket[username]
                break
        if client_socket in socket_to_encryptor:
            del socket_to_encryptor[client_socket]
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
server.bind(("25.11.190.207", 8080))
server.listen(20)
print("Server is listening on port 8080...")


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


    def find_client(username):
        for i in object_connected_clients:
            if i.username == username:
                return i    


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
