import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
import sys

IP = "server ip"
PORT = 20205

class MessageManager():# 서버와 연결 및 메시지 송수신 처리 역할
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

    def receive_msg_check(self): # 메시지 받으면서 연결상태? 체크
        try:
            msg = self.client_socket.recv(1024).decode()
        except:
            return 0
        
        print(f"receive msg from server : {msg}")
        return msg

    def disconnect_from_server(self): # 서버와 연결 해제
        self.client_socket.close()

class ClientWindow():
    def __init__(self):
        self.window = None                  # 클라이언트 전체 윈도우
        self.chat_input_box = None          # 채팅 입력 박스
        self.send_button = None             # 전송 버튼
        self.chat_contents_field = None     # 채팅 내용이 보여지는 필드
        self.bold_font = None               # 굵은 글씨 폰트 (닉네임에 사용)
        self.manager = None

    def set_window(self):
        # 전체 윈도우 생성 및 설정
        self.window = tk.Tk()
        self.window.title("hell(o) gint!")
        self.window.geometry("400x400+100+100") # 긴급탈출 넣을거면 400x450으로
        self.window.resizable(False, False) # 창 크기 조절 가능 여부 (상하, 좌우)

        # 기타 위젯 생성 및 설정
        self.chat_contents_field = scrolledtext.ScrolledText(self.window, width = 50, height = 27)
        self.chat_input_box = tk.Entry(self.window, width=40)
        self.send_button = tk.Button(self.window, width=10, text="전송")

        # 위젯 배치
        self.chat_contents_field.place(x=20, y=0)
        self.chat_input_box.place(x=20, y=370)
        self.send_button.place(x=310, y=370)

        # 위젯 - 이벤트 묶기
        self.send_button.bind("<Button-1>", self.press_send_button)              # 전송 버튼을 마우스 좌클릭하면 send_msg 실행하도록 (<Button-1> : 마우스 좌클릭)
        self.chat_input_box.bind("<Return>", self.press_send_button)             # input box에 Enter키가 입력되면 send_msg 실행하도록 (<Return> : Enter 버튼 입력)

        # 초기 메시지
        self.chat_contents_field.insert("insert","닉네임을 입력하세요\n")

        # 창닫기 버튼 누를 시 exit_window 실행
        self.window.protocol("WM_DELETE_WINDOW", self.exit_window)

    def exit_window(self):
        exit_msg = "/exit"
        self.manager.send_msg(exit_msg)
        self.manager.disconnect_from_server()
        self.window.destroy()
        sys.exit(1)

    def press_send_button(self, e): # 입력받은 메시지 서버로 전송 (e는 이벤트에 대한 값이 들어옴)
        # input box에서 메시지 받은 후 input box 초기화
        msg = self.chat_input_box.get()
        if not msg:
            return
        self.chat_input_box.delete(0, tk.END)
        self.chat_input_box.config(text="")

        self.manager.send_msg(msg)

    def run(self):
        self.manager = MessageManager()
        self.manager.connect_to_server()
        self.set_window()

        th = threading.Thread(target=self.chat_stream_to_field)
        th.start()
        
        self.window.mainloop()

    def chat_stream_to_field(self):
        while True:
            msg = self.manager.receive_msg_check()
            if not msg:
                print("disconnected!")
                break
            msg += "\n"

            # chat contents field에 메시지 출력
            self.chat_contents_field.insert("end",msg) # insert vs end
            self.chat_contents_field.see("end")

def client_start():
    client_window = ClientWindow()
    client_window.run()

if __name__ == "__main__":
    client_start()