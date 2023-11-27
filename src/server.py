import socket
import time
import json
import os
from datetime import datetime

BUFFER_SIZE = 1024

def fromClients(entry):
    message = json.loads(entry.decode())
    command = message['command']
    
    if command == "join":
        if address in clients:
            print(f"Client {address} has reconnected")
            jsonData = {'command': 'success', 'message': f"User {address} reconnected"}
            server_socket.sendto(json.dumps(jsonData).encode(), address)
        else:
            clients.update({address : None})
            print(f"Client {address} has connected")
            jsonData = {'command': 'success', 'message': "New user connected"}
            server_socket.sendto(json.dumps(jsonData).encode(), address)
                
    elif command == "leave":
        print(f"Client {clients[address]}:{address} disconnected")
        if clients[address] == None:
            message = "Unregistered user disconnected\n> "
        else:
            message = f"User {clients[address]} disconnected\n> "
        jsonData = {'command': 'server', 'message': message}
        
        for client_address in clients:
            if client_address != address:
                server_socket.sendto(json.dumps(jsonData).encode(), client_address)

    elif command == "register":
        handle = message['handle']
        if clients[address] != None:
            print(f"{address} ({clients[address]}) Attempted to register again")
            jsonData = {'command': 'error', 'message': "Error: Registration failed. You already have a username.\n> "}
        elif handle in clients.values():
            print(f"{address} handle registration failed")
            jsonData = {'command': 'error', 'message': "Error: Registration failed. Handle or alias already exists.\n> "}
        else:
            clients[address] = handle
            print(f"Username {handle} registered by {address}")
            jsonData = {'command': 'server', 'given' : 'register' , 'message': f"Welcome {handle}!\n> "}
        
        for client_address in clients:
            if client_address != address:
                server_socket.sendto(json.dumps(jsonData).encode(), client_address)
    elif command == "store":
        filename = message.get('filename')
        file_data = message.get('data')
        user = clients.get(address)

        try:
            with open(filename, 'wb') as file:
                file.write(file_data.encode('utf-8'))

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file_list.append((filename, timestamp, user))
            response_message = f"{user}<{timestamp}>: Uploaded {filename}"
            response = json.dumps({'command': 'server', 'message': response_message + "\n> "})
        except Exception as e:
            response = json.dumps({'command': 'error', 'message': str(e)} + "\n> ")
        
        for client_address in clients:
            if client_address != address:
                server_socket.sendto(json.dumps(response).encode(), client_address)
        
    elif command == "dir":
        try:
            if len(file_list) == 0:
                print("Error: No files in server.")
                jsonData = {'command': 'error', 'message': "Error: No files in server.\n> "}
            else:
                jsonData = {'command': 'dir', 'file_list': file_list}
            server_socket.sendto(json.dumps(jsonData).encode(), address)
        except Exception as e:
            print("Error sending response to client: " + e + "\n> ")
    
    elif command == "get":
        filename = message['filename']
        try:
            with open(filename, 'rb') as file:
                file_data = file.read()
                response = {"command": "get", "filename": filename, "data": file_data.decode('ISO-8859-1'), "message": "File sent successfully."}
            print("File sent to client successfully.")
        except FileNotFoundError:
            response = {"command": "error", "message": f"File {filename} not found.\n> "}
            print("File Not Found.")
        except Exception as e:
            response = {"command": "error", "message": str(e)}
            print(f"Error: {str(e)}\n> ")
        server_socket.sendto(json.dumps(response).encode(), address)
        
    elif command == "broadcast":
        if clients[address] == None:
            print(f"Client {address} Attempted to /broadcast without username")
            jsonData = {'command': 'error', 'message': "Error: You must register a handle first.\n> "}
            server_socket.sendto(json.dumps(jsonData).encode(), address)
            return
        message = f"{message['message']}"
        print(f"{address} > {message}")
        message_jsonData = {'command': 'broadcast', 'sender' : f'{clients[address]}', 'message': message}
        for client_address, client_handle in clients.items():
            if client_handle != None:
                server_socket.sendto(json.dumps(message_jsonData).encode(), client_address)
       
    elif command == "unicast":
        handle = message['handle']
        message = message['message']
        sender = clients[address]
        
        print(f"{sender} to {handle} : {message}")
        
        if sender == None:
            print(f"Client {address} Attempted to /unicast without username")
            jsonData = {'command': 'error', 'message': "Error: You must register a handle first.\n> "}
            server_socket.sendto(json.dumps(jsonData).encode(), address)
            return
        elif sender == handle:
            print(f"Client {address} Attempted to /unicast self")
            jsonData = {'command': 'error', 'message': "Error: You cannot message yourself.\n> "}
            server_socket.sendto(json.dumps(jsonData).encode(), address)
            return
        
        for client_address, client_handle in clients.items():
            if client_handle == handle:
                message_jsonData = {'command': 'unicast', 'sender' : sender, 'message': message}
                try:
                    server_socket.sendto(json.dumps(message_jsonData).encode(), client_address)
                    print(f"Direct Message Sent from {sender} to {handle}")
                    
                    receipt = f"{message}"
                    jsonData = {'command': 'receipt', 'given' : 'unicast', 'handle' : handle, 'message': receipt}
                    print(f"Receipt sent back to {sender}")
                except:
                    jsonData = {'command': 'error', 'message': "Error: Handle/alias does not exist.\n> "}
                
                server_socket.sendto(json.dumps(jsonData).encode(), address)
                return

def ping():
    for user in clients:
        print(f"Pinging user {user} : ", end="")
        ping_req = {'command': 'ping', 'message' : "Server ping"}
        server_socket.sendto(json.dumps(ping_req).encode(), user)
        
        time.sleep(0.3)
        try:
            server_socket.settimeout(3)
            server_socket.recvfrom(BUFFER_SIZE)
            print("Online")
        except Exception as e:
            print("Offline")
            disconnected.append(user)

clients = {}
disconnected = []
file_list = []

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)           
       
while True:
    print("File Exchange UDP Server")
    try:
        ip = input("Enter IP Address: ")
        port = input("Enter Port Number: ")
        server_socket.bind((ip, int(port)))
        print(f"Server is running on {ip}:{port}")
        break
    except Exception as e:
        os.system('cls')
        print(f"Error: {str(e)}")
        print("Try again\n")
        
while True:
    try:
        entry, address = server_socket.recvfrom(BUFFER_SIZE)
        fromClients(entry)
        
    except ConnectionResetError as e:
        print(f"ConnectionResetError: {e}")
        ping()
        
    except Exception as e:
        print(f"Error: {str(e)}")
    
    finally:
        for user in disconnected:
            print(f"User {clients[user]} : {user} offline. Disconnecting")
            clients.pop(user)
        disconnected.clear()