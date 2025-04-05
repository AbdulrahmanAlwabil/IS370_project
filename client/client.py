import socket
import pickle
from encryption import Encryptor


class Client:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.encryptor = Encryptor()  # Initialize the encryptor
        try:
            self.client.connect(("25.11.190.207", 8080))
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
            return "Connection error"

        try:
            self.send_encrypted_message(
                f"GET-HISTORY::{self.username}::{receiver_username}::{chat_type}"
            )

            # Wait for the server's response
            response = self.receive_encrypted_object()

            chat_list = list(response)
            return chat_list

        except Exception as e:
            print(f"Error during sending: {e}")
            return "Loading list/dict object has failed"

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

    def send_unicast(self, reciever, msg):
        if not self.client:
            print("No connection to the server.")
            return "Connection error"

        try:
            self.send_encrypted_message(
                f"UNICAST-MSG::{msg}::{self.username}::{reciever}"
            )

            # Wait for the server's response
            response = self.receive_encrypted_message()
            return True
        except Exception as e:
            print(f"Error during sending: {e}")
            return False

    def send_multicast(self, group, msg):
        if not self.client:
            print("No connection to the server.")
            return "Connection error"

        try:
            self.send_encrypted_message(
                f"MULTICAST-MSG::{msg}::{self.username}::{group}"
            )

            # Wait for the server's response
            response = self.receive_encrypted_message()
            return True
        except Exception as e:
            print(f"Error during sending: {e}")
            return False

    def send_broadcast(self, msg):

        if not self.client:
            print("No connection to the server.")
            return "Connection error"

        try:
            self.send_encrypted_message(f"BROADCAST-MSG::{msg}::{self.username}")

            # Wait for the server's response
            response = self.receive_encrypted_message()
            return True
        except Exception as e:
            print(f"Error during sending: {e}")
            return False
