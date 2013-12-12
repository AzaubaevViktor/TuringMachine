#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import argparse

__author__ = 'ktulhy'
__version__ = "0.1b"
__supportedStructureVersion__ = [1]


def __getNumBySymbol(sym):
    if 'R' == sym:
        return 1
    elif 'L' == sym:
        return -1
    return 0

def getCodeByStr(str):
    """ Разбирает строку формата q123 1 -> q321 0 R
    """
    code = []
    lexemes = [lex for lex in str.split(" ") if (lex != "")]
    code.append(int(lexemes[0][1:]))
    code.append((1 == int(lexemes[1])))
    code.append(int(lexemes[3][1:]))
    code.append((1 == int(lexemes[4])))
    if 5 == len(lexemes):
        code.append(0)
    else:
        code.append(__getNumBySymbol(lexemes[5][0]))
    return code


class HeadError(Exception):
    def __init__(self):
        print("Ошибка -- лента -- луч!")


def getSymByNum(num):
    if -1 == num:
        return 'L'
    elif 0 == num:
        return ''
    elif 1 == num:
        return 'R'


def printMem(mem, head, scatter, state):
    start = max(0, head - scatter)
    end = min(head + scatter, len(mem))
    s = "[" + str(start) + "]"
    for m in mem[start:end]:
        if m:
            s += '1'
        else:
            s += '0'
    s += "[" + str(end) + "]"
    print(s)
    print(" " * (head - start + (len(str(start)) + 2)) + "|" + str(state))


class TuringMachine():
    def __init__(self, programm, args):
        self.mem = [False for x in range(sum(args) + len(args)*2 + 1)]
        head = 1
        for arg in args:
            for i in range(arg+1):
                self.mem[head] = True
                head += 1
            head += 1
        self.maxMem = head
        self.head = 0
        self.state = 1
        self.programm = programm

    def __addMem__(self):
        if self.head == self.maxMem:
            self.mem += [False for x in range(1024)]
            self.maxMem += 1024

    def step(self):
        for code in self.programm:
            if (self.state == code[0]) and (self.mem[self.head] == code[1]):
                self.state = code[2]
                self.mem[self.head] = code[3]
                self.head += code[4]
                self.__addMem__()
                if self.head < 0:
                    raise HeadError
                return code

    def getAnswer(self):
        ans = 0
        head = self.head
        if 0 == self.mem[head]:
            head += 1
            while 1 == self.mem[head]:
                ans += 1
                head += 1
            ans -= 1
            return ans
        return -1


parser = argparse.ArgumentParser(add_help=True, description="Turing Machine")
parser.add_argument("-f", "--filename", type=str, help="Имя файла с программой")
parser.add_argument("-q", "--quiet", action="store_true", help="Вывод без отладочной информации")
args = parser.parse_args()
quietMode = args.quiet
print(quietMode)
filename = args.filename

if (None == filename):
    print("Введите имя файла (без расширения):", end='')
    filename = input()
filename += ".mt"
try:
    f = open(filename,"rt")
except FileNotFoundError:
    print("Не удалось открыть файл '%s' :(" % filename)
    exit()
print("Открыт файл '%s'" % filename)

if int(f.readline()) not in __supportedStructureVersion__:
    print("Несовместимая версия файла")
    exit()

kSteps = int(f.readline())
print("Поставлено ограничение в %d шагов" % kSteps)

codes = []
for line in f.readlines():
    if '#' != line[0]:
        codes.append(getCodeByStr(line))

f.close()

print("Введите аргументы через запятую: ",end="")
args = [int(num) for num in input().split(",")]

tm = TuringMachine(codes,args)

kStep = 0
while 0 != tm.state:
    if not quietMode:
        print("================================")

    kStep += 1
    if kStep > kSteps:
        print("Достигнуто максимальное количество шагов")
        break

    if not quietMode:
        printMem(tm.mem, tm.head, 20, tm.state)

    code = tm.step()

    if None != code:
        if not quietMode:
            print("Code: q%d %d -> q%d %d %s" % (code[0], code[1], code[2], code[3], getSymByNum(code[4])))
    else:
        print("Не найдена команда, программа завершилась некорректно.")
        break

if (0 == tm.state):
    if not quietMode:
        printMem(tm.mem, tm.head, 20, tm.state)
    print("================================")
    print("Программа завершила свою работу. Выполнено %d инструкций" % kStep)
    print("Ответ: %d" % tm.getAnswer())