from database.db_manager import create_user
from client.client import Client

# create_user('omar', '3333')
# create_user('abdulrahman', '1111')
client = Client()

while True:
    msg = input("Enter a message for server: ")
    client.client.send(msg.encode())

