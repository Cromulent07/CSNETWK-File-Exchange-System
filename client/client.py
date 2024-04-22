import socket
import threading
import json
import time
import os
import base64
import tkinter as tk
from tkinter import scrolledtext

BUFFER_SIZE = 1024

class Client:
    def __init__(self, root):
        self.root = root
        self.isConnected = False
        self.join_success = False
        self.server_address = None
        self.params = None
        self.current_handle = None
        self.interface()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.start_network_thread()
        self.isRegistered = False
        self.join_event = threading.Event()

    def interface(self):
        self.chat_box = scrolledtext.ScrolledText(root, wrap=tk.WORD)
        self.command = tk.Entry(root, width=50)
        self.button = tk.Button(root, text="Send Command", command=self.send_command)

        self.chat_box.grid(row=0, column=0, sticky="nsew")
        self.command.grid(row=1, column=0, sticky="ew")
        self.button.grid(row=2, column=0, sticky="ew")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.output_print("Enter a command. Type /? for help")
    
    def output_print(self, message, end='\n'):
        self.chat_box.insert(tk.END, message + '\n')
        self.chat_box.see(tk.END)

    def send_command(self):
        entry = self.command.get()
        self.output_print(f">> {entry}")
        self.toServer(entry)
        self.command.delete(0, tk.END)

    def toServer(self, entry):
        if not entry.startswith('/'):
            self.output_print("Error: That is not a command! Type /? for help.")
            return
    
        input_line = entry.split()
        command = input_line[0]
        params = input_line[1:]
    
        if command == "/join":
            if self.isConnected:
                self.output_print("Error: User is already connected to the server.")
            elif len(params) != 2:
                self.output_print("Invalid command syntax!")
                self.output_print("Usage: /join <server_ip_add> <port>")
            else:
                try:
                    socket.gethostbyname(params[0])
                    self.server_address = (params[0], int(params[1]))
                    self.client_socket.sendto(json.dumps({"command": "join"}).encode(), self.server_address)
                    self.join_success = False
                    self.join_event.clear()
                    threading.Thread(target=self.buffer_join, daemon=True).start()
                    if not self.join_event.wait(timeout=20):
                        if not self.join_success and not self.isConnected:
                            self.output_print("Error: Connection to the Server has failed! Please check IP Address and Port Number.")
                            self.server_address = None
                except Exception as e:
                    self.output_print(f"Error: {str(e)}")
                    self.server_address = None
                    return

        elif command == "/leave":
            if self.isConnected:
                if len(params) > 0:
                    self.output_print("Error: There should be no parameters for leave.")
                    self.output_print("Usage: /leave")
                else:
                    self.client_socket.sendto(json.dumps({"command": "leave"}).encode(), self.server_address)
                    time.sleep(0.1)
            else:
                self.output_print("Error: Disconnection failed. Please connect to the server first.")
        elif command == "/register":
            if self.isConnected and self.isRegistered:
                self.output_print("Error: You are already registered.")
                return
            elif self.isConnected:
                if len(params) != 1:
                    self.output_print("Error: Command parameters do not match or is not allowed.")
                    self.output_print("Usage: /register <handle>")
                else:
                    self.client_socket.sendto(json.dumps({"command": "register", "handle": params[0]}).encode(), self.server_address)
                    time.sleep(0.1)
            else:
                self.output_print("Error: Please connect to the server first.")
        elif command == "/store":
            if self.isConnected:
                if len(params) < 1:
                    self.output_print("Error: Invalid command syntax!")
                    self.output_print("Usage: /store <filename>")
                
                elif self.current_handle == None:
                    self.output_print("Error: Please register a handle first.")
                else:
                    filename = params[0]
                    try:
                        with open(filename, 'rb') as file:
                            file_data = file.read()
                            encoded_file_data = base64.b64encode(file_data).decode()
                            self.client_socket.sendto(json.dumps({"command": "store", "filename": filename, "data": encoded_file_data}).encode(), self.server_address)
                            time.sleep(0.1)
                    except FileNotFoundError:
                        self.output_print(f"Error: File not found.")
                    except Exception as e:
                        self.output_print(f"Error: {str(e)}")
            else:
                self.output_print("Error: Please connect to the server first.")
        
        elif command == "/dir":
            if self.isConnected:
                if len(params) > 0:
                    self.output_print("Error: There should be no parameters for dir.")
                    self.output_print("Usage: /dir")
                elif self.current_handle == None:
                    self.output_print("Error: Please register a handle first.")
                else:
                    try:
                        self.client_socket.sendto(json.dumps({"command": "dir"}).encode(), self.server_address)
                        time.sleep(0.1)
                    except Exception as e:
                        self.output_print("Error sending data:", e)
            else:
                self.output_print("Error: Please connect to the server first.")

        elif command == "/get":
            if self.isConnected:
                if len(params) < 1:
                    self.output_print("Error: Invalid command syntax!")
                    self.output_print("Usage: /get <filename>")
                elif self.current_handle == None:
                    self.output_print("Error: Please register a handle first.")
                else:
                    filename = params[0]
                    self.client_socket.sendto(json.dumps({"command": "get", "filename": filename}).encode(), self.server_address)
                    time.sleep(0.1)
            else:
                self.output_print("Error: Please connect to the server first.")
            
        elif command == "/broadcast":
            if self.isConnected:
                if len(params) == 0:
                    self.output_print("Error: Command parameters do not match or is not allowed.")
                    self.output_print("Usage: /broadcast <message>")
                elif self.current_handle == None:
                    self.output_print("Error: Please register a handle first.")
                else:
                    message = ' '.join(params)
                    self.client_socket.sendto(json.dumps({"command" : "broadcast", "message" : message}).encode(), self.server_address)
            else:
                self.output_print('Error. Please connect to the server first.')
    
        elif command == "/unicast":
            if self.isConnected:
                if len(params) < 2:
                    self.output_print("Error: Command parameters do not match or is not allowed.")
                    self.output_print("Usage: /unicast <handle> <message>")
                elif self.current_handle == None:
                    self.output_print("Error: Please register a handle first.")
                else:
                    handle = params[0]
                    message = ' '.join(params[1:])
                    self.client_socket.sendto(json.dumps({"command" : "unicast", "handle" : handle, "message" : message}).encode(), self.server_address)
            else:
                self.output_print('Error. Please connect to the server first.')
         
        elif command == "/cls":
            if os.name == "nt":  
                os.system('cls') 
            else:
                os.system('clear')  

            if self.current_handle == None:
                self.output_print("File Exchange Client")
            else:
                self.output_print(f"File Exchange Client - {self.current_handle}")
            self.output_print("Enter a command. Type /? for help")


        elif command == "/?":
            self.output_print("Connect to the server application:               /join <server_ip_add> <port>")
            self.output_print("Disconnect to the server application:            /leave")
            self.output_print("Register a unique handle or alias:               /register <handle>")
            self.output_print("Send file to server:                             /store <filename>")
            self.output_print("Request directory file list from server:         /dir")
            self.output_print("Fetch a file from a server:                      /get <filename>")
            self.output_print("Send a message to all registered Handles:        /broadcast <message>")
            self.output_print("Send a direct message to one Handle:             /unicast <handle> <message>")
            self.output_print("Request command help:                            /?")
            self.output_print("Clear Screen:                                    /cls")
        else:
            self.output_print("Command not found. Type /? for help.")

    def fromServer(self, data):
        if not(isinstance(data, str)):
            command = data['command']

            if 'message' in data:
                message = data['message']
        
            if command == "ping":
                ping_ack = {'command': 'ping'}
                self.client_socket.sendto(json.dumps(ping_ack).encode(), self.server_address)
                return
        
            elif command == "join":
                message = data['message']
                self.output_print(f"{message}")
            
            elif command == "leave":
                self.output_print("Connection closed. Thank you!")
                self.isConnected = False
                self.server_address = None
        
            elif command == "register":
                self.current_handle = data['handle']
                self.output_print(f"Handle Registration Successful! Your Handle is now {self.current_handle}.")
                self.isRegistered = True
        
            elif command == "store":
                filename = data['filename']
                self.output_print(f"File {filename} sent to server.")
        
            elif command == "dir":
                if data['command'] == 'dir':
                    self.output_print("File Server Directory:")
                    file_list = data['file_list']
                    timestamp_list = data['timestamp_list']
                    uploader_list = data['uploader_list']
                    for i in range(len(file_list)):
                        curr_filename = file_list[i]
                        curr_timestamp = timestamp_list[i]
                        curr_uploader = uploader_list[i]
                        self.output_print(f"{curr_filename} <{curr_timestamp}> : {curr_uploader}")
                return

            elif command == "get":
                filename = data['filename']
                file_data = base64.b64decode(data['file_data'])
                try:
                    with open(filename, 'wb') as file:
                        file.write(file_data)
                    self.output_print(f"File received from server: {filename}")
                except Exception as e:
                    self.output_print(f"Error: {str(e)}")
                
            elif command == "broadcast":
                sender = data['sender']
                message = f"[From {sender} to all]: {message}"
                self.output_print(f"{message}\n> ", end = "")
        
            elif command == "unicast":
                sender = data['sender']
                message = f"[From {sender} to you]: {message}"
                self.output_print(f"{message}\n> ", end = "")
            
            elif command == 'error':
                if 'message' in data:
                    self.output_print(f"{message}")

    def receive(self):
        while True:
            if self.isConnected:
                try:   
                    response = self.client_socket.recvfrom(BUFFER_SIZE)
                    response_str = response[0].decode()
                    try:
                        data = json.loads(response_str)
                    except json.JSONDecodeError:
                        data = response_str

                    self.fromServer(data)

                except ConnectionResetError:
                    self.output_print("Error: Connection to the Server has been lost!")
                    self.isConnected = False
                except Exception as e:
                    self.output_print(f"Error: {str(e)}")
                
    
    def buffer_join(self):
        try:
            #  self.client_socket.settimeout(5)
            response = self.client_socket.recvfrom(BUFFER_SIZE)
            data = json.loads(response[0].decode())
            if data["command"] == "join_ack":
                self.isConnected = True
                self.join_success = True
                self.output_print("Successfully connected to the server.")
                self.join_event.set()
                #  self.client_socket.settimeout(5)
            else:
                raise Exception("Did not receive 'join_ack' from server.")
                
        except socket.timeout:
            self.output_print("Error: Server is offline or not responding.")
            self.server_address = None

        except ConnectionResetError:
            self.output_print("Error: Connection to the Server has failed! Please check IP Address and Port Number.")
            self.server_address = None

        except Exception as e:
            self.output_print(f"Error: {str(e)}")
            self.server_address = None
    

    def start_network_thread(self):
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.daemon = True
        receive_thread.start() 

if __name__ == "__main__":
    root = tk.Tk()
    root.title("File Exchange Client")
    app = Client(root)
    app.start_network_thread()
    root.mainloop()