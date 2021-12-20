class Letter():
    ''' класс букв'''

    def __init__(self, char, vchar = None):
        self.origin = char if vchar is None else vchar
        self.technic = char
        
        #self.printable = char
        self.is_consonant = False
        self.is_volve = False
        self.is_let = False
        self.syll = 0 # в каком слоге буква
        self.pwr = 0
        self.number = 0 # какой по счету звук в строке
        self.word = 0 # в каком слове буква
        self.dist = None

    def __str__(self):
        return self.origin + '(' + "".join([self.technic]) + ')'

    def __repr__(self):

        return "     '     ".join([
            self.origin,
            str(self.technic),
            'C' if self.is_consonant else '-',
            'V' if self.is_volve else '-',
            "да" if self.is_let else '-',
            str(self.syll),
            str(self.number),
            str(self.word),
            str(self.pwr),
            str(self.dist)
        ])
    
class Phonotext():
    ''' преобразование текста в последовательность объектов класса Letter '''

    def __init__(self, text, visual_text = None):
        if type(text) == str:
            text = [x for x in text.lower()]

        if type(text[0]) == Letter:
            self.basetext = text
        elif visual_text is None:
            self.basetext = [Letter(x) for x in text]
           
        else:
            self.basetext = [Letter(x, y) for x, y in zip(text, visual_text)]

        

    def count_letters(self):
        count_symbols = count_volves = 0
        for symb in self.basetext:
            if symb.is_consonant:
                count_symbols += 1
            if symb.is_volve and symb.technic not in ["--endl",'\n']:
                count_volves += 1
                count_symbols += 1
        return count_volves, count_symbols

    
    def __getitem__(self, item):
        if isinstance(item, slice):
            # Создание нового объекта данного класса с элементами среза внутреннего списка
            return self.__class__(self.basetext[item.start:item.stop:item.step]) #  Phonotext!
            # или return self.__class__(self.__lst[item]))
        else:
            return self.basetext[item]

    def get_origin(self):
        return ''.join([x.origin for x in self.basetext])

    def get_technic(self):
        return ''.join([x.technic for x in self.basetext])

    '''
    def get_printable(self):
        return ''.join([x.printable for x in self.basetext])
    '''
    def __repr__(self):
        return '\n'.join([repr(x) for x in self.basetext])

    def __len__(self):
        return len(self.basetext)

class Node:
    def __init__(self, value, nxt=None):
        self.value = value
        self.nxt = nxt

    def get_value(self):
        return self.value

    def get_next(self):
        return self.nxt

class LinkedLiset:
    def __init__(self):
        self.start = None
        self.length = 0
        self.last = None

    def add(self, value):
        elem = Node(value)
        if self.start is None:
            self.start = elem
            self.last = elem
        else:
            self.last.nxt = elem
            self.last = elem
        self.length += 1

    def __len__(self):
        return self.length
    
    def __getitem__(self, idx):
        if idx >= self.length:
            raise IndexError("Index out of range")
        current = self.start
        for i in range(idx):
            current = current.get_next()
        return current.get_value()

    def __iter__(self):
        self.__curr = self.start
        return self

    def __next__(self):
        if self.__curr is None:
            raise StopIteration()
        val = self.__curr.get_value()
        self.__curr = self.__curr.get_next()
        return val

import abc 

class AbstractEvent(abc.ABC):
    '''
    Abstract event call
    '''
    @abc.abstractmethod
    def __init__(self):
        pass
class TextProcessorHandler():
    def __init__(self, succesor=None):
        self.__succesor = succesor

    def handle(self, obj, conf):
        if self.__succesor is not None:
            return self.__succesor.handle(obj, conf)   

ZERO_SPACE = u'\u200B'

class SameEvent(AbstractEvent):
    # делает словарь одинаковых элементов - правило соотнесения
    def __init__(self, rules):
        self.rules = dict()
        for r in rules:
            for ch in r:
                self.rules[ch] = r[0]

class SameProcessor(TextProcessorHandler):
    def handle(self, obj, conf):
        if isinstance(conf, SameEvent):
            #если заданы правила определения одинаковых букв
            for i in range(len(obj.basetext)):
                #basetext - список букв
                if obj.basetext[i].is_consonant and obj.basetext[i].origin in conf.rules.keys():
                    if (i+1 == len(obj.basetext) or (not obj.basetext[i+1].is_let)):
                        obj.basetext[i].technic = conf.rules.get(obj.basetext[i].technic, ZERO_SPACE)
                    elif obj.basetext[i+1].is_consonant and obj.basetext[i+1].origin in conf.rules.values():
                         obj.basetext[i].technic = conf.rules.get(obj.basetext[i].technic, ZERO_SPACE)
                        
                elif not obj.basetext[i].is_let:
                    obj.basetext[i].technic = conf.rules.get(obj.basetext[i].technic, ZERO_SPACE)
                #если нет ключа - возвращет ZERO_SPASE, если есть - в техническом похожая буква

        else:
            super().handle(obj, conf) #????

