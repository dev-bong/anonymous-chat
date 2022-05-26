import socket

IP = ""
PORT = 20205

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP, PORT))
server_socket.listen()

listen_socket, addr = server_socket.accept()
print(listen_socket, addr)

while True:
    msg = listen_socket.recv(1024).decode()
    print(f"message : {msg}")
    if msg == "/exit":
        break
    listen_socket.sendall(msg.encode(encoding='utf-8'))

listen_socket.close()
server_socket.close()

print("chat server shutdown")