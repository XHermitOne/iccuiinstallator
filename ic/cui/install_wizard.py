#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Визард инсталляции.
"""

import os
import os.path

from . import wizard
from . import uninstall_manager

try:
    from iccuiinstallator import config
    from iccuiinstallator.ic.utils import util
    from iccuiinstallator.ic.utils import log
    from iccuiinstallator.ic.cui import cui_message
    from iccuiinstallator.ic.utils import utils
    from iccuiinstallator.ic.utils import ini
except ImportError:
    import config
    from ic.utils import util
    from ic.utils import log
    from ic.cui import cui_message
    from ic.utils import utils
    from ic.utils import ini

__version__ = (0, 1, 1, 1)


class icInstallCUIWizard(wizard.icCUIWizard):
    """
    Консольный визард инсталлятора.
    """
    def __init__(self, *args, **kwargs):
        wizard.icCUIWizard.__init__(self, *args, **kwargs)

        # Внутренне окружение визарда инсталяции
        self.environment = {}

        # Инсталяционная папка
        self._install_dir = None

        # Регистратор-менеджер инсталляции
        self._install_log_manager = uninstall_manager.icInstallLogManager()
        # Регистратор-менеджер деинсталляции
        self._uninstall_log_manager = uninstall_manager.icUninstallLogManager()

        # Папка настроек
        self.settings_path = None
        # файл настроек
        self.settings_filename = None

        # Настройки визарда
        self.settings = None
        self.loadSettings()

    def getInstallDir(self):
        return self._install_dir

    def getInstallLogManager(self):
        """
        Регистратор-менеджер инсталляции.
        """
        return self._install_log_manager
    
    def getUninstallLogManager(self):
        """
        Регистратор-менеджер деинсталляции.
        """
        return self._uninstall_log_manager

    def check_root(self):
        """
        Функция проверки прав администратора.
        """
        ok = util.is_root_user()
        if not ok:
            cui_message.MessageBox(u'Запуск инсталяции возможен только с правами root!', u'ВНИМАНИЕ!',
                                   sDialogType=utils.get_var('DIALOG_MODE'))
        return ok

    def loadSettings(self, INIFileName=None):
        """
        Загрузка настрок визарда.
        @param INIFileName: Файл настроек.
        @return: Словарь настроек.
        """
        if INIFileName is None:
            INIFileName = self.getSettingsFileName()
        self.settings = ini.INI2Dict(INIFileName)
        if self.settings is None:
            self.settings = {}
        return self.settings
    
    def saveSettings(self, dSettings=None, INIFileName=None):
        """
        Сохранение настроек в файле.
        @param dSettings: Словарь настроек.
        @param INIFileName: Файл настроек.
        @return: True/False.
        """
        if INIFileName is None:
            INIFileName = self.getSettingsFileName()
        if dSettings is None:
            dSettings = self.settings
        return ini.Dict2INI(dSettings, INIFileName)

    def getSettingsPath(self):
        """
        Папка сохраненных параметров программы.
            Находиться в HOME.
            Функция сразу провеяет если этой папки нет,
            то создает ее.
        """
        if self.settings_path is None:
            home_path = utils.getHomeDir()
            self.settings_path = os.path.join(home_path, config.DEFAULT_WIZ_INI_DIR)
            if not os.path.exists(self.settings_path):
                try:
                    log.info(u'Создание директории <%s>' % self.settings_path)
                    os.makedirs(self.settings_path)
                except:
                    log.fatal(u'Ошибка саздания папки <%s>' % self.settings_path)
        return self.settings_path

    def getSettingsFileName(self):
        """
        Полное имя файла настроек.
        """
        if self.settings_filename is None:
            ini_path = self.getSettingsPath()
            self.settings_filename = os.path.join(ini_path, config.DEFAULT_WIZ_INI_FILENAME)
        return self.settings_filename

    def initPage(self, Page):
        """
        Функция инициализации контролов страницы.
        @param Page: Объект страницы.
        """
        if self.settings and Page.__class__.__name__ in self.settings and hasattr(Page, 'init'):
            log.info(u'Инициализация страницы <%s> - <%s>' % (Page.__class__.__name__, self.settings[Page.__class__.__name__]))
            return Page.init(**self.settings[Page.__class__.__name__])
        return None


def install(fInstallScript=None, fPrevInstallScript=None, fPostInstallScript=None, *args, **kwargs):
    """
    Основная функция запуска инсталлятора.
    @param fInstallScript: Функция инсталляционного скрипта.
    @param fPrevInstallScript: Предварительный скрипт инсталляции.
    @param fPostInstallScript: Завершающий скрипт инсталляции.
    В качестве аргумента функция должна принимать объект визарда.
    """
    wiz = icInstallCUIWizard(u'Инсталляция программного обеспечения')

    if fPrevInstallScript:
        fPrevInstallScript(wiz, *args, **kwargs)
    
    # Запустить функцию инсталляционного скрипта
    script_ok = False
    if fInstallScript:
        script_ok = fInstallScript(wiz, *args, **kwargs)

    # Визард всегда запускается с первой страницы
    if script_ok:
        wiz_result_code = wiz.runFirstPage()
        log.debug(u'Инсталяция. Код результата <%s>' % wiz_result_code)

    if fPostInstallScript:
        fPostInstallScript(wiz, *args, **kwargs)


def uninstall(fUninstallScript=None, fPrevUninstallScript=None, fPostUninstallScript=None,
              dProgramms=None, *args, **kwargs):
    """
    Основная функция запуска деинсталлятора.
    @param Script_: Функция деинсталляционного скрипта.
    @param PrevInstallScript_: Предварительный скрипт деинсталляции.
    @param PostInstallScript_: Завершающий скрипт деинсталляции.
    @param Programms_; Описание инсталлируемы/Деинсталлируемых программ.
    В качестве аргумента функция должна принимать объект визарда.
    """
    from . import uninstall_pages
    
    wiz = icInstallCUIWizard(u'Деинсталляция программного обеспечения')
    
    if fPrevUninstallScript:
        fPrevUninstallScript(wizard, *args, **kwargs)
        
    # Запустить функцию деинсталляционного скрипта
    script_ok = False
    if fUninstallScript:
        script_ok = fUninstallScript(wizard, *args, **kwargs)
    else:
        uninstall_pages.add_wizard_programm_uninstall_page(wiz, dProgramms)
        script_ok = True

    # Визард всегда запускается с первой страницы
    if script_ok:
        wiz_result_code = wiz.runFirstPage()
        log.debug(u'Деинсталяция. Код результата <%d>' % wiz_result_code)

    if fPostUninstallScript:
        fPostUninstallScript(wizard, *args, **kwargs)
