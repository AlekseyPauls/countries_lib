# -*- coding: utf-8 -*-
import shelve
import difflib
from os import path
import csv


DB_PATH = path.join(path.split(path.abspath(__file__))[0], 'database', 'countries_db')


def match_country_name(key, value, priority=2):
    """ Добавление страны. Аргументы: key - вариант названия страны (строка), value - общее название страны (строка),
    priority (целое число, 1 или 2) - приоритет варианта при нормализации ('1' - высокий
    (название страны, перевод, сокращение), '2' - низкий (столица, регион, и т.д.) """

    if type(key) is str and type(value) is str and type(priority) is int and (priority == 1 or priority == 2):
        try:
            with shelve.open(DB_PATH, 'w') as countries_db:
                countries_db[key.lower()] = str(priority) + value
            return None
        # Здесь и далее. На всякий случай перехватывается Exception. Не смотря на то,
        # что ошибка здесь может быть только в отсутствии корректной базы данных
        except Exception:
            return 'DatabaseError'
    else:
        return 'Invalid arguments'


def del_country_name(key):
    """ Удаление варианта названия страны. Аргумент: key - удаляемый вариант названия страны. 
    Возращаемое значение: нет """

    if type(key) is str:
        try:
            with shelve.open(DB_PATH, 'w') as countries_db:
                if key.lower() in countries_db.keys():
                    del countries_db[key.lower()]
            return None
        except Exception:
            return 'DatabaseError'
    else:
        return 'Invalid arguments'


def normalize_country_name(posname, dif_acc=0.7):
    """ Приведение названия страны к общепринятому виду. Аргументы: posname (possible name) - нормализуемое название 
    (строка), dif_acc - параметр точности (вещественное число от 0 до 1, по умолчанию 0.7). 
    Возвращаемое значение: общее название страны (строка), если не найдено - 'None' (строка) """

    if type(posname) is not str or type(dif_acc) is not float or dif_acc <= 0.0 or dif_acc >= 1.0 or posname == "":
        return 'Invalid arguments'
    try:
        with shelve.open(DB_PATH, 'w') as countries_db:
            posname = posname.lower()
            # Очищаем входную строку от знаков препинания (кроме пробелов) и цифр.
            # Данный способ безопаснее, чем регулярные выражения и применение некоторых стандартных функций,
            # всвязи с национальными символами в названиях стран. Если пользователь умудрится использовать
            # иные символы, то он либо опечатался, либо издевается. Опечатки исправляются далее.
            symbols = [',', '.', '/', '!', '?', '<', '>', '[', ']', '|', '(', ')', '+', '=', '_', '*', '&', '%',
                       ';', '№', '~', '@', '#', '$', '{', '}', '-', '`', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            for symb in symbols:
                posname = posname.replace(symb, ' ')
            if posname == "":
                return 'Invalid arguments'

            # Сначала ищем совпадение всей строки и значения с приоритетом '1'
            # Проверка на длину - чтобы исключить варианты, когда совпало только начало или другая часть строки
            posname_tmp = difflib.get_close_matches(posname, countries_db.keys(), n=1, cutoff=dif_acc)
            if posname_tmp != [] and countries_db[posname_tmp[0]][0] == '1' and \
                    abs(len(posname) - len(posname_tmp[0])) <= 1:
                return countries_db[posname_tmp[0]][1:]
            # Ищем совпадение всей строки и значения с приоритетом '2'
            posname_tmp = difflib.get_close_matches(posname, countries_db.keys(), n=1, cutoff=dif_acc)
            if posname_tmp != [] and countries_db[posname_tmp[0]][0] == '2' and \
                    abs(len(posname) - len(posname_tmp[0])) <= 1:
                return countries_db[posname_tmp[0]][1:]
            # Ищем совпадение всей строки без пробелов и значения с приоритетом '1'
            posname_tmp = posname.replace(' ', '')
            posname_tmp = difflib.get_close_matches(posname_tmp, countries_db.keys(), n=1, cutoff=dif_acc)
            if posname_tmp != [] and countries_db[posname_tmp[0]][0] == '1' and \
                    abs(len(posname.replace(' ', '')) - len(posname_tmp[0].replace(' ', ''))) <= 1:
                return countries_db[posname_tmp[0]][1:]
            # Ищем совпадение всей строки без пробелов и значения с приоритетом '2'
            posname_tmp = posname.replace(' ', '')
            posname_tmp = difflib.get_close_matches(posname_tmp, countries_db.keys(), n=1, cutoff=dif_acc)
            if posname_tmp != [] and countries_db[posname_tmp[0]][0] == '2' and \
                    abs(len(posname.replace(' ', '')) - len(posname_tmp[0].replace(' ', ''))) <= 1:
                return countries_db[posname_tmp[0]][1:]

            # Делим входную строку на слова, разделитель - пробел
            parts = posname.split(" ")
            for part in parts:
                # Ищем равное по количеству букв совпадение части строки и значения с приоритетом '1'
                part_tmp = difflib.get_close_matches(part, countries_db.keys(), n=1, cutoff=dif_acc)
                if part_tmp != [] and countries_db[part_tmp[0]][0] == '1' and len(part) == len(part_tmp[0]):
                    return countries_db[part_tmp[0]][1:]
            for part in parts:
                # Ищем неравное по количеству букв совпадение части строки и значения с приоритетом '1'
                part_tmp = difflib.get_close_matches(part, countries_db.keys(), n=1, cutoff=dif_acc)
                if part_tmp != [] and countries_db[part_tmp[0]][0] == '1':
                    return countries_db[part_tmp[0]][1:]
            for part in parts:
                # Ищем равное по количеству букв совпадение части строки и значения с приоритетом '2'
                part_tmp = difflib.get_close_matches(part, countries_db.keys(), n=1, cutoff=dif_acc)
                if part_tmp != [] and countries_db[part_tmp[0]][0] == '2' and len(part) == len(part_tmp[0]):
                    return countries_db[part_tmp[0]][1:]
            for part in parts:
                # Ищем неравное по количеству букв совпадение части строки и значения с приоритетом '2'
                part_tmp = difflib.get_close_matches(part, countries_db.keys(), n=1, cutoff=dif_acc)
                if part_tmp != [] and countries_db[part_tmp[0]][0] == '2':
                    return countries_db[part_tmp[0]][1:]
            return 'None'
    # На всякий случай перехватывается Exception. Не смотря на то,
    # что ошибка здесь может быть только в отсутствии корректной базы данных
    except Exception:
            return 'DatabaseError'
