#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
Инсталляционные страницы визарда.
"""

from . import cui_dialog
from . import urwid_dialog
from . import pydlg_dialog
from . import wizard_page

try:
    from ..utils import util
    from ..utils import log
    from ..utils import tools
    from ..utils import utils
except Exception:
    from ic.utils import util
    from ic.utils import log
    from ic.utils import tools
    from ic.utils import utils


__version__ = (0, 1, 1, 1)


class icInstallCUIWizardPage(wizard_page.icCUIWizardPage):
    """
    Инсталляционные страницы визарда.
    """
    def __init__(self, *args, **kwargs):
        """
        """
        wizard_page.icCUIWizardPage.__init__(self, *args, **kwargs)
    
    def getData(self):
        return None
    
    def init(self, **kwargs):
        """
        Иницализация контролов.
        """
        # for name, value in kwargs.items():
        #     for ctrlname in dir(self.panel):
        #         if ctrlname.lower() == name:
        #             ctrl = getattr(self.panel, ctrlname)
        #             if issubclass(ctrl.__class__, wx.CheckBox):
        #                 ctrl.SetValue(value)
        #             elif issubclass(ctrl.__class__, wx.TextCtrl):
        #                 ctrl.SetValue(value)
        #             elif issubclass(ctrl.__class__, wx.DatePickerCtrl):
        #                 dt = wx.DateTime()
        #                 dt.ParseFormat(value, config.DEFAULT_DATE_FORMAT)
        #                 ctrl.SetValue(dt)
        #             elif issubclass(ctrl.__class__, wx.DirPickerCtrl):
        #                 ctrl.SetPath(value)
        #             else:
        #                 log.warning('Wizard get values. Type %s not supported' % ctrl.__class__.__name__)
        #             break
        pass


class icPackageControlPage(icInstallCUIWizardPage):
    """
    Страница проверки установленных пакетов и их версий.
    Если контрольпакетов не проходит, то переход на следующую страницу блокируется, 
    т.к. нет смысла продолжать инсталяцию.
    """

    def __init__(self, Wizard, sTitle, dPackages=None, *args, **kwargs):
        """
        Конструктор.
        @param parent: Родительский визард, в который вставляется страница.
        @param sTitle: Заголовок страницы.
        @param dPackage: Описательная структура проверки наличия python пакетов.
        Формат:
        {
        'имя пакета':{
            'type':'py' или 'pkg',
            'ver':'версия',
            'compare':'условие проверки'
            }
        }
        """
        icInstallCUIWizardPage.__init__(self, Wizard)
        self._initPackages(dPackages)

    def _initPackages(self, dPackages):
        """
        Инициализация списка пакетов.
        """
        package_list = []
        # Данные списка пакетов
        self.result = True
        if dPackages:
            log.debug(u'Список контролируемых пакетов:')
            for package_name, package_misc in dPackages.items():
                if 'type' in package_misc:
                    package_type = package_misc['type']
                else:
                    package_type = 'py'

                # Определение версии
                if 'ver' in package_misc:
                    package_ver = package_misc['ver']
                else:
                    package_ver = ''
                if 'compare' in package_misc:
                    package_compare = package_misc['compare']
                else:
                    package_compare = '=='

                # Проверка наличия пакетов
                result = False
                if package_type == 'py':
                    result = util.check_python_library_version(package_name, package_ver, package_compare)
                    # Если пакет не установлен, 
                    # то попытаться поставить его из пакетов инсталлятора
                    if not result:
                        autoinstall_pack = package_misc.get('auto', None)
                        result = util.targz_install_python_package(autoinstall_pack)
                elif package_type == 'pkg':
                    result = util.check_linux_package(package_name, package_ver, package_compare)
                    
                self.result = self.result and result
                check_package_ver = package_ver if result else u'Не установлен/Не сооответствует версии %s' % package_ver
                line = (package_name, check_package_ver, result)
                log.debug(u'\t%s\tver: (%s)\t[%s]' % (package_name, check_package_ver, result))
                package_list += list(line)

        # Создание списка пакетов
        self.dlg = self.create_dialog(sDialogType=utils.get_var('DIALOG_MODE'), items=package_list)

    def create_dialog(self, sDialogType=wizard_page.URWID_DIALOG_TYPE, items=None):
        """
        Создать диалог.
        """
        if items is None:
            log.warning('Install page. Not define items for package control page.')
            return None

        if sDialogType == wizard_page.URWID_DIALOG_TYPE:
            return urwid_dialog.do_list(u'Контроль установленных пакетов',
                                        cui_dialog.DEFAULT_DLG_HEIGHT, cui_dialog.DEFAULT_DLG_WIDTH,
                                        cui_dialog.DEFAULT_DLG_HEIGHT, *items)
        elif sDialogType == wizard_page.PYDLG_DIALOG_TYPE:
            return pydlg_dialog.do_list(u'Контроль установленных пакетов',
                                        cui_dialog.DEFAULT_DLG_HEIGHT, cui_dialog.DEFAULT_DLG_WIDTH,
                                        pydlg_dialog.DEFAULT_LIST_HEIGHT, *items)
        else:
            log.warning(u'Не поддерживаемый тип диалога <%s>' % sDialogType)
        return None

    def getNext(self):
        """
        Если все библиотеки присутствуют, то перейти на следующую страницу,
        иначе пропустить следующую страницу.
        """
        if not self.result:
            self.setNext(None)
        return self.next
    

class icProgrammInstallPage(icInstallCUIWizardPage):
    """
    Страница выбора установки программ.
    """

    def __init__(self, Wizard, sTitle, lProgramms=None):
        """
        Конструктор.
        @param Wizard: Родительский визард, в который вставляется страница.
        @param sTitle: Заголовок страницы.
        @param lProgramms: Описательная структура указания устанавливаемых программ.
        [
            {
            'programm':'инсталяционный файл устанавлеемой программы',
            'dir':'инсталяционная папка программы',
            'pth':{
                'name':'имя генерируемого pth-файла',
                'dir':'указание папки, которую содержит pth-файл',
                'var':'пересенная из окружения визарда, которая содержит путь до папки',
                },
            },
        ...
        ]
        """
        icInstallCUIWizardPage.__init__(self, Wizard)
        self._initProgramm(lProgramms)

    def getData(self):
        return self._programms

    def _initProgramm(self, lProgrammss):
        """
        """
        self._programms = lProgrammss
        
        # Создание списка инсталируемых программ
        programm_list = []
        if self._programms:
            log.debug(u'Список инсталлируемых программ:')
            for programm in self._programms:
                line = [programm.get('name', programm.get('programm', '-')),
                        programm.get('description', programm.get('programm', '-')),
                        'on' if programm.get('check', False) else 'off']
                log.debug(u'\t%s\t(%s)\t[%s]' % (line[0], line[1], line[2]))
                programm_list += line

        self.dlg = self.create_dialog(sDialogType=utils.get_var('DIALOG_MODE'), items=programm_list)

    def create_dialog(self, sDialogType=wizard_page.URWID_DIALOG_TYPE, items=None):
        """
        Создать диалог.
        """
        if items is None:
            log.warning(u'Не определены элементы страницы устанавливаемых программ')
            return None
        if sDialogType == wizard_page.URWID_DIALOG_TYPE:
            return urwid_dialog.do_checklist(u'Выбор программ', cui_dialog.DEFAULT_DLG_HEIGHT, cui_dialog.DEFAULT_DLG_WIDTH,
                                             cui_dialog.DEFAULT_DLG_HEIGHT, *items)
        elif sDialogType == wizard_page.PYDLG_DIALOG_TYPE:
            return pydlg_dialog.do_checklist(u'Выбор программ', cui_dialog.DEFAULT_DLG_HEIGHT, cui_dialog.DEFAULT_DLG_WIDTH,
                                             cui_dialog.DEFAULT_DLG_HEIGHT, *items)
        else:
            log.warning(u'Не поддерживаемый тип диалога <%s>' % sDialogType)
        return None

    def addScenarioScript(self):
        """
        Добавить скрипты в список сценария.
        """
        check_list = self.get_check_list()
        if not check_list:
            log.warning(u'Не определен список инсталируемых программ')
            return
        # log.debug('Check list <%s> programms %s' % (check_list, len(self._programms)))
        for i, check in enumerate(check_list):
            name = self._programms[i].get('name', 'programm_%d' % i)
            func = tools.getFuncStr(self._programms[i].get('script', None))
            args = ()
            kwargs = {}
            kwargs.update(self._programms[i])
            kwargs.update({'page': self})
            self.wizard.addScenarioScript(name, func, args, kwargs, check)


def add_wizard_package_control_page(Wizard, *args, **kwargs):
    """
    Добавить страницу проверки установленных пакетов в визард.
    @param Wizard: Объект главного визарда.
    @return: Созданный объект страницы или None в случае ошибки.
    """
    page = icPackageControlPage(Wizard, u'Проверка пакетов', *args, **kwargs)
    Wizard.appendPage(page)
    return page    


def add_wizard_programm_install_page(Wizard, *args, **kwargs):
    """
    Добавить страницу инсталляции программ в визард.
    @param Wizard: Объект главного визарда.
    @return: Созданный объект страницы или None в случае ошибки.
    """
    page = icProgrammInstallPage(Wizard, u'Программы', *args, **kwargs)
    Wizard.appendPage(page)
    return page

