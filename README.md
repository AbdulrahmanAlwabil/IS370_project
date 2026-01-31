# IS370 Project

A secure client-server messaging application with end-to-end encryption.

## Features

- User authentication and registration
- Encrypted messaging (unicast, multicast, broadcast)
- Group chat functionality
- Message history logging
- GUI interface built with CustomTkinter

## Requirements

- Python 3.x
- Dependencies listed in requirements.txt

## Installation

1. Set up a Python virtual environment:
   ```
   python -m venv .venv
   ```

2. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

Edit settings.py to configure network settings:
- Set IP address (use 'localhost' for local testing)
- Set PORT to an available port number

## Usage

1. Start the server:
   ```
   python server.py
   ```

2. In a separate terminal, start the client:
   ```
   python client_main.py
   ```

3. Create a new account or log in with existing credentials

## Project Structure

- server.py - Server implementation handling client connections
- client_main.py - GUI application entry point
- client/client.py - Client communication logic
- encryption.py - Encryption/decryption implementation
- database/db_manager.py - Database operations
- settings.py - Configuration file

## Test Accounts

The following test accounts are available:
- abdulrahman:123
- omar:123
- mohamed:123
- fahad:123
- ali:123
- saqer:123

## Notes

- All connected users are visible to each other
- Message logs are stored in the logs folder
- Server terminal displays connection logs and request details
- For remote testing, use network tools like Hamachi
