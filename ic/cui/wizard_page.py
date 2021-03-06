#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
Страница визарда.
"""

from . import cui_dialog

from . import urwid_dialog

try:
    from ..utils import log
    from ..utils import utils
except Exception:
    from ic.utils import log
    from ic.utils import utils

__version__ = (0, 1, 1, 1)

URWID_DIALOG_TYPE = 'urwid'
PYDLG_DIALOG_TYPE = 'python-dialog'
DEFAULT_DIALOG_TYPE = URWID_DIALOG_TYPE


class icCUIWizardPage:
    """
    Страница визарда.
    """
    # Типы создаваемых диалогов
    _dialog_type = {URWID_DIALOG_TYPE: urwid_dialog.icCUIUrwidDialog,
                    PYDLG_DIALOG_TYPE: None,
                    }

    def __init__(self, Wizard, DialogType=DEFAULT_DIALOG_TYPE, *args, **kwargs):
        """
        Конструктор.
        @param Wizard: Родительский визард, в который вставляется страница.
        """
        self.dlg = None     # self.create_dialog(DialogType)
        self.wizard = Wizard
        
        self.next = None
        self.prev = None

    def create_dialog(self, sDialogType, *args, **kwargs):
        """
        Создать диалог.
        """
        dialog_class = self._dialog_type.get(sDialogType)
        if dialog_class:
            return dialog_class(*args, **kwargs)
        return None

    def getWizard(self):
        return self.wizard
    
    def setNext(self, next):
        self.next = next

    def setPrev(self, prev):
        self.prev = prev
    
    def getNext(self):
        return self.next
        
    def getPrev(self):
        return self.prev

    def addScenarioScript(self):
        pass
    
    def delScenarioScript(self):
        pass

    def add_buttons(self, lButtons, sAlign=cui_dialog.BUTTONS_ALIGN_RIGHT):
        """
        Добавление кнопок в диалоговое окно.
        @param lButtons: Список кнопок в формате:
            [('Текст',Возвращаемый код),...]
        @param sAlign: Выравнивание списка кнопок.
        """
        if self.dlg:
            return self.dlg.add_buttons(lButtons, sAlign)
        else:
            log.warning(u'Страница. Не определен диалог')
        return None

    def button_press(self, button):
        if self.dlg:
            return self.dlg.button_press(button)
        else:
            log.warning(u'Страница. Не определен диалог')
        return None

    def main(self):
        if self.dlg:
            result = self.dlg.main()
            if isinstance(result, tuple):
                # Может возвращать не только код, но необходим только код
                return result[0]
            else:
                return result
        else:
            log.warning(u'Страница. Не определен диалог')
        return None

    def on_exit(self, exitcode):
        if self.dlg:
            result = self.dlg.on_exit(exitcode)
            if isinstance(result, tuple):
                # Может возвращать не только код, но необходим только код
                return result[0]
            else:
                return result
        else:
            log.warning(u'Страница. Не определен диалог')
        return None

    def get_check_list(self):
        """
        Список выбранных элементов.
        """
        if self.dlg:
            return self.dlg.get_check_list()
        else:
            log.warning(u'Страница. Не определен диалог')
        return None
