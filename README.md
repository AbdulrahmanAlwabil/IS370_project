

# To begin starting this application, you will need to configure a few things:

## 1
### You should have a Python environment set up (preferably a .venv folder).

## 2
### Use *pip install -r requirements.txt* in IDE terminal.

## 3
### You must configure the IP addresses & port numbers in the server & client. Here is how:
#### During development, we used a Hamachi network so we can remotely test the app. In the client file (that is, client/client.py) you should find in the constructor of the Client class (line 10) 2 attributes that reflect the port and IP address, you can change the IP to "localhost" to use the app locally. Also, you must change it in the server.py file, you will find it below the imports directly (line 22).

## 4
### After doing the three steps above, run server.py in a dedicated terminal (so the server runs and starts listening for new clients).

## 5
### Next, run client_main.py in another dedicated terminal. This module has the GUI functionality as well as maintaining communications with the client script.
### You can now sign up with a username and a password, and it should work as long as the server is running

## 6
### If you are using MacOS and find some trouble even after doing the 5  steps above, it might be caused by the file paths in database/db_manager.py and server.py. You can change the variable 'is_Windows' (line 4 in db_manager.py and line 26 in server.py) to True if you are using Windows, or to False if you are using MacOS. (This is a simple way to make sure that our app runs on both OSs.). By default is_Windows = False.

# Final Notes
### You can create multiple accounts, and every account created will be displayed to every other user. There is no need to add friends.
### You can get remote connections using network software such as Logmein Hamachi to test concurrency with other devices and clients.
### The server.py terminal shows logs of every request that has been sent by clients, as well as the body of each communication. Also, you can either: 1- view every connected client. or 2- exit the server (i.e. shut it down). 
### Message logs are viewed in the logs folder in the project directory. A log file is created dynamically once a chat has been initiated (that is, a message has been sent for the first time in that particular chat) 

# Accounts
## You can use the following accounts we created to test the app:
### abdulrahman, pass: 123
### omar, pass: 123
### mohamed, pass: 123
### fahad, pass: 123
### ali, pass: 123
### saqer, pass: 123
