import socket

class Client:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect(('localhost', 8080))
            print("Connected to the server.")
        except ConnectionRefusedError:
            print("Failed to connect to the server. Ensure the server is running.")
            self.client = None

    def authenticate_user(self, username, password):
        if not self.client:
            print("No connection to the server.")
            return "Connection error"

        try:
            # Send login credentials to the server
            self.client.send(f'LOGIN::{username}::{password}'.encode())
            
            # Wait for the server's response
            response = self.client.recv(1024).decode()
            return response
        except Exception as e:
            print(f"Error during authentication: {e}")
            return "Authentication failed"

    def send_messages(self):
        if not self.client:
            print("No connection to the server.")
            return

        try:
            while True:
                message = input("Enter a message to send (or 'exit' to quit): ")
                if message.lower() == 'exit':
                    print("Closing connection...")
                    self.client.send("DISCONNECT".encode())
                    break
                self.client.send(message.encode())
                response = self.client.recv(1024).decode()
                print(f"Server response: {response}")
        except Exception as e:
            print(f"Error during communication: {e}")
        finally:
            self.client.close()

    