import socket
import pickle
from encryption import Encryptor
import threading



class Client:
    def __init__(self):
        IP = "25.11.190.207"
        PORT = 8080
        
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.encryptor = Encryptor()  # Initialize the encryptor
        try:
            self.client.connect((IP, PORT))
            print("Connected to the server.")
            self.username = None
        except ConnectionRefusedError:
            print("Failed to connect to the server. Ensure the server is running.")
            self.client = None

    def send_encrypted_message(self, message):
        """Encrypt and send a message to the server."""
        if not self.client:
            return False
        try:
            encrypted_message = self.encryptor.encrypt(message)
            self.client.send(encrypted_message)
            return True
        except Exception as e:
            print(f"Error sending encrypted message: {e}")
            return False

    def receive_encrypted_message(self):
        """Receive and decrypt a message from the server."""
        if not self.client:
            return None
        try:
            encrypted_response = self.client.recv(4096)
            return self.encryptor.decrypt_to_string(encrypted_response)
        except Exception as e:
            print(f"Error receiving encrypted message: {e}")
            return None

    def send_encrypted_object(self, obj):
        """Pickle, encrypt and send an object to the server."""
        if not self.client:
            return False
        try:
            pickled_data = pickle.dumps(obj)
            encrypted_data = self.encryptor.encrypt(pickled_data)
            self.client.send(encrypted_data)
            return True
        except Exception as e:
            print(f"Error sending encrypted object: {e}")
            return False

    def receive_encrypted_object(self):
        """Receive, decrypt and unpickle an object from the server."""
        if not self.client:
            return None
        try:
            encrypted_data = self.client.recv(8192)
            decrypted_data = self.encryptor.decrypt(encrypted_data)
            return pickle.loads(decrypted_data)
        except Exception as e:
            print(f"Error receiving encrypted object: {e}")
            return None

    def create_user(self, username, password):
        if not self.client:
            print("No connection to the server.")
            return "Connection error"

        try:
            self.send_encrypted_message(f"SIGNUP::{username}::{password}")

            # Wait for the server's response
            response = self.receive_encrypted_message()
            return response
        except Exception as e:
            print(f"Error during authentication: {e}")
            return "Authentication failed"

    def authenticate_user(self, username, password):
        if not self.client:
            print("No connection to the server.")
            return "Connection error"

        try:
            # Send login credentials encrypted
            self.send_encrypted_message(f"LOGIN::{username}::{password}")

            # Receive encrypted response
            response = self.receive_encrypted_message()
            if "AUTH" in response:
                self.username = username
            return response
        except Exception as e:
            print(f"Error during authentication: {e}")
            return "Authentication failed"

    def retrieve_chat_history(self, receiver_username, chat_type):
        if not self.client:
            print("No connection to the server.")
            return []

        try:
            self.sending = True
            self.send_encrypted_message(
                f"GET-HISTORY::{self.username}::{receiver_username}::{chat_type}"
            )

            # Wait for the server's response
            response = self.receive_encrypted_object()
            self.sending = False
            
            if response is None:
                print("No chat history received")
                return []
                
            chat_list = list(response)
            return chat_list

        except Exception as e:
            print(f"Error retrieving chat history: {e}")
            self.sending = False
            return []  # Return empty list on error

    def get_contacts(self):
        if not self.client:
            print("No connection to the server.")
            return []

        try:
            # Send request to server
            self.send_encrypted_message(f"GET-CONTACTS::{self.username}")
            data = self.receive_encrypted_object()

            contacts_list = list(data)

            return contacts_list

        except Exception as e:
            print(f"Error during retrieving contacts: {e}")
            return []

    def get_user_groups(self):
        if not self.client:
            print("No connection to the server.")
            return []

        try:
            # Send request to server
            self.send_encrypted_message(f"GET-GROUPS::{self.username}")
            data = self.receive_encrypted_object()

            groups = list(data)

            return groups

        except Exception as e:
            print(f"Error during retrieving groups: {e}")
            return []

    def create_group(self, group_name, members):
        if not self.client:
            print("No connection to the server.")
            return False

        try:
            # Convert the list to a string with a special delimiter
            members_str = "|".join(members)

            # Format: CREATE-GROUP::group_name::creator_username::member1|member2|...
            self.send_encrypted_message(
                f"CREATE-GROUP::{group_name}::{self.username}::{members_str}"
            )

            # Wait for the server's response
            response = self.receive_encrypted_message()

            if "SUCCESS" in response:
                return True
            else:
                return False
        except Exception as e:
            print(f"Error creating group: {e}")
            return False

    def send_unicast(self, receiver, msg):
        if not self.client:
            print("No connection to the server.")
            return False

        try:
            # Set flag that we're sending a message
            self.sending = True
            
            # Send the message
            self.send_encrypted_message(
                f"UNICAST-MSG::{msg}::{self.username}::{receiver}"
            )
            
              
            try:
                # Keep checking if there's data to receive
                encrypted_response = self.client.recv(4096)
                if encrypted_response:
                    response = self.encryptor.decrypt_to_string(encrypted_response)
                    self.sending = False
                    return "MSG-SENT" in response
            except Exception as e:
                print(f"Error waiting for response: {e}")
                
            
            self.sending = False
            return True  # Assume success even if we didn't get a response
        except Exception as e:
            print(f"Error during sending: {e}")
            self.sending = False
            return False

    def send_multicast(self, group, msg):
        if not self.client:
            print("No connection to the server.")
            return False

        try:
            # Set flag that we're sending a message
            self.sending = True
            
            # Send the message
            self.send_encrypted_message(
                f"MULTICAST-MSG::{msg}::{self.username}::{group}"
            )
            
            try:
                # Keep checking if there's data to receive
                encrypted_response = self.client.recv(4096)
                if encrypted_response:
                    response = self.encryptor.decrypt_to_string(encrypted_response)
                    self.sending = False
                    return "MSG-SENT" in response
                
            except Exception as e:
                print(f"Error waiting for response: {e}")
                
            
            
            self.sending = False
            return True  # Assume success even if we didn't get a response
        except Exception as e:
            print(f"Error during sending: {e}")
            self.sending = False
            return False

    def send_broadcast(self, msg):
        if not self.client:
            print("No connection to the server.")
            return False

        try:
            # Set flag that we're sending a message
            self.sending = True
            
            # Send the message
            self.send_encrypted_message(f"BROADCAST-MSG::{msg}::{self.username}")
            
            try:
                encrypted_response = self.client.recv(4096)
                if encrypted_response:
                    response = self.encryptor.decrypt_to_string(encrypted_response)
                    self.sending = False
                    return "MSG-SENT" in response
                
            except Exception as e:
                print(f"Error waiting for response: {e}")
                
            
            self.sending = False
            return True
        except Exception as e:
            print(f"Error during sending: {e}")
            self.sending = False
            return False

    def start_listening(self):
        def listen_for_messages():
            while True:
                try:
                    import select
                    ready_to_read, _, _ = select.select([self.client], [], [], 0.1)
                    
                    if ready_to_read:
                        try:
                            encrypted_data = self.client.recv(4096)
                            if not encrypted_data:
                                print("Connection closed by server")
                                break
                                
                            message = self.encryptor.decrypt_to_string(encrypted_data)
                            print(f"Received message: {message}")
                            
                            if message.startswith("NEW-MSG::"):
                                try:
                                    _, content, sender = message.split("::")
                                    if hasattr(self, 'message_callback'):
                                        self.message_callback(sender, content)
                                except ValueError:
                                    print(f"Error parsing message format: {message}")
                                    
                            elif message.startswith("NEW-GROUP-MSG::"):
                                try:
                                    _, content, sender, group = message.split("::")
                                    if hasattr(self, 'group_message_callback'):
                                        self.group_message_callback(group, sender, content)
                                except ValueError:
                                    print(f"Error parsing group message format: {message}")
                                    
                            elif message.startswith("NEW-BROADCAST-MSG::"):
                                try:
                                    _, content, sender = message.split("::")
                                    if hasattr(self, 'broadcast_message_callback'):
                                        self.broadcast_message_callback(sender, content)
                                except ValueError:
                                    print(f"Error parsing broadcast message format: {message}")
                                    
                            elif message.startswith("NEW-GROUP-ADDED::"):
                                try:
                                    _, group_name, creator = message.split("::")
                                    print(f"Group add notification received: {group_name} by {creator}")
                                    if hasattr(self, 'group_added_callback'):
                                        self.group_added_callback(group_name, creator)
                                except ValueError:
                                    print(f"Error parsing group added message: {message}")
                                    
                            elif "MSG-SENT" in message:
                                # This is a response to a send operation
                                self.sending = False
                                
                        except Exception as e:
                            print(f"Error processing message: {e}")
                            if hasattr(self, 'server_disconnected_callback'):
                                self.server_disconnected_callback()
                            break
                            
                except Exception as e:
                    print(f"Error in listening thread: {e}")
                    import time
                    time.sleep(0.5)
                        
        threading.Thread(target=listen_for_messages, daemon=True).start()