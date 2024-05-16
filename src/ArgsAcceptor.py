import argparse
import os


class ArgsAcceptor:
    def __init__(self):
        self.acceptor = argparse.ArgumentParser()
        self.args = None
        self.add_commands()

    def add_commands(self):
        self.acceptor.add_argument("-f", "--fps", action=argparse.BooleanOptionalAction,
                                   help="Параметр отвечает за отображает на экране количество кадров в секунду")
        self.acceptor.add_argument("-v", "--video", default="", type=str, help="Параметр отвечает за входящий "
                                                                               "видеопоток, если указан файл, "
                                                                               "программа будет обрабатывать файл.")
        self.acceptor.add_argument("-b", "--blur", default=5, type=int, help="Параметр отвечает за значение "
                                                                             "медианного размытия")
        self.acceptor.add_argument("-t", "--threshold", default=10, type=int, help="Параметр отвечает за пороговое "
                                                                                   "значение, влияет на точность "
                                                                                   "работы программы")
        self.acceptor.add_argument("-d", "--debug", action=argparse.BooleanOptionalAction,
                                   help="Параметр отвечает за открытие вспомогательного окна, в котором отоборажается "
                                        "работа алгоритма")
        self.args = self.acceptor.parse_args()

    def check_values(self):
        if self.args.video != "" and not os.path.exists(self.args.video):
            print(self.args.video)
            return False, "Такого файла не существует"
        if self.args.blur < 1 and self.args.blur % 2 == 0:
            return False, "Неправильное значение для медианного фильтра"
        if self.args.threshold < 0 or self.args.threshold > 255:
            return False, "Некорректное пороговое значение"
        return True, ""

    def get_args(self):
        return self.args

