# staticmethod
class hello:
    num = 10

    @staticmethod
    def calc(x):
        return x + 10


print(hello.calc(10))


# 결과 20


# classmethod
class hello:
    num = 10

    @classmethod
    def calc(cls, x):
        return x + 10


print(hello.calc(10))


# 결과20


# 상속 되잇는 경우라면? 상속 받은 경우가 우선
class hello:
    t = '내가 상속해 줬어'

    @classmethod
    def calc(cls):
        return cls.t


class hello_2(hello):
    t = '나는 상속 받았어'


print(hello_2.calc())
# 결과 내가 상속 받았어
"""상속받은 hello_2 클래스가 t 속성을 업데이트 했다. 
cls.t이 상속시켜준 클래스에 있더라도 이것이 가리키는 것은 상속받은 클래스의 t 속성이다. 
cls는 상속 받은 클래스에서 먼저 찾는다."""
