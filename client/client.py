import socket

class Client:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect(('25.11.190.207', 8080))
            print("Connected to the server.")
            self.username = None
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
            if 'AUTH' in response:
                self.username = username
            return response
        except Exception as e:
            print(f"Error during authentication: {e}")
            return "Authentication failed"
    
    def send_unicast(self, reciever, msg):
        if not self.client:
            print("No connection to the server.")
            return "Connection error"

        try:
            self.client.send(f'UNICAST-MSG::{msg}::{self.username}::{reciever}'.encode())
            
            # Wait for the server's response
            response = self.client.recv(4096).decode()
            return True
        except Exception as e:
            print(f"Error during sending: {e}")
            return False

    def send_multicast(self, group, msg):
        if not self.client:
            print("No connection to the server.")
            return "Connection error"

        try:
           
            self.client.send(f'MULTICAST-MSG::{msg}::{self.username}::{group}'.encode())
            
            # Wait for the server's response
            response = self.client.recv(4096).decode()
            return True
        except Exception as e:
            print(f"Error during sending: {e}")
            return False

    def send_broadcast(self, msg):
        
        if not self.client:
            print("No connection to the server.")
            return "Connection error"

        try:
           
            self.client.send(f'BROADCAST-MSG::{msg}::{self.username}'.encode())
            
            # Wait for the server's response
            response = self.client.recv(4096).decode()
            return True
        except Exception as e:
            print(f"Error during sending: {e}")
            return False