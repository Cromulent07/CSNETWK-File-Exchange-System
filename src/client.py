import socket
import threading
import json
import time
import os

BUFFER_SIZE = 1024
isConnected = False
server_address = None

def toServer(entry):
    global isConnected
    global server_address
    
    if not entry.startswith('/'):
        print("Error: That is not a command! Type /? for help.")
        return
    
    input_line = entry.split()
    command = input_line[0]
    params = input_line[1:]
    
    if command == "/join":
        if len(params) != 2:
            print("Invalid command syntax!")
            print("Usage: /join <server_ip_add> <port>")
        elif isConnected:
            print("Error: User is already connected to the server.")
        else:
            try:
                server_address = (params[0], int(params[1]))
                
                client_socket.sendto(json.dumps({"command": "join"}).encode(), server_address)
                print("Connection to the Server is successful!")
                time.sleep(0.1)
                client_socket.settimeout(3)
                client_socket.settimeout(None)
                isConnected = True
                
            except Exception as e:
                print("Error: Connection to the Server has failed! Please check IP Address and Port Number.")
                print(f"More details: {str(e)}")
                server_address = None
                return

    elif command == "/leave":
        if isConnected:
            if len(params) > 0:
                print("Error: There should be no parameters for leave.")
                print("Usage: /leave")
            else:
                client_socket.sendto(json.dumps({"command": "leave"}).encode(), server_address)
                print("Connection closed. Thank you!")
                time.sleep(0.1)
                isConnected = False
                server_address = None
        else:
            print("Error: Disconnection failed. Please connect to the server first.")

    elif command == "/register":
        if isConnected:
            if len(params) != 1:
                print("Error: Command parameters do not match or is not allowed.")
                print("Usage: /register <handle>")
            else:
                client_socket.sendto(json.dumps({"command": "register", "handle": params[0]}).encode(), server_address)
                print(f"Handle Registration Successful! Your Handle is now {params[0]}.")
                time.sleep(0.1)
        else:
            print("Error: Please connect to the server first.")

    elif command == "/store":
        if isConnected:
            if len(params) < 1:
                print("Error: Invalid command syntax!")
                print("Usage: /store <filename>")
            else:
                filename = params[0]
                try:
                    with open(filename, 'rb') as file:
                        file_data = file.read()
                        client_socket.sendto(json.dumps({"command": "store", "filename": filename, "data": file_data.decode('ISO-8859-1')}).encode(), server_address)
                        print(f"File {filename} sent to server.")
                        time.sleep(0.1)
                except FileNotFoundError:
                    print(f"Error: File not found.\n> ", end = "")
                except Exception as e:
                    print(f"Error: {str(e)}\n> ", end = "")
        else:
            print("Error: Please connect to the server first.")
        
    elif command == "/dir":
        if isConnected:
            try:
                client_socket.sendto(json.dumps({"command": "dir"}).encode(), server_address)
                time.sleep(0.1)
            except Exception as e:
                print("Error sending data:", e)            
        else:
            print("Error: Please connect to the server first.")

    elif command == "/get":
        if isConnected:
            if len(params) < 1:
                print("Error: Invalid command syntax!")
                print("Usage: /get <filename>")
            else:
                filename = params[0]
                try:
                    client_socket.sendto(json.dumps({"command": "get", "filename": filename}).encode(), server_address)
                    time.sleep(0.1)
                except Exception as e:
                    print("Error sending data:", e)
        else:
            print("Error: Please connect to the server first.")
            
    elif command == "/broadcast":
        if isConnected:
            if len(params) == 0:
                print("Error: Command parameters do not match or is not allowed.")
                print("Usage: /broadcast <message>")
            else:
                message = ' '.join(params)
                client_socket.sendto(json.dumps({"command" : "broadcast", "message" : message}).encode(), server_address)
        else:
            print('Error. Please connect to the server first.')
    
    elif command == "/unicast":
        if isConnected:
            if len(params) < 2:
                print("Error: Command parameters do not match or is not allowed.")
                print("Usage: /unicast <handle> <message>")
            else:
                handle = params[0]
                message = ' '.join(params[1:])
                client_socket.sendto(json.dumps({"command" : "unicast", "handle" : handle, "message" : message}).encode(), server_address)
        else:
            print('Error. Please connect to the server first.')
            
    elif command == "/cls":
        os.system('cls')

    elif command == "/?":
        print("Connect to the server application:               /join <server_ip_add> <port>")
        print("Disconnect to the server application:            /leave")
        print("Register a unique handle or alias:               /register <handle>")
        print("Send file to server:                             /store <filename>")
        print("Request directory file list from server:         /dir")
        print("Fetch a file from a server:                      /get <filename>")
        print("Send a message to all registered handles:        /broadcast <message>")
        print("Send a direct message to one handle:             /unicast <handle> <message>")
        print("Request command help:                            /?")
        print("Clear screen:                                    /cls")
    else:
        print("Command not found. Type /? for help.")

def fromServer(data):
    command = data['command']

    if 'message' in data:
        message = data['message']
    
    if command == "ping":
        ping_ack = {'command': 'ping'}
        client_socket.sendto(json.dumps(ping_ack).encode(), server_address)
        return
    
    elif command == "dir":
        if data['command'] == 'dir':
            print("File Server Directory:")
            for file in data['file_list']:
                filename = file[0]
                timestamp = file[1]
                user = file[2]
                print(f"{filename} <{timestamp}> : {user}")
        return

    elif command == "get":
        filename = data['filename']
        file_data = data['data'].encode('ISO-8859-1')
        try:
            with open(filename, 'wb') as file:
                file.write(file_data)
            file.close()
            print(f"File received from server:  {filename}")
        except Exception as e:
            print(f"Error: {str(e)}")
            
    elif command == "broadcast":
        sender = data['sender']
        message = f"[From {sender} to all]: {message}"
        print(f"{message}\n> ", end = "")
    
    elif command == "unicast":
        sender = data['sender']
        message = f"[From {sender} to you]: {message}"
        print(f"{message}\n> ", end = "")
        
    elif command == 'receipt':
        handle = data['handle']
        message = f"[From you to {handle}]: {message}"
        print("> ", end = "")

    elif command == 'server' or command == 'error':
        if 'message' in data:
            print(f"Server Message: {message}", end = "")

def receive():
    global isConnected
    
    while True:
        if isConnected:
            try:
                response = client_socket.recvfrom(BUFFER_SIZE)
                data = json.loads(response[0].decode())
                fromServer(data)
            except ConnectionResetError:
                print("Error: Connection to the Server has been lost!")
                isConnected = False
            except Exception as e:
                print(f"Error: {str(e)}")
   
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

thread = threading.Thread(target = receive)
thread.start()

print("File Exchange Client")
print("Enter a command. Type /? for help")
 
while True:
    entry = input("> ")
    toServer(entry)