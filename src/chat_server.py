import socket
import threading

IP = ""
PORT = 20205

class Room: # 채팅방
    def __init__(self):
        self.client_list = []
        self.server_socket = None

    def ready_to_connect(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((IP, PORT))
        self.server_socket.listen()
        print("Start server..")
    
    def enter_client(self, c):
        self.client_list.append(c)

    def leave_client(self, c):
        self.client_list.remove(c)

    def push_msg_to_room(self, msg):  # 채팅방에 있는 모든 사람한테 메시지 전송
        for c in self.client_list:
            c.send_msg(msg)

    def run(self):
        self.ready_to_connect()

        while True:
            c = ClientManager(self.server_socket.accept(), self)
            self.enter_client(c)

            print("Client :", self.client_list)
            th = threading.Thread(target=c.receive_msg)
            th.start()

class ClientManager: # 클라이언트, 유저 관리자
    def __init__(self, cm_inform, r):
        soc, addr = cm_inform
        self.nickname = None
        self.listen_socket = soc
        self.room = r
        print(f"Enter {addr}")

    def send_msg(self, msg): # 클라이언트로 메시지 전송
        msg = msg.encode(encoding="utf-8")
        self.listen_socket.sendall(msg)

    def receive_msg_check(self): # 메시지 받으면서 연결상태? 체크
        try:
            msg = self.listen_socket.recv(1024).decode()
        except:
            return 0
        
        return msg

    def receive_msg(self): # 계속해서 대기하며 클라이언트로부터 메시지 수신
        self.nickname = self.receive_msg_check()
        print(self.nickname)
        if self.nickname == "/exit": # nickname을 받는데 실패하거나 nickname을 입력전에 클라이언트를 닫아버린 경우
            print("connection fail")
            self.room.leave_client(self)
            print("Client :",self.room.client_list)
            return
        msg = self.nickname + '님이 입장하셨습니다'
        self.room.push_msg_to_room(msg)

        while True:
            msg = self.receive_msg_check()  # 사용자가 전송한 메시지 읽음
            if not msg:
                self.leave()
                break
            elif msg == "/exit": # 종료 메시지이면 종료
                self.leave()
                break
            print(msg, type(msg))
            msg = self.nickname+': '+ msg
            self.room.push_msg_to_room(msg) # 모든 사용자에 메시지 전송

    def leave(self):
        self.room.leave_client(self)
        self.room.push_msg_to_room(self.nickname + '님이 퇴장하셨습니다.')
        self.listen_socket.close()
        print("Current clients :",self.room.client_list)

def server_start():
    chat_room = Room()
    chat_room.run()

if __name__ == "__main__":
    server_start()