class NumberEvent(AbstractEvent):
    def __init__(self, volves, consonants):
        #задает правило согласных и гласных, а также все что буква
        self.volves = set(volves)
        self.consonants = set(consonants)
        self.words = self.volves.union(self.consonants)

class NumberProcessor(TextProcessorHandler):
    def handle(self, obj, conf):
        if isinstance(conf, NumberEvent):
            i = 0 #позиция буквы в тексте
            j = 1 #какой слог
            k = 1 #какое слово
            num = 1 #какая буква в слове
            space = False
            # print(conf.volves, conf.consonants)

            for l_number in range(len(obj.basetext)):
                #для каждой буквы - задается класс
                letter = obj.basetext[l_number]
                letter.number = i #какая буква по порядку в тексте 
                letter.word = k  #какое слово
                letter.w_pos = [num, 0] #позиция буквы в слове ?
                # print(' ', letter.technic, letter.printable, sep='', end='')
                if letter.technic in " |\n": #если что-то по аналогу пробела
                    if not space:
                        #добавляем новое слово
                        k += 1
                        if num < 3: # если предыдущее меньше 3 - по сути из одной буквы
                            while num > 1: #  по сути из одной буквы
                                num -= 1
                                #предыдущей задается [0, 0]
                                obj.basetext[l_number - num].w_pos = [0, 0]
                                num -= 1
                        while num > 1:
                            num -= 1
                            obj.basetext[l_number - num].w_pos[1] = -num #[x, -x+1] [позиция от начала слова, от конца слова]
                            num -= 1

                    space = True # это пробел
                
                else:
                    space = space and letter.technic not in conf.words #??????????
                        
                if letter.technic == "\n":
                    stopper = obj.basetext[l_number - 1].syll - 3 # в каком слоге предыдущая буква - 3
                    tmp = 1
                    while obj.basetext[l_number - tmp].syll > stopper and obj.basetext[l_number - tmp].technic != "\n":
                        #пока не пройдем на 3 слога назад и не найдем еще один перенос строки
                        obj.basetext[l_number - tmp].p_end = 1 #у этой буквы позиция конца рядом?
                        tmp += 1
                if letter.technic in conf.volves:
                    # print(0, end='')
                    letter.is_volve = True #задаем атрибут 
                    letter.is_let = True
                    letter.syll = j
                    j += 1 #еще одна гласная буква в слове - еще один слог
                elif letter.technic in conf.consonants:
                    
                    # print(1, end='')
                    letter.is_consonant = True
                    letter.is_let = True
                    letter.syll = j #эта буква в таком-то слоге
                else:
                    letter.syll = 0
                    j += 1
                i += 1 #еще одна буква в тексте
                num += 1 #еще одна буква в слове
            # print()
        else:
            super().handle(obj, conf) #???

from collections import defaultdict

class JoinEvent(AbstractEvent):
    def __init__(self, rules):
        self.rules = defaultdict(dict)
        for a in rules:
            self.rules[a[1]] = a[0]


class JoinProcessor(TextProcessorHandler):
    def handle(self, obj, conf):
        if isinstance(conf, JoinEvent):
            i = 1
            while i < len(obj.basetext): #проверяем предыдущую и эту в правилах
                tmp_a = obj.basetext[i - 1].origin
                tmp_b = obj.basetext[i].origin
                if tmp_a + tmp_b in conf.rules.keys() or tmp_b == u"\u0301":
                    obj.basetext[i - 1].origin = tmp_a + tmp_b
                    #obj.basetext[i - 1].printable = tmp_a + tmp_b
                    
                    obj.basetext[i - 1].technic = conf.rules[tmp_a + tmp_b]
                    obj.basetext.pop(i)
                    i -= 1
                i += 1
        else:
            super().handle(obj, conf)

class ModifyEvent(AbstractEvent):
    def __init__(self, rules):
        self.rules = defaultdict(dict)
        for a in rules:
            self.rules[a[0]][a[1]] = rules[a]


class ModifyProcessor(TextProcessorHandler):
    def handle(self, obj, conf):
        if isinstance(conf, ModifyEvent):
            i = 1
            while i < len(obj.basetext):
                tmp_a = obj.basetext[i - 1].origin
                tmp_b = obj.basetext[i].origin
                if tmp_a in conf.rules:
                    if tmp_b in conf.rules[tmp_a]:
                        tmp_c = conf.rules[tmp_a][tmp_b]
                        obj.basetext.insert(i, Letter(ZERO_SPACE))
                        obj.basetext[i - 1].technic = tmp_c[0]
                        obj.basetext[i + 0].technic = tmp_c[1]
                        obj.basetext[i + 1].technic = tmp_c[2]
                i += 1
        else:
            super().handle(obj, conf)

