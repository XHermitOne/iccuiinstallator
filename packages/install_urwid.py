#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
Инсталляция библиотеки urwid для организации консольного интерфейса.
"""

import os
import os.path

try:
    from iccuiinstallator.ic.utils import util
    from iccuiinstallator.ic.utils import log
except ImportError:
    print(u'Ошибка импорта')


def _set_public_chmod(sPath):
    """
    """
    try:
        util.set_public_chmode_tree(sPath)
    except:
        cmd = 'chmod -R 777 %s' % sPath
        print(u'Выполнение комманды ОС <%s>' % cmd)
        os.system(cmd)


def _targz_extract(sTarFilename, sPath):
    """
    """
    try:
        util.targz_extract_to_dir(sTarFilename, sPath)
    except:
        cmd = 'tar --extract --verbose --gzip --directory=%s --file=%s' % (sPath, sTarFilename)
        print(u'Выполнение комманды ОС <%s>' % cmd)
        os.system(cmd)


def _log_info(sMsg):
    """
    """
    try:
        log.info(sMsg)
    except:
        print('INFO. %s' % sMsg)


def _log_warning(sMsg):
    """
    """
    try:
        log.warning(sMsg)
    except:
        print('WARNING. %s' % sMsg)


def install_urwid():
    """
    Инсталлировать urwid.
    """

    cur_dir = os.path.dirname(__file__)
    if not cur_dir:
        cur_dir = os.getcwd()
    tar_filename = os.path.normpath(os.path.join(cur_dir, 'urwid-1.2.1.tar.gz'))
    _log_info(u'Начало инсталляции пакета URWID')
    _log_info(u'\tТекущая директория <%s>' % cur_dir)
    _log_info(u'\tИмя файла <%s>''' % tar_filename)

    if os.path.exists(tar_filename):
        _set_public_chmod(cur_dir)
        _targz_extract(tar_filename, cur_dir)

        setup_dir = os.path.normpath(os.path.join(cur_dir, 'urwid-1.2.1'))
        setup_filename = os.path.normpath(os.path.join(setup_dir, 'setup.py'))
        if os.path.exists(setup_filename):
            cmd = 'cd %s; sudo python setup.py install' % setup_dir
            _log_info(u'Инсталляция библиотеки urwid. Команда ОС <%s>' % cmd)
            os.system(cmd)
            # Удалить после инсталляции распакованный архив
            if os.path.exists(setup_dir):
                cmd = 'sudo rm -R %s' % setup_dir
                _log_info(u'Удаление директории <%s>. Комманда <%s>' % (setup_dir, cmd))
                os.system(cmd)
        else:
            _log_warning(u'Не найден setup.py файл <%s>' % setup_filename)
    else:
        _log_warning(u'Не существует tar.gz файл <%s>' % tar_filename)


if __name__ == '__main__':
    install_urwid()
