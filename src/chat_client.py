import socket
import threading
import time

IP = "server ip"
PORT = 20205

class MessageManager():
    # 서버와 연결 및 메시지 송수신 처리 역할

    def __init__(self):
        self.client_socket = None
        self.con_state = 1

    def connect_to_server(self): # 서버에 연결
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((IP, PORT))

    def send_msg(self, msg): # 서버로 메시지 전송
        print(f"send msg to server : {msg}")
        msg = msg.encode(encoding="utf-8")
        self.client_socket.sendall(msg)

    def receive_msg(self): # 계속해서 대기하며 서버로부터 메시지 수신
        while True:
            try:
                msg = self.client_socket.recv(1024)
            except:
                self.con_state = 0 # 메시지 제대로 못받았을 경우 (연결상태 이상) 종료
            if not self.con_state:
                print("disconnected!")
                break
            msg = msg.decode()
            print(f"receive msg from server : {msg}")

    def receive_msg_in_thread(self): # 메시지 대기 및 수신을 스레드에서 진행
        th = threading.Thread(target=self.receive_msg)
        th.start()

    def disconnect_from_server(self): # 서버와 연결 해제
        self.client_socket.close()

chat_client = MessageManager()
chat_client.connect_to_server()

chat_client.receive_msg_in_thread() # 스레드를 이용해서 메시지 송수신을 동시에 진행할 수 있도록함

while True:
    time.sleep(1) # 서버로 부터 수신하는 메시지 출력과 "input message : " 출력의 순서를 맞추기 위해 1초 간격 둠
    msg = input("input message : ")
    chat_client.send_msg(msg)
    if msg == "/exit":
        break

chat_client.disconnect_from_server()