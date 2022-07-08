from random import randint

class Game:
    pass


class ChosungQuiz(Game):
    def __init__(self):
        self.answer = ""

    def get_answer(self):
        return self.answer

    def exist_answer(self):  # 문제 존재 여부
        return True if self.answer else False

    def get_chosung(self, text):  # text에서 초성 추출
        """
        코드 출처 : http://smlee729.github.io/python/natural%20language%20processing/2015/12/29/korean-letter-processing-search.html
        """

        CHOSUNG_START_LETTER = 4352
        JAMO_START_LETTER = 44032
        JAMO_END_LETTER = 55203
        JAMO_CYCLE = 588

        def is_hangul(ch):
            return ord(ch) >= JAMO_START_LETTER and ord(ch) <= JAMO_END_LETTER

        result = ""

        for ch in text:
            if ch == " ":
                result += " "
                continue
            if is_hangul(ch):
                result += chr(
                    int(
                        (ord(ch) - JAMO_START_LETTER) / JAMO_CYCLE
                        + CHOSUNG_START_LETTER
                    )
                )

        return result

    def put_chosung_quiz(self, msg):  # 초성퀴즈 정답 등록
        _, answer = msg.split(" ", maxsplit=1)
        chosung = self.get_chosung(answer)
        self.answer = answer.strip(" ")
        print(f"초성퀴즈 등록 : {self.answer}")
        return chosung

    def is_answer(self, msg):  # msg가 정답인지 체크
        return True if msg == self.answer else False

    def initiate_answer(self):  # 정답 초기화
        self.answer = ""


class NumberBaseball(Game):
    def __init__(self):
        self.answer = ""

    def make_random_answer(self): # 중복없는 4자리 난수 생성
        avoid_dupl = []
        while len(self.answer) < 4:
            rand_num = randint(0, 9)
            if rand_num not in avoid_dupl:
                self.answer += str(rand_num)
                avoid_dupl.append(rand_num)
        print(f"숫자야구 정답 생성 : {self.answer}")

    def guess_format_check(self, user_guess):
        checker = [str(i) for i in range(10)]
        if len(user_guess) == 4:
            for num in user_guess:
                if num not in checker:
                    return False
            return True
        else:
            return False

    def guess_answer(self, user_guess): # 유저 추측에 대한 결과. user_guess는 string으로 된 4자리 숫자
        strike = 0
        ball = 0
        out = 0

        for i in range(4):
            if user_guess[i] in self.answer:
                if user_guess[i] == self.answer[i]:
                    strike += 1
                else:
                    ball += 1
            else:
                out += 1

        return (strike, ball, out)
    
    def get_answer(self):
        return self.answer

    def initiate_answer(self):
        print("숫자야구 정답 초기화")
        self.answer = ""
            