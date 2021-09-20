import datetime


def datetime_decorator(func):
    def decorated():
        print(datetime.datetime.now())

        func()

        print(datetime.datetime.now())

    return decorated


@datetime_decorator
def main_function_1():
    print("MAIN FUNCTION 1 START")


main_function_1()