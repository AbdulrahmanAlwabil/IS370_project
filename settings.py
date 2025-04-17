import os

IP = 'localhost'
PORT = 8080

UNICAST_LOG_PATH = os.path.join('logs', 'unicast_logs')
MULTICAST_LOG_PATH = os.path.join('logs', 'multicast_logs')
BROADCAST_LOG_PATH = os.path.join('logs', 'broadcast_logs')

ENCRYPTION_KEY_PATH = os.path.join('keys', 'encryption.key')

DATABASE_PATH = os.path.join('database', 'chat.db')