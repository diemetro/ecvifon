from app.mod.classes import *
import yaml
import time

def load_config(filename):
    '''
    заргужаем yaml с русским
    '''
    with open(filename, 'r', encoding="utf-8") as stream:
        try:
            config = yaml.load(stream, Loader=yaml.FullLoader)
            return [
                JoinEvent(config['as_one']),
                NumberEvent(config['volves'], config['consonants']),
                ModifyEvent(config['modifications']),
                SameEvent( config['as_same'])
            ]
            # return config
        except yaml.YAMLError as exc:
            print(f'ERROR {exc}')

        return None
    
def config(file, *text):

    PROCESSOR = TextProcessorHandler()
    PROCESSOR = JoinProcessor(PROCESSOR)
    PROCESSOR = NumberProcessor(PROCESSOR)
    PROCESSOR = ModifyProcessor(PROCESSOR)
    PROCESSOR = SameProcessor(PROCESSOR)
    
    for i in load_config(file):
        for t in text:
            PROCESSOR.handle(t, i)
            
import pandas as pd

def imp_csv(file):
    weight = pd.read_csv(file , sep = ',')

    weight.rename(columns={ weight.columns[0]: "0" }, inplace = True)
    weight.index = [i for i in weight["0"]]
    del weight['0']
    return weight

def weight(pattern_letter, text_letter):
    if isinstance(pattern_letter, Letter) and isinstance(text_letter, Letter):
        if pattern_letter.is_volve and text_letter.is_volve:
            if not pattern_letter.technic.isupper() and not text_letter.technic.isupper():
                return 0 #пока так? что с пробелами надо придумать и что с ударениями - и если поставить как 0 -сбивается алгоритм
            elif pattern_letter.technic == text_letter.technic:
                return 0
            else: 
                return 1
        elif pattern_letter.is_consonant and text_letter.is_consonant:
            a = pattern_letter.technic
            b = text_letter.technic
            data = imp_csv('/home/dasha/my_project/eqphone/app/mod/1.csv')
            count =[data[a][b], data[b][a]]
            for i in count:
                if not pd.isna(i):
                    i = i.split(',')
                    i = '.'.join(i)
                    return float(i)
            return 1 #тоже пока
        #elif pattern_letter.is_let and text_letter.is_let:
        else:
            return 1.5 #тут замены согласных на гласные и тд
        #else:
            #return 2.5 #тут не буквы? но пробел считаем за гласную
        
def distance(let1, let2):
#Calculates the Levenshtein distance between let1 and let2
    
    n, m = len(let1), len(let2)

    current_column = range(n+1) # Keep current and previous column, not entire matrix
    for i in range(1, m+1):
        previous_column, current_column = current_column, [i]+[0]*n
        for j in range(1,n+1):
            add, delete, change = previous_column[j]+1, current_column[j-1]+1, previous_column[j-1]
            #добавление или удаление гласной - нарушает структуру слова
            if let1[j-1].is_volve:
                 add += 2
            elif let2[i-1].is_volve:
                 delete += 2
            if let1[j-1].technic != let2[i-1].technic:
                change += weight(let1[j-1], let2[i-1])
           # print(let1[j-1], let2[i-1], add, delete, change)
            current_column[j] = min(add, delete, change)

    return current_column[n]

#алгоритм Нидлмана-Вунша поиска подпоследовательности
def fill_matrix(x, y):
    M = [[0]*(len(y)+1) for _ in range(len(x)+1)]
    for x_cur in range(len(x)):
        for y_cur in range(len(y)):
            if weight(x[x_cur], y[y_cur]) < 2:
                M[x_cur][y_cur] = M[x_cur-1][y_cur-1] + 1
            else:
                M[x_cur][y_cur] = max((M[x_cur][y_cur-1],M[x_cur-1][y_cur]))
    return M

def LCS_DYN(x, y, d):
    M = fill_matrix(x, y)
    LCSx = []
    LCSy = []
    x_cur,y_cur = len(x)-1,len(y)-1
    while x_cur >= 0 and y_cur >= 0:
        if weight(x[x_cur], y[y_cur]) < 1:
            LCSx.append(x[x_cur])
            LCSy.append(y[y_cur])
            if x[x_cur].dist is None or x[x_cur].dist > d or y[y_cur].dist is None or y[y_cur].dist > d:
                x[x_cur].pwr, y[y_cur].pwr = y[y_cur].number, x[x_cur].number
                x[x_cur].dist, y[y_cur].dist = d, d
            x_cur, y_cur = x_cur-1, y_cur-1
        elif M[x_cur-1][y_cur] > M[x_cur][y_cur-1]:
            x_cur -= 1
        else:
            y_cur -= 1
    LCSx.reverse()
    LCSy.reverse()
    return LCSx, LCSy, x, y
  
def union1(text, c):
    res = []
    printed = str()
    n = 0
    l1 = ["<b>", "<u>", "<b><u>", "<i><u>", "<b><u><i>" ]
    l2 = ["</b>", "</u>", "</u></b>", "</u></i>", "</i></u></b>" ]
    for colloc in text:
        for let in range(len(colloc)):
            if colloc[let].number == n:
                for i in range(let, len(colloc)):
                    res.append(colloc[i])
                    if colloc in c:
                        f = (c.index(colloc) + 1)%5
                        printed += l1[f] + colloc[i].origin + l2[f]
                        if i == len(colloc)-1:
                            c[c.index(colloc)] = None
                    else:
                        printed += colloc[i].origin
                break
        n = res[-1].number + 1
    res = Phonotext(res)
    return res, printed
    
# def result(text_one, text_two, c1, c2):
#     text_one = union(text_one)
#     text_two = union(text_two)
#     printed_one = str()
#     printed_two = str()
#     l1 = ["<b>", "<u>", "<b><u>", "<i><u>", "<b><u><i>" ]
#     l2 = ["</b>", "</u>", "</u></b>", "</u></i>", "</i></u></b>" ]
#     f = 0
#     for a, i in enumerate(c1):
        
#     for i in range(len(text_one)):
#         if text_one[i].dist != None:
#             if counter > 1:
#                 f = (f + 1)%5
#             o = l1[f]+ text_one[i].origin + l2[f]
#             t = l1[f]+ text_two[text_one[i].pwr].origin+ l2[f]
#             printed_one += p
            
#             counter = 0
            
#         else:
#             printed += res[i].origin
#             counter += 1
#     return printed

def union(text, collocations):
    #text is Phonotext
    origin = text.get_origin()
    printed = list(origin)
    l1 = ["<b>", "<u>", "<b><u>", "<i><u>", "<b><u><i>"]
    l2 = ["</b>", "</u>", "</u></b>", "</u></i>", "</i></u></b>"]
    f = 0
    for colloc in collocations:
        col = colloc.get_origin()
        for i in range(len(origin)-3):
            if col == origin[i:i+3]:
                smth = col
            elif i+4 <= len(origin) and col == origin[i:i+4]:
                smth = col
            elif i+5 <= len(origin) and col == origin[i:i+5]:
                smth = col
            else:
                continue
            for j in smth:
                printed[i] = l1[f] + printed[i] + l2[f]
                i+=1
            f = (f + 1)%5
    return "".join(printed)



def splitting(text):
    lst = LinkedLiset()
    i  = 0
    if len(text) < 5:
        lst.add(text.basetext)
        i += 1
    while i != len(text):
        if i+4 <= len(text):
            if i == 0 or text[i].is_consonant or not text[i-1].is_let:
                lst.add(text[i:i+5])
                lst.add(text[i:i+4])
#                 lst.add(text[i:i+3])
            i += 1
        else:
            if i + 3<= len(text) and (text[i].is_consonant or not text[i-1].is_let):
                lst.add(text[i::])
                
            i += 1
                
    return lst

def differ(str1, str2):
    
    str1 = Phonotext(str1)
    str2 = Phonotext(str2)
    
    config("/home/dasha/my_project/eqphone/app/mod/russian.yaml", str1, str2)
        
    s1 = splitting(str1)
    s2 = splitting(str2)
    

    print_str = []
    c1 = []
    c2 = []
    for coll1 in s1: #что-то мне подсказывает, что есть способ быстрее
        for coll2 in s2:
            #print(t2[1][1].technik)
            d = distance(coll1, coll2)
            if d <= 2:
                a, b, coll1, coll2 = LCS_DYN(coll1, coll2, d)
                c1.append(coll1)
                c2.append(coll2)
                i1 = ''.join([x.origin for x in coll1])
                i2 = ''.join([x.origin for x in coll2])
                a = ','.join([x.technic for x in a])
                b = ','.join([x.technic for x in b])
                print_str.append(f"Расстояние между {i1} ({a}) и {i2} ({b}) составляет {d} - это похожая часть исходных строк")
    printed1 = union(str1, c1)
    printed2 = union(str2, c2)
    
    return printed1, printed2,  "<br>".join(print_str)

