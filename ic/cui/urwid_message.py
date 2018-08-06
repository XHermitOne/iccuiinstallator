#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
Окно сообщения.
"""

try:
    import urwid
    from . import cui_dialog
    from . import urwid_dialog
except ImportError:
    print(u'Ошибка импорта библиотеки urwid')

__version__ = (0, 1, 1, 1)

DEFAULT_MSG_HEIGHT = 10


def urwidMessageBox(sText, sTitle):
    """
    Диалоговое окно сообщения.
    @param sText: Текст сообщения.
    @param sTitle: Заголовок.
    """
    body = urwid.ListBox([urwid.Text(sText)])
    dlg = urwid_dialog.icCUIUrwidDialog(sTitle, DEFAULT_MSG_HEIGHT, cui_dialog.DEFAULT_DLG_WIDTH, body)
    dlg.add_buttons([('OK', 1)])
    dlg.main()
