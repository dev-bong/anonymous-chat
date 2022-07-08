import socket
import threading
import games

IP = ""
PORT = 20205


class Room:  # 채팅방
    def __init__(self):
        self.client_list = []
        self.server_socket = None
        self.usable_colors = [1, 2, 3, 4, 5, 6]  # 사용 가능한 색상코드들
        self.colors_in_use = []  # 사용중인 색상코드들
        self.chosung_game = games.ChosungQuiz()
        self.number_baseball = games.NumberBaseball()

    def ready_to_connect(self):  # 서버 소켓 생성 및 bind, listen
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((IP, PORT))
        self.server_socket.listen()
        print("Start server..")

    def enter_client(self, c):  # 클라이언트 입장
        self.client_list.append(c)

    def leave_client(self, c):  # 클라이언트 퇴장
        self.client_list.remove(c)

    def push_msg_to_room(self, msg):  # 채팅방에 있는 모든 사람한테 메시지 전송
        for c in self.client_list:
            c.send_msg(msg)

    def give_color(self, nickname):  # 닉네임에 색상코드 부여
        color = self.usable_colors.pop(0)
        self.colors_in_use.append(color)
        return str(color) + "|" + nickname  # bong -> 2|bong 이런식으로.. | 앞에 숫자가 색상코드

    def take_color(self, nickname):  # 닉네임 색상코드 반환
        color = int(nickname.split("|")[0])
        self.colors_in_use.remove(color)
        self.usable_colors.append(color)

    def run(self):  # 채팅 서버 실행
        self.ready_to_connect()

        while True:
            c = ClientManager(self.server_socket.accept(), self)
            self.enter_client(c)

            print("Client :", self.client_list)
            th = threading.Thread(target=c.receive_msg)
            th.start()


class ClientManager:  # 클라이언트, 유저 관리자
    def __init__(self, cm_inform, r):
        soc, addr = cm_inform
        self.nickname = None
        self.listen_socket = soc
        self.room = r
        print(f"Enter {addr}")

    def send_msg(self, msg):  # 클라이언트로 메시지 전송
        msg = msg.encode(encoding="utf-8")
        self.listen_socket.sendall(msg)

    def receive_msg_check(self):  # 메시지 받으면서 연결상태? 체크
        try:
            msg = self.listen_socket.recv(1024).decode()
        except:
            return 0

        return msg

    def receive_msg(self):  # 계속해서 대기하며 클라이언트로부터 메시지 수신
        self.nickname = self.receive_msg_check()
        print(self.nickname)
        if (
            self.nickname == "/exit"
        ):  # nickname을 받는데 실패하거나 nickname을 입력전에 클라이언트를 닫아버린 경우
            print("connection fail")
            self.room.leave_client(self)
            print("Client :", self.room.client_list)
            return
        msg = self.nickname + "님이 입장하셨습니다"
        only_nickname = self.nickname
        self.room.push_msg_to_room(msg)

        self.nickname = self.room.give_color(self.nickname)  # 닉네임에 색상코드 부여

        while True:
            msg = self.receive_msg_check()  # 사용자가 전송한 메시지 읽음
            if not msg:
                self.leave()
                break
            elif msg == "/exit":  # 종료 메시지이면 종료
                self.leave()
                break

            if self.process_cmd(msg, only_nickname):
                continue

            print(msg, type(msg))
            msg = self.nickname + ": " + msg
            self.room.push_msg_to_room(msg)  # 모든 사용자에 메시지 전송

    def leave(self):  # 퇴장
        self.room.leave_client(self)
        self.room.take_color(self.nickname)  # 퇴장 시 색상코드 반환
        self.room.push_msg_to_room(self.nickname + "님이 퇴장하셨습니다.")
        self.listen_socket.close()
        print("Current clients :", self.room.client_list)

    def process_cmd(self, msg, nick_name):

        if msg == "/도움":
            help_text = """
            명령어 사용법
            \"/\" + \"명령어\" 조합으로 사용

            명령어 리스트
            /도움
                - 도움말 출력
            /문제 + [한글 텍스트]
                - 초성퀴즈 문제 등록
                - 한글과 띄어쓰기만 가능
                - 덮어쓰기 가능
            /야구시작
                - 숫자야구 시작
                - 중복없는 4자리 난수 생성
                - 숫자는 0 ~ 9
                - 덮어쓰기 불가
            /야구 + [숫자]
                - 숫자야구 정답 추측
                - 4자리 숫자 입력
                - 1S 2B 1O 형식 리턴
            """
            self.send_msg(help_text)
            return True

        ##### 초성퀴즈 #####
        if msg.startswith("/문제 "):  # 초성퀴즈 문제 등록
            msg = (
                "초성퀴즈 문제 : "
                + self.room.chosung_game.put_chosung_quiz(msg)
                + f"(출제 : {nick_name})"
            )
            self.room.push_msg_to_room(msg)
            return True
        elif self.room.chosung_game.exist_answer() and self.room.chosung_game.is_answer(
            msg
        ):  # 초성퀴즈 정답 맞춘 경우
            ans = self.room.chosung_game.get_answer()
            msg = f"{nick_name} 초성퀴즈 우승! (정답 : {ans})"
            print("초성퀴즈 정답! 초성퀴즈 초기화")
            self.room.push_msg_to_room(msg)
            self.room.chosung_game.initiate_answer()
            return True

        ##### 숫자야구 #####
        if msg == "/야구시작":  # 숫자야구 정답 생성
            if not self.room.number_baseball.get_answer():
                self.room.number_baseball.make_random_answer()
                msg = "숫자야구 시작!"
                self.room.push_msg_to_room(msg)
            else:
                msg = "이미 진행중인 숫자야구 게임이 있습니다"
                self.send_msg(msg)
            return True

        if msg.startswith("/야구 "):  # 숫자야구 정답 추측
            if not self.room.number_baseball.get_answer():
                msg = "진행중인 숫자야구 게임이 없습니다"
                self.send_msg(msg)
                return True
            else:
                _, guess_num = msg.split(" ", maxsplit=1)
                print(f"숫자야구 추측 : {guess_num}")
                if self.room.number_baseball.guess_format_check(
                    guess_num
                ):  # 포맷 검사 (4자리 숫자인지)
                    guess_res = self.room.number_baseball.guess_answer(guess_num)

                    if guess_res == (4, 0, 0):  # 정답인 경우
                        msg = f"{nick_name} 숫자야구 우승! (정답 : {guess_num})"
                        self.room.number_baseball.initiate_answer()  # 정답 맞추면 초기화
                        self.room.push_msg_to_room(msg)
                    else:
                        strike, ball, out = guess_res
                        msg = f"{guess_num} -> {strike}S {ball}B {out}O ({nick_name})"
                        self.room.push_msg_to_room(msg)
                    return True
                else:
                    msg = "올바른 포맷이 아닙니다. 4자리 숫자를 입력해주세요"
                    self.send_msg(msg)
                    return True

        return False


def server_start():
    chat_room = Room()
    chat_room.run()


if __name__ == "__main__":
    server_start()
