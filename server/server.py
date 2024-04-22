import socket
import time
import json
import os
import base64
import threading
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from datetime import datetime

BUFFER_SIZE = 1024
SERVER_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Server:
    def __init__(self, root):
        self.root = root
        self.clients = {}
        self.disconnected = []
        self.file_list = []
        self.file_data_list = []
        self.timestamp_list = []
        self.uploader_list = []
        self.setup_gui()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.root.protocol("WM_DELETE_WINDOW", self.close_server_window)
    
    def setup_gui(self):
        self.ip_name = tk.Label(self.root, text="IP Address:")
        self.ip_name.grid(row=0, column=0, padx=5, pady=5)

        self.ip = tk.Entry(self.root, width=15)
        self.ip.grid(row=0, column=1, padx=5, pady=5)

        self.port_name = tk.Label(self.root, text="Port:")
        self.port_name.grid(row=0, column=2, padx=5, pady=5)

        self.port = tk.Entry(self.root, width=5)
        self.port.grid(row=0, column=3, padx=5, pady=5)

        self.start_button = tk.Button(self.root, text="Start Server", command=self.start_server)
        self.start_button.grid(row=1, column=1, columnspan=2, padx=5, pady=5)

        self.chat_box = scrolledtext.ScrolledText(self.root, height=15, width=50)
        self.chat_box.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
    
    def output_print(self, message):
        self.chat_box.insert(tk.END, message + "\n")
        self.chat_box.see(tk.END)

    def start_server(self):
        ip = self.ip.get()
        port = self.port.get()
        try:
            self.server_socket.bind((ip, int(port)))
            self.output_print(f"Server is running on {ip}:{port}")
            server_thread = threading.Thread(target=self.run_server, daemon=True)
            server_thread.start()
        except Exception as e:
            self.output_print(f"Error: {str(e)}")
            self.output_print("Try again\n")

    def run_server(self):
        while True:
            try:
                entry, address = self.server_socket.recvfrom(BUFFER_SIZE)
                self.fromClients(entry, address)
            except ConnectionResetError as e:
                self.output_print(f"ConnectionResetError: {e}")
                self.ping()
            except Exception as e:
                self.output_print(f"Error: {str(e)}")
                self.output_print("Default server exception tracker")
            finally:
                for user in self.disconnected:
                    self.output_print(f"User {self.clients[user]} : {user} offline. Disconnecting")
                    self.clients.pop(user)
                self.disconnected.clear()
    
    def close_server_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()

    def fromClients(self, entry, address):
        message = json.loads(entry.decode())
        command = message['command']
    
        if command == "join":
            if address in self.clients:
                self.output_print(f"Client {address} has reconnected")
                jsonData = {'command': 'join_ack', 'message': "Re-connection to the Server is successful!"}
            else:
                self.clients.update({address : None})
                self.output_print(f"Client {address} has connected")
                jsonData = {'command': 'join_ack', 'message': "Connection to the Server is successful!"}
            self.server_socket.sendto(json.dumps(jsonData).encode(), address)
           
        elif command == "leave":
            self.output_print(f"Client {self.clients[address]}:{address} disconnected")
            if self.clients[address] == None:
                message = "Unregistered user disconnected"
            else:
                message = f"User {self.clients[address]} disconnected"
            jsonData = {'command': 'leave', 'message': message}
            self.server_socket.sendto(json.dumps(jsonData).encode(), address)

        elif command == "register":
            handle = message['handle']
            if self.clients[address] != None:
                self.output_print(f"{address} ({self.clients[address]}) Attempted to register again")
                jsonData = {'command': 'error', 'message': "Error: Registration failed. You already have a username."}
            elif handle in self.clients.values():
                self.output_print(f"{address} handle registration failed")
                jsonData = {'command': 'error', 'message': "Error: Registration failed. Handle or alias already exists."}
            else:
                self.clients[address] = handle
                self.output_print(f"Username {handle} registered by {address}")
                jsonData = {'command': 'register', 'given' : 'register' , 'handle' : handle, 'message': f"Welcome {handle}!"}
        
            self.server_socket.sendto(json.dumps(jsonData).encode(), address)
    
        elif command == "store":
            filename = message.get('filename')
            file_data = base64.b64decode(message.get('data'))
            uploader = self.clients.get(address)

            # Create the full path for the file to be stored in SERVER_DIRECTORY
            filepath = os.path.join(SERVER_DIRECTORY, filename)

            try:
                # Ensuring the directory exists; if not, create it
                os.makedirs(SERVER_DIRECTORY, exist_ok=True)
                
                # Open the file at the computed path for writing
                with open(filepath, 'wb') as file:
                    file.write(file_data)

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
                if filename not in self.file_list:
                    self.output_print("New File Detected. Appending to Lists.")
                    self.file_list.append(filename)
                    self.file_data_list.append(file_data)
                    self.timestamp_list.append(timestamp)
                    self.uploader_list.append(uploader)
                    response_message = f"{uploader} <{timestamp}>: Uploaded {filename}"
                    self.output_print(response_message)
                    response = {'command': 'store', 'uploader' : uploader, 'timestamp' : timestamp, 'filename': filename}
                    self.server_socket.sendto(json.dumps(response).encode(), address)
                else:
                    self.output_print("Existing File Detected")
                    response_message = f"Error: File {filename} already exists."
                    self.output_print(response_message)
                    response = {'command': 'error', 'message': response_message}
                    self.server_socket.sendto(json.dumps(response).encode(), address)
            except Exception as e:
                response = json.dumps({'command': 'error', 'message': f"{str(e)}"})
                self.server_socket.sendto(json.dumps(response).encode(), address)

        elif command == "dir":
            try:
                if len(self.file_list) == 0:
                    self.output_print("Error: No files in server.")
                    jsonData = {'command': 'error', 'message': "Error: No files in server."}
                else:
                    jsonData = {'command': 'dir', 'file_list': self.file_list, 'timestamp_list': self.timestamp_list, 'uploader_list': self.uploader_list}
                self.server_socket.sendto(json.dumps(jsonData).encode(), address)
            except Exception as e:
                self.output_print("Error sending response to client: " + e)

        elif command == "get":
            filename = message['filename']
            filepath = os.path.join(SERVER_DIRECTORY, filename)

            try:
                if not os.path.exists(filepath):
                    raise FileNotFoundError(f"File {filename} not found.")

                with open(filepath, 'rb') as file:
                    file_data = file.read()
                    encoded_file_data = base64.b64encode(file_data).decode()
                    response = {"command": "get", "filename": filename, "file_data": encoded_file_data, "message": "File sent successfully."}

                self.server_socket.sendto(json.dumps(response).encode(), address)
                self.output_print("File sent to client successfully.")

            except FileNotFoundError:
                response = {"command": "error", "message": f"Error: File {filename} not found."}
                self.output_print("File Not Found.")
                self.server_socket.sendto(json.dumps(response).encode(), address)
            except Exception as e:
                response = {"command": "error", "message": f"Error: {str(e)}"}
                self.output_print(f"Error: {str(e)}")
                self.server_socket.sendto(json.dumps(response).encode(), address) 
        
        elif command == "broadcast":
            if self.clients[address] == None:
                self.output_print(f"Client {address} Attempted to /broadcast without username")
                jsonData = {'command': 'error', 'message': "Error: You must register a handle first."}
                self.server_socket.sendto(json.dumps(jsonData).encode(), address)
                return
            message = f"{message['message']}"
            self.output_print(f"{address} > {message}")
            message_jsonData = {'command': 'broadcast', 'sender' : f'{self.clients[address]}', 'message': message}
            for client_address, client_handle in self.clients.items():
                if client_handle != None:
                    if client_handle != self.clients[address]:
                        self.server_socket.sendto(json.dumps(message_jsonData).encode(), client_address)
       
        elif command == "unicast":
            handle = message['handle']
            message = message['message']
            sender = self.clients[address]
        
            self.output_print(f"{sender} to {handle} : {message}")
        
            if sender == handle:
                self.output_print(f"Client {address} Attempted to /unicast self")
                jsonData = {'command': 'error', 'message': "Error: You cannot unicast yourself."}
                self.server_socket.sendto(json.dumps(jsonData).encode(), address)
                return
        
            elif handle not in self.clients.values():
                self.output_print(f"Client {address} Attempted to /unicast non-existent handle")
                jsonData = {'command': 'error', 'message': "Error: Handle does not exist."}
                self.server_socket.sendto(json.dumps(jsonData).encode(), address)
                return
        
            for client_address, client_handle in self.clients.items():
            
                if client_handle == handle:
                    message_jsonData = {'command': 'unicast', 'sender' : sender, 'message': message}
                    
                    self.server_socket.sendto(json.dumps(message_jsonData).encode(), client_address)
                    self.output_print(f"Direct Message Sent from {sender} to {handle}")
                    return

    def ping(self):
        for user in self.clients:
            self.output_print(f"Pinging user {user} : ", end="")
            ping_req = {'command': 'ping', 'message' : "Server ping"}
            self.server_socket.sendto(json.dumps(ping_req).encode(), user)
        
            time.sleep(0.3)
            try:
               # self.server_socket.settimeout(5)
                self.server_socket.recvfrom(BUFFER_SIZE)
                self.output_print("Online")
            except Exception as e:
                self.output_print("Offline")
                self.disconnected.append(user)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("File Exchange Server")
    app = Server(root)
    root.mainloop()