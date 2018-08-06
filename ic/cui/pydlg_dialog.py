#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
Python dialog. Отрисовка диалогово окна.
"""

from . import cui_dialog

try:
    import dialog
except ImportError:
    print(u'Ошибка импорта библиотеки python-dialog')

try:
    from iccuiinstallator import config
except ImportError:
    import config

__version__ = (0, 1, 1, 1)


DEFAULT_BACKGROUND_DIALOG_TITLE = config.DEFAULT_TITLE

DEFAULT_LIST_HEIGHT = cui_dialog.DEFAULT_DLG_HEIGHT - 10


class icCUIPyDlgDialog(cui_dialog.icCUIDialog, dialog.Dialog):

    def __init__(self, title='', height=cui_dialog.DEFAULT_DLG_HEIGHT,
                 width=cui_dialog.DEFAULT_DLG_WIDTH, body='', *args, **kwargs):
        cui_dialog.icCUIDialog.__init__(self, title=title, height=height, width=width, body=body)
        dialog.Dialog.__init__(self, *args, **kwargs)

        try:
            self.set_background_title(DEFAULT_BACKGROUND_DIALOG_TITLE)
        except AttributeError:
            # Для поддержки более ранних версий
            self.setBackgroundTitle(DEFAULT_BACKGROUND_DIALOG_TITLE)


class icCUIPyDlgYesNoDialog(icCUIPyDlgDialog):

    def main(self):
        result = self.yesno(self.body, width=self.width, height=self.height, title=self.title)
        return result == self.OK


class icCUIPyDlgMsgBoxDialog(icCUIPyDlgDialog):

    def main(self):
        result = self.msgbox(self.body, width=self.width, height=self.height, title=self.title)
        return result == self.OK


class icCUIPyDlgInputBoxDialog(icCUIPyDlgDialog):

    def main(self):
        return self.inputbox(self.title, width=self.width, height=self.height)


class icCUIPyDlgTextBoxDialog(icCUIPyDlgDialog):

    def main(self):
        return self.editbox(self.body, width=self.width, height=self.height)


class icCUIPyDlgCheckListDialog(icCUIPyDlgDialog):

    def __init__(self, title='', height=cui_dialog.DEFAULT_DLG_HEIGHT, width=cui_dialog.DEFAULT_DLG_WIDTH,
                 list_height=DEFAULT_LIST_HEIGHT, body='', *args, **kwargs):
        icCUIPyDlgDialog.__init__(self, title=title, height=height, width=width, body=body, *args, **kwargs)

        self.list_height = list_height
        self.result = None

    def main(self):
        if self.body:
            self.result = self.checklist(text=self.title, width=self.width, height=self.height,
                                         list_height=self.list_height, choices=self.body)
        else:
            self.result = (self.msgbox(u'ВНИМАНИЕ! Пустой список выбора',
                                       width=self.width, height=self.height, title=self.title), None)
        return self.result[0] == self.OK, self.result[1:]

    def get_check_list(self):
        body = [line[0] for line in self.body]
        result = [name in self.result[1] for name in body]
        return result


class icCUIPyDlgRadioListDialog(icCUIPyDlgDialog):

    def __init__(self, title='', height=cui_dialog.DEFAULT_DLG_HEIGHT, width=cui_dialog.DEFAULT_DLG_WIDTH,
                 list_height=DEFAULT_LIST_HEIGHT, body='', *args, **kwargs):
        icCUIPyDlgDialog.__init__(self, title=title, height=height, width=width, body=body, *args, **kwargs)

        self.list_height = list_height
        self.result = None

    def main(self):
        # print self.body
        self.result = self.radiolist(text=self.title, width=self.width, height=self.height,
                                     list_height=self.list_height, choices=self.body)
        return self.result[0] == self.OK, self.result[1]

    def get_check_list(self):
        body = [line[0] for line in self.body]
        result = [name in self.result[1] for name in body]
        return result


LIST_ELEMENT_HIDDEN = 0x1
LIST_ELEMENT_READ_ONLY = 0x2


class icCUIPyDlgListDialog(icCUIPyDlgDialog):

    def __init__(self, title='', height=cui_dialog.DEFAULT_DLG_HEIGHT, width=cui_dialog.DEFAULT_DLG_WIDTH,
                 list_height=DEFAULT_LIST_HEIGHT, body='', *args, **kwargs):
        icCUIPyDlgDialog.__init__(self, title=title, height=height, width=width, body=body, *args, **kwargs)

        self.list_height = list_height
        self.result = None

    def main(self):
        try:
            if self.body:
                self.result = self.mixedform(text=self.title, elements=self.body,
                                             height=self.height, width=self.width,
                                             form_height=self.list_height)

                return self.result[0] == self.OK
            else:
                # Списка нет
                return True
        except:
            # print '>>>', self.height, self.width, self.list_height
            raise


def do_list(text, height=cui_dialog.DEFAULT_DLG_HEIGHT, width=cui_dialog.DEFAULT_DLG_WIDTH,
            list_height=DEFAULT_LIST_HEIGHT, *items):
    elements = [(items[i*3], i+1, 1, items[i*3+1], i+1, 20, 0, 0, LIST_ELEMENT_READ_ONLY) for i in range(len(items)/3)]
    return icCUIPyDlgListDialog(title=text, width=width, height=height,
                                list_height=list_height, body=elements)


def do_checklist(text, height=cui_dialog.DEFAULT_DLG_HEIGHT, width=cui_dialog.DEFAULT_DLG_WIDTH,
                 list_height=DEFAULT_LIST_HEIGHT, *items):
    # choices = [(items[i*3], items[i*3+1],
    #             'on' if items[i*3+2] else 'off') for i in range(len(items)/3)]
    choices = [(items[i*3], items[i*3+1],
                items[i*3+2]) for i in range(len(items)/3)]
    return icCUIPyDlgCheckListDialog(title=text, width=width, height=height,
                                     list_height=list_height, body=choices)


def do_inputbox(text, height=cui_dialog.DEFAULT_DLG_HEIGHT, width=cui_dialog.DEFAULT_DLG_WIDTH):
    return icCUIPyDlgInputBoxDialog(title=text, width=width, height=height)


def do_msgbox(text, height=cui_dialog.DEFAULT_DLG_HEIGHT, width=cui_dialog.DEFAULT_DLG_WIDTH):
    return icCUIPyDlgMsgBoxDialog(title=u'Сообщение', width=width, height=height, body=text)


def do_radiolist(text, height=cui_dialog.DEFAULT_DLG_HEIGHT, width=cui_dialog.DEFAULT_DLG_WIDTH,
                 list_height=DEFAULT_LIST_HEIGHT, *items):
    choices = [(items[i*3], items[i*3+1], 'on' if items[i*3+2] else 'off') for i in range(len(items)/3)]
    return icCUIPyDlgRadioListDialog(title=text, width=width, height=height,
                                     list_height=list_height, body=choices)


def do_textbox(filename, height=cui_dialog.DEFAULT_DLG_HEIGHT, width=cui_dialog.DEFAULT_DLG_WIDTH):
    return icCUIPyDlgTextBoxDialog(body=filename, width=width, height=height)


def do_yesno(text, height=cui_dialog.DEFAULT_DLG_HEIGHT, width=cui_dialog.DEFAULT_DLG_WIDTH):
    return icCUIPyDlgYesNoDialog(title=u'Вопрос', width=width, height=height, body=text)


def test_yesno():
    dlg = do_yesno(u'Русский текст', 10, 50)
    result = dlg.main()
    return 'YesNo <%s>' % result


def test_msgbox():
    dlg = do_msgbox(u'Русский текст', 10, 50)
    result = dlg.main()
    return 'MsgBox <%s>' % result


def test_textbox():
    import os
    filename = os.path.splitext(__file__)[0]+'.py'
    dlg = do_textbox(filename, 30, 50)
    result = dlg.main()
    return 'TextBox <%s>' % result[0]


def test_inputbox():
    dlg = do_inputbox(u'Ввод', 30, 50)
    result = dlg.main()
    return 'InputBox <%s>' % result[0]


def test_checklist():
    dlg = do_checklist(u'Check list пример', 30, 50, 20, u'Текст1', u'Text1', 3, u'Text2', u'Текст2', 'on')
    result = dlg.main()
    return 'CheckList <%s>' % result[0]


def test_radiolist():
    dlg = do_radiolist(u'Check list пример', 30, 50, 20, u'Текст1', u'Text1', 3, u'Text2', u'Текст2', 5)
    result = dlg.main()
    return 'RadioList <%s>' % result[0]


def test_list():
    dlg = do_list(u'Check list пример', 30, 50, 20, u'Текст1', u'Text1', 3, u'Text2', u'Текст2', 5)
    result = dlg.main()
    return 'List <%s>' % result


if __name__ == '__main__':
    results = list()
    results.append(test_yesno())
    results.append(test_msgbox())
    results.append(test_inputbox())
    results.append(test_textbox())
    results.append(test_checklist())
    results.append(test_radiolist())
    results.append(test_list())

    for result in results:
        print(u'Результат', result)
