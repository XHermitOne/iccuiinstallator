#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
Инсталляция библиотеки pythondialog для организации консольного интерфейса.
"""

import os
import os.path

try:
    from ..utils import util
    from ..utils import log
except Exception:
    print(u'Ошибка импорта в модуле install_pythondialog')

__version__ = (0, 1, 1, 1)


def _set_public_chmod(sPath):
    """
    """
    try:
        util.set_public_chmode_tree(sPath)
    except:
        cmd = 'chmod -R 777 %s' % sPath
        log.info(u'Выполнение комманды ОС <%s>' % cmd)
        os.system(cmd)


def _targz_extract(sTarFilename, sPath):
    """
    """
    try:
        util.targz_extract_to_dir(sTarFilename, sPath)
    except:
        cmd = 'tar --extract --verbose --gzip --directory=%s --file=%s' % (sPath, sTarFilename)
        log.warning(u'Выполнение комманды ОС <%s>' % cmd)
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


def install_pythondialog():
    """
    Инсталлировать pythondialog.
    """
    cur_dir = os.path.dirname(__file__)
    if not cur_dir:
        cur_dir = os.getcwd()

    tar_filename = os.path.normpath(os.path.join(cur_dir, 'python2-pythondialog-3.3.0.tar.gz'))
    _log_info(u'Начало инсталляции пакета PYTHONDIALOG')
    _log_info(u'\tТекущая директория <%s>' % cur_dir)
    _log_info(u'\tИмя файла <%s>''' % tar_filename)

    if os.path.exists(tar_filename):
        _set_public_chmod(cur_dir)
        _targz_extract(tar_filename, cur_dir)

        setup_dir = os.path.normpath(os.path.join(cur_dir, 'python2-pythondialog-3.3.0'))
        setup_filename = os.path.normpath(os.path.join(setup_dir, 'setup.py'))
        if os.path.exists(setup_filename):
            cmd = 'cd %s; sudo python setup.py install' % setup_dir
            _log_info(u'Инсталяция библиотеки pythondialog. Комманда ОС <%s>' % cmd)
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
    install_pythondialog()
