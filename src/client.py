import socket
from datetime import datetime as dt

# HOST = "127.0.0.1"  # The server's hostname or IP address
# PORT = 12345  # The port used by the server


def getHelp():
    help = """Connect to the server application           - /join <server_ip_add> <port>
Disconnect to the server application        - /leave
Register a unique handle or alias           - /register <handle>
Send file to server                         - /store <filename>
Request directory file list from a server   - /dir
Fetch a file from a server                  - /get <filename>
Request command help to output all Input
    Syntax commands for references          - /?"""
    return help

HOST, PORT= "", 0
user = ""
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

while True:
    command = input("Enter command: ")
    if "/join" in command:
        try:
            tmp = command.split(' ')
            HOST, PORT = tmp[1], int(tmp[2])
            s.connect((HOST, PORT))
            print("Connection to the File Exchange Server is successful!")
        except (ConnectionRefusedError, IndexError):
            print("Error: Connection to the Server has failed! Please check IP Address and Port Number.")
    elif "/leave" in command:
            s.close()
            print("Connection closed. Thank you!")
    elif "/register" in command:
        user = command.split(' ')[-1]
        # TODO create user handle
        print(f"Welcome {user}!")
    elif "/store" in command:
        filename = command.split(' ')[-1]
        # TODO send file to server
        timestamp = dt.now().strftime('%Y-%m-%d %H:%M:%S')
        if user == "":
            print("Error: Register a user first!")
        else:
            print(f"{user}<{timestamp}>: Uploaded {filename}")
    elif "/dir" in command:
        print()
    elif "/get" in command:
        filename = command.split(' ')[-1]
        print(f"File received from Server: {filename}")

    elif command == "/?":
        print(getHelp())
    else:
        print("ERROR: Unknown command!")