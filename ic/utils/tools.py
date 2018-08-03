#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

""" 
Дополниетельные сервисные функции.
"""

import sys

import log

__version__ = (0, 0, 1, 1)


def unLoadSource(name):
    """ 
    Выгрузить модуль.
    @type name: C{string}
    @param name: Имя модуля.
    """
    if name in sys.modules:
        del sys.modules[name]
        return True
    return False


def getFuncStr(sFuncStr, dEnv=None, bReImport=False, 
               *args, **kwargs):
    """ 
    Получение объекта функции по строке в формате: пакеты.модуль.функция.
    @type sFuncStr: C{string}
    @param sFuncStr: Строковая функция.
    @type dEnv: C{dictionary}
    @param dEnv: Пространство имен.
    @type bReImport: C{bool}
    @param bReImport: Переимпортировать модуль функции?
    @return: Вовращает объект функции или None  в случае ошибки.
    """
    if not sFuncStr:
        log.warning('Empty function string name <%s> in getFuncStr' % sFuncStr)
        return None
    
    result = None

    # Выделить модуль функции
    func_mod = '.'.join(sFuncStr.split('.')[:-1])
        
    # Подготовить пространство имен
    if dEnv is None or type(dEnv) <> type({}):
        dEnv = {}

    # Выполнение функции
    try:
        try:
            if bReImport:
                unLoadSource(func_mod)
            import_str = 'import '+func_mod
            exec import_str
        except:
            log.error('Import module <%s>' % import_str)
            raise

        dEnv.update(locals())

        result = eval(sFuncStr, globals(), dEnv)
    except:
        log.error('Get function: <%s> ' % sFuncStr)
        raise
    
    return result
