#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
Отрисовка диалогово окна.
"""

DEFAULT_DLG_HEIGHT = 30
DEFAULT_DLG_WIDTH = 100

BUTTONS_ALIGN_LEFT = 'left'
BUTTONS_ALIGN_CENTER = 'center'
BUTTONS_ALIGN_RIGHT = 'right'


class icCUIDialog:

    def __init__(self, title='', 
                 height=DEFAULT_DLG_HEIGHT, 
                 width=DEFAULT_DLG_WIDTH, body=None):
        self.title = title
        self.width = width
        self.height = height
        self.body = body

    def add_buttons(self, lButtons, sAlign=BUTTONS_ALIGN_RIGHT):
        """
        Добавление кнопок в диалоговое окно.
        @param lButtons: Список кнопок в формате:
            [('Текст',Возвращаемый код),...]
        @param sAlign: Выравнивание списка кнопок.
        """
        pass

    def button_press(self, button):
        pass

    def main(self):
        pass

    def on_exit(self, exitcode):
        return exitcode

    def get_check_list(self):
        """
        Список выбранных элементов.
        """
        return []

