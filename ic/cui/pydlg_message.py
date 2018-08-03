#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
Python dialog. Окно сообщения.
"""

try:
    import dialog
except ImportError:
    print(u'ERROR. Import error python-dialog')

try:
    import cui_dialog
except ImportError:
    pass

__version__ = (0, 0, 2, 2)

DEFAULT_MSG_HEIGHT = 10


def pydlgMessageBox(sText, sTitle):
    """
    Диалоговое окно сообщения.
    @param sText: Текст сообщения.
    @param sTitle: Заголовок.
    """
    dlg = dialog.Dialog(dialog='dialog')
    dlg.msgbox(sText, width=cui_dialog.DEFAULT_DLG_WIDTH, height=DEFAULT_MSG_HEIGHT, title=sTitle)


def test():
    pydlgMessageBox(u'Тестовое сообщение', u'Заголовок')

if __name__ == '__main__':
    test()