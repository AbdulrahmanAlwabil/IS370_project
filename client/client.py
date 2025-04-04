import socket
import pickle
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
            
        
    def create_user(self, username, password):
        if not self.client:
            print("No connection to the server.")
            return "Connection error"
        
        try:
            
            self.client.send(f'SIGNUP::{username}::{password}'.encode())
            
            # Wait for the server's response
            response = self.client.recv(1024).decode()
            return response
        except Exception as e:
            print(f"Error during authentication: {e}")
            return "Authentication failed"

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
        
    def retrieve_chat_history(self, receiver_username, chat_type):
        if not self.client:
            print("No connection to the server.")
            return "Connection error"

        try:
            self.client.send(f'GET-HISTORY::{self.username}::{receiver_username}::{chat_type}'.encode())
            
            # Wait for the server's response
            response = self.client.recv(8192).decode()
            chat_list = pickle.loads(response)
            return chat_list
        except Exception as e:
            print(f"Error during sending: {e}")
            return 'Loading list object has failed'
        
    def get_contacts(self):
        if not self.client:
            print("No connection to the server.")
            return []
        
        try:
            # Send request to server
            self.client.send(f'GET-CONTACTS::{self.username}'.encode())
            
            # First, receive the length prefix (4 bytes)
            length_bytes = b''
            while len(length_bytes) < 4:
                chunk = self.client.recv(4 - len(length_bytes))
                if not chunk:
                    print("Connection closed while receiving length prefix")
                    return []
                length_bytes += chunk
            
            # Convert bytes to integer
            length = int.from_bytes(length_bytes, byteorder='big')
            print(f"Expected data length: {length} bytes")
            
            # Receive the actual data
            data = b''
            while len(data) < length:
                bytes_to_receive = min(4096, length - len(data))
                chunk = self.client.recv(bytes_to_receive)
                if not chunk:
                    print(f"Connection closed unexpectedly. Received {len(data)}/{length} bytes")
                    return []
                data += chunk
                
            # Verify we got all the data
            if len(data) == length:
                print(f"Successfully received {len(data)} bytes")
                contacts_list = pickle.loads(data)
                return contacts_list
            else:
                print(f"Data length mismatch: received {len(data)}, expected {length}")
                return []
        except Exception as e:
            print(f"Error during retrieving contacts: {e}")
            return []
    
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