#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
Деинсталляционные страницы визарда.
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


class icUninstallCliWizardPage(wizard_page.icCUIWizardPage):
    """
    Инсталляционные страницы визарда.
    """
    def __init__(self, *args, **kwargs):
        """
        """
        wizard_page.icCUIWizardPage.__init__(self, *args, **kwargs)


class icProgrammUninstallPage(icUninstallCliWizardPage):
    """
    Страница выбора деинсталляции программ/пакетов.
    """
    def __init__(self, Wizard, sTitle, lProgramms=None, *args, **kwargs):
        """
        Конструктор.
        @param Wizard: Родительский визард, в который вставляется страница.
        @param sTitle: Заголовок страницы.
        @param lProgramms: Описательная структура указания установленных программ.
        [
            {
            'programm':'инсталяционный файл устанавлеенной программы',
            'dir':'инсталяционная папка программы',
            },
        ...
        ]
        """

        icUninstallCliWizardPage.__init__(self, Wizard)
        self._initProgramms(lProgramms)

    def _initProgramms(self, lProgramms):
        """
        Инициализация списка удаляемых программ.
        """

        self._programms = lProgramms
        
        # Создание списка инсталируемых программ
        programm_list = []
        if self._programms:
            for programm in self._programms:
                line = [programm.get('name', programm['programm']),
                        programm.get('description', programm['programm']),
                        'on' if programm.get('check', True) else 'off']
                programm_list += line

        # log.debug(u'Список программ <%s>' % programm_list)
        self.dlg = self.create_dialog(sDialogType=utils.get_var('DIALOG_MODE'), items=programm_list)

    def create_dialog(self, sDialogType=wizard_page.URWID_DIALOG_TYPE, items=None):
        """
        Создать диалог.
        """
        if items is None:
            log.warning('Install page. Not define items for programm install page.')
            return None
        if sDialogType == wizard_page.URWID_DIALOG_TYPE:
            return urwid_dialog.do_checklist(u'Выбор программ', cui_dialog.DEFAULT_DLG_HEIGHT, cui_dialog.DEFAULT_DLG_WIDTH,
                                             cui_dialog.DEFAULT_DLG_HEIGHT, *items)
        elif sDialogType == wizard_page.PYDLG_DIALOG_TYPE:
            return pydlg_dialog.do_checklist(u'Выбор программ', cui_dialog.DEFAULT_DLG_HEIGHT, cui_dialog.DEFAULT_DLG_WIDTH,
                                             cui_dialog.DEFAULT_DLG_HEIGHT, *items)
        else:
            log.warning(u'Не поддерживаемы тип диалога <%s>' % sDialogType)
        return None

    def addScenarioScript(self):
        """
        Добавить скрипты в список сценария.
        """
        check_list = self.get_check_list()
        for i, check in enumerate(check_list):
            name = self._programms[i].get('programm', 'programm_%d' % i)
            func = tools.getFuncStr(self._programms[i].get('script', None))
            args = ()
            kwargs = {}
            kwargs.update(self._programms[i])
            kwargs.update({'page': self})
            self.wizard.addScenarioScript(name, func, args, kwargs, check)


def add_wizard_programm_uninstall_page(Wizard, lProgramms, *args, **kwargs):
    """
    Добавить страницу инсталляции программ в визард.
    @param Wizard: Объект главного визарда.
    @param lProgramms; Описание инсталлируемы/Деинсталлируемых программ.
    @return: Созданный объект страницы или None в случае ошибки.
    """
    packages = Wizard.getInstallLogManager().load_packages()
    programms = []
    if packages:
        dProgramms = dict([(prg.get('programm', prg.get('name', '-')),
                            prg) for prg in lProgramms]) if lProgramms else {}
        programms = [{'programm': package_name,
                      'dir': package_dir,
                      'description': dProgramms.get(package_name, {}).get('description', ''),
                      'script': dProgramms.get(package_name, {}).get('script', None),
                      'check': dProgramms.get(package_name, {}).get('check', True)} for package_name, package_dir in packages.items()]
    page = icProgrammUninstallPage(Wizard, u'Программы', programms, *args, **kwargs)
    Wizard.appendPage(page)
    return page    
