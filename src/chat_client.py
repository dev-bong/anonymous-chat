import socket

IP = "server ip"
PORT = 20205

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))

while True:
    send_msg = input("input message : ")
    client_socket.send(send_msg.encode(encoding="utf-8"))
    if send_msg == "/exit":
        break

client_socket.close()