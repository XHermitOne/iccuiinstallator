#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
Окно сообщения.
"""

from . import urwid_message
from . import pydlg_message
from . import wizard_page

try:
    from iccuiinstallator.ic.utils import log
except ImportError:
    from ic.utils import log

__version__ = (0, 1, 1, 1)

DEFAULT_MSG_HEIGHT = 10


def MessageBox(sText, sTitle, sDialogType=wizard_page.DEFAULT_DIALOG_TYPE):
    """
    Диалоговое окно сообщения.
    @param sText: Текст сообщения.
    @param sTitle: Заголовок.
    @param sDialogType: Тип диалога.
    """
    if sDialogType == wizard_page.URWID_DIALOG_TYPE:
        return urwid_message.urwidMessageBox(sText, sTitle)
    elif sDialogType == wizard_page.PYDLG_DIALOG_TYPE:
        return pydlg_message.pydlgMessageBox(sText, sTitle)
    else:
        log.warning(u'Не поддерживаемый тип диалога <%s>' % sDialogType)
    return None
