from database.db_manager import create_user
from client.client import Client

# create_user('omar', '3333')
# create_user('abdulrahman', '1111')
client = Client()
print(client.authenticate_user('ammar', '3333'))

