#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
URWID. Отрисовка диалогово окна.
"""

import cui_dialog

try:
    import urwid
except ImportError:
    print(u'ERROR. Import error urwid')

__version__ = (0, 0, 2, 2)


class icCUIUrwidDialogExitException(Exception):
    pass


class icCUIUrwidDialog(cui_dialog.icCUIDialog):
    palette = [
        ('body', 'black', 'light gray', 'standout'),
        ('border', 'black', 'dark blue'),
        ('shadow', 'white', 'black'),
        ('selectable', 'black', 'dark cyan'),
        ('focus', 'white', 'dark blue', 'bold'),
        ('focustext', 'light gray', 'dark blue'),
        ]
        
    def __init__(self, title='', 
                 height=cui_dialog.DEFAULT_DLG_HEIGHT,
                 width=cui_dialog.DEFAULT_DLG_WIDTH, body=None):
                 
        width = int(width)
        if width <= 0:
            width = ('relative', 80)
            
        height = int(height)
        if height <= 0:
            height = ('relative', 80)
    
        self.body = body
        if body is None:
            # fill space with nothing
            body = urwid.Filler(urwid.Divider(), 'top')

        self.frame = urwid.Frame(body, focus_part='footer')
        if title is not None:
            self.frame.header = urwid.Pile([urwid.Text(title), urwid.Divider()])
        w = self.frame
        
        # pad area around listbox
        w = urwid.Padding(w, ('fixed left', 2), ('fixed right', 2))
        w = urwid.Filler(w, ('fixed top', 1), ('fixed bottom', 1))
        w = urwid.AttrWrap(w, 'body')
        
        # "shadow" effect
        w = urwid.Columns([w, ('fixed', 2, urwid.AttrWrap(
            urwid.Filler(urwid.Text(('border', '  ')), 'top'), 'shadow'))])
        w = urwid.Frame(w, footer=urwid.AttrWrap(urwid.Text(('border', '  ')), 'shadow'))

        # outermost border area
        w = urwid.Padding(w, 'center', width)
        w = urwid.Filler(w, 'middle', height)
        w = urwid.AttrWrap(w, 'border')
        
        self.view = w

    def add_buttons(self, lButtons, sAlign=cui_dialog.BUTTONS_ALIGN_RIGHT):
        """
        Добавление кнопок в диалоговое окно.
        @param lButtons: Список кнопок в формате:
            [('Текст',Возвращаемый код),...]
        @param sAlign: Выравнивание списка кнопок.
        """
        l = []
        for name, exitcode in lButtons:
            b = urwid.Button(name, self.button_press)
            b.exitcode = exitcode
            b = urwid.AttrWrap(b, 'selectable', 'focus')
            l.append(b)
        self.buttons = urwid.GridFlow(l, 10, 3, 1, sAlign)
        self.frame.footer = urwid.Pile([urwid.Divider(),
                                        self.buttons], focus_item=1)

    def button_press(self, button):
        raise icCUIUrwidDialogExitException(button.exitcode)

    def main(self):
        loop = urwid.MainLoop(self.view, self.palette)
        try:
            loop.run()
        except icCUIUrwidDialogExitException, e:
            return self.on_exit(e.args[0])
        return None
        
    def on_exit(self, exitcode):
        return exitcode


class icCUIUrwidInputDialog(icCUIUrwidDialog):
    def __init__(self, text, height, width):
        self.edit = urwid.Edit()
        body = urwid.ListBox([self.edit])
        body = urwid.AttrWrap(body, 'selectable', 'focustext')

        icCUIUrwidDialog.__init__(self, text, height, width, body)

        self.frame.set_focus('body')

    def unhandled_key(self, size, k):
        if k in ('up', 'page up'):
            self.frame.set_focus('body')
        if k in ('down', 'page down'):
            self.frame.set_focus('footer')
        if k == 'enter':
            # pass enter to the "ok" button
            self.frame.set_focus('footer')
            self.view.keypress(size, k)

    def on_exit(self, exitcode):
        return exitcode, self.edit.get_edit_text()


class icCUIUrwidTextDialog(icCUIUrwidDialog):
    def __init__(self, filename, height, width):
        l = []
        # read the whole file (being slow, not lazy this time)
        for line in open(filename).readlines():
            l.append(urwid.Text(line.rstrip()))
        body = urwid.ListBox(l)
        body = urwid.AttrWrap(body, 'selectable', 'focustext')

        icCUIUrwidDialog.__init__(self, None, height, width, body)

    def unhandled_key(self, size, k):
        if k in ('up', 'page up', 'down', 'page down'):
            self.frame.set_focus('body')
            self.view.keypress(size, k)
            self.frame.set_focus('footer')


class icCUIUrwidListDialog(icCUIUrwidDialog):
    def __init__(self, text, height, width, constr, items, has_default):
        j = []
        if has_default:
            k, tail = 3, ()
        else:
            k, tail = 2, ('no',)
        while items:
            j.append(items[:k] + tail)
            items = items[k:]

        l = []
        self.items = []
        for tag, item, default in j:
            w = constr(tag, default == 'on')
            self.items.append(w)
            w = urwid.Columns([('fixed', 30, w), urwid.Text(item)], 2)
            w = urwid.AttrWrap(w, 'selectable', 'focus')
            l.append(w)

        lb = urwid.ListBox(l)
        lb = urwid.AttrWrap(lb, 'selectable')
        icCUIUrwidDialog.__init__(self, text, height, width, lb)

        self.frame.set_focus('body')

    def unhandled_key(self, size, k):
        if k in ('up', 'page up'):
            self.frame.set_focus('body')
        if k in ('down', 'page down'):
            self.frame.set_focus('footer')
        if k == 'enter':
            # pass enter to the "ok" button
            self.frame.set_focus('footer')
            self.buttons.set_focus(0)
            self.view.keypress(size, k)

    def on_exit(self, exitcode):
        """
        Print the tag of the item selected.
        """
        if exitcode != 0:
            return exitcode, ''
        s = ''
        for i in self.items:
            if i.get_state():
                s = i.get_label()
                break
        return exitcode, s

    def get_check_list(self):
        """
        Список выбранных элементов.
        """
        return [item.get_state() for item in self.items]


class icCUIUrwidCheckListDialog(icCUIUrwidListDialog):
    def on_exit(self, exitcode):
        """
        Mimic dialog(1)'s --checklist exit.
        Put each checked item in double quotes with a trailing space.
        """
        if exitcode != 0:
            return exitcode, ''
        l = []
        for i in self.items:
            if i.get_state():
                l.append(i.get_label())
        return exitcode, ''.join(['"'+tag+'" ' for tag in l])


class icCUIUrwidListBoxButton(urwid.Button):
    """
    Кнопка списка.
    """
    def __init__(self, *args, **kwargs):
        state = None
        if 'state' in kwargs:
            state = kwargs['state']
            del kwargs['state']
        self.state = state

        urwid.Button.__init__(self, *args, **kwargs)

    def get_state(self):
        return self.state


def do_list(text, height=cui_dialog.DEFAULT_DLG_HEIGHT, width=cui_dialog.DEFAULT_DLG_WIDTH,
                 list_height=cui_dialog.DEFAULT_DLG_HEIGHT, *items):
    def constr(tag, state):
        return icCUIUrwidListBoxButton(tag, state=state)
    d = icCUIUrwidListDialog(text, height, width, constr, items, True)
    d.add_buttons([('OK', 0), ('Cancel', 1)])
    return d


def do_checklist(text, height=cui_dialog.DEFAULT_DLG_HEIGHT, width=cui_dialog.DEFAULT_DLG_WIDTH,
                 list_height=cui_dialog.DEFAULT_DLG_HEIGHT, *items):
    def constr(tag, state):
        # print tag, state
        return urwid.CheckBox(tag, state)
    d = icCUIUrwidCheckListDialog(text, height, width, constr, items, True)
    d.add_buttons([('OK', 0), ('Cancel', 1)])
    return d


def do_inputbox(text, height=cui_dialog.DEFAULT_DLG_HEIGHT, width=cui_dialog.DEFAULT_DLG_WIDTH):
    d = icCUIUrwidInputDialog(text, height, width)
    d.add_buttons([('Exit', 0)])
    return d


def do_msgbox(text, height=cui_dialog.DEFAULT_DLG_HEIGHT, width=cui_dialog.DEFAULT_DLG_WIDTH):
    d = icCUIUrwidDialog(text, height, width)
    d.add_buttons([('OK', 0)])
    return d


def do_radiolist(text, height=cui_dialog.DEFAULT_DLG_HEIGHT, width=cui_dialog.DEFAULT_DLG_WIDTH,
                 list_height=cui_dialog.DEFAULT_DLG_HEIGHT, *items):
    radiolist = []

    def constr(tag, state, radiolist=radiolist):
        return urwid.RadioButton(radiolist, tag, state)

    d = icCUIUrwidListDialog(text, height, width, constr, items, True)
    d.add_buttons([('OK', 0), ('Cancel', 1)])
    return d


def do_textbox(filename, height=cui_dialog.DEFAULT_DLG_HEIGHT, width=cui_dialog.DEFAULT_DLG_WIDTH):
    d = icCUIUrwidTextDialog(filename, height, width)
    d.add_buttons([('Exit', 0)])
    return d


def do_yesno(text, height=cui_dialog.DEFAULT_DLG_HEIGHT, width=cui_dialog.DEFAULT_DLG_WIDTH):
    d = icCUIUrwidDialog(text, height, width)
    d.add_buttons([('Yes', 0), ('No', 1)])
    return d


def test():

    l = []

    for i, line in enumerate(open('./wizard.py').readlines()):
        text = urwid.Columns([urwid.Text(line.rstrip()), urwid.Text('+++')])
        if i < 10:
            text = urwid.AttrMap(text, urwid.AttrSpec('light red', 'light gray'))
        else:
            text = urwid.AttrMap(text, urwid.AttrSpec('dark green', 'light gray'))
        l.append(text)

    l = [urwid.Columns([urwid.Text('Text'), urwid.Text('Version')])]+l
    body = urwid.ListBox(l)

    dlg = icCUIUrwidDialog(title=u'Русский текст', body=body)
    dlg.add_buttons([('Prev', -1), ('Next', 1), ('Cancel', 0)])
    result = dlg.main()
    print('Dialog return <%s>' % result)
    i = 0
    while result == 1 or result == -1:
        dlg = icCUIUrwidDialog(title=u'Русский текст <%d>' % i)
        dlg.add_buttons([('Prev', -1), ('Next', 1), ('Cancel', 0)])
        i += 1
        result = dlg.main()
        print('Dialog return <%s>' % result)


def test_yesno():
    dlg = do_yesno(u'Русский текст', 10, 50)
    result = dlg.main()
    print('Dialog return <%s>' % result)


def test_msgbox():
    dlg = do_msgbox(u'Русский текст', 10, 50)
    result = dlg.main()
    print('Dialog return <%s>' % result)


def test_textbox():
    import os
    filename = os.path.splitext(__file__)[0]+'.py'
    dlg = do_textbox(filename, 30, 50)
    result = dlg.main()
    print('Dialog return <%s>' % result)


def test_inputbox():
    dlg = do_inputbox(u'Ввод', 30, 50)
    result = dlg.main()
    print('Dialog return ', result)


def test_checklist():
    dlg = do_checklist(u'Check list пример', 30, 50, 1, u'Текст1', u'Text1', 3, u'Text2', u'Текст2', 'on')
    result = dlg.main()
    print('Dialog return', result)


def test_radiolist():
    dlg = do_radiolist(u'Check list пример', 30, 50, 1, u'Текст1', u'Text1', 3, u'Text2', u'Текст2', 5)
    result = dlg.main()
    print('Dialog return', result)


def test_list():
    dlg = do_list(u'Check list пример', 30, 50, 1, u'Текст1', u'Text1', 3, u'Text2', u'Текст2', 5)
    result = dlg.main()
    print('Dialog return', result)

if __name__ == '__main__':
    # test()
    test_yesno()
    test_msgbox()
    test_inputbox()
    test_textbox()
    test_checklist()
    test_radiolist()
    test_list()
