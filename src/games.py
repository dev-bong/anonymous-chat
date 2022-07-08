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
