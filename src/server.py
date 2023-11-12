import socket

HOST = "127.0.0.1"
PORT = 12345

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    print("Waiting for connection...")
    s.listen()
    conn, addr = s.accept()
    # while True:
    #     conn, addr = s.accept()
    #     data = conn.recv(1024)
    #     while data:
    #         print(data)
    #         data = conn.recv(1024)
    #     print("All data")
    #     conn.close()
    #     break