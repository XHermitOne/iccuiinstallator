#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
""" 
Менеджер деинсталляции.
"""

# --- Imports ---
import os
import os.path
import shutil
import time

try:
    from iccuiinstallator.ic.utils import log
    from iccuiinstallator.ic.utils import util
except ImportError:
    from ic.utils import log
    from ic.utils import util

__version__ = (0, 0, 2, 2)

INSTALLATOR_SETTINGS_DIR = '.iccuiinstallator'
INSTALL_LOG_FILE_NAME = 'install.log'
UNINSTALL_LOG_FILE_NAME = 'uninstall.log'


class icInstallLogManagerPrototype:
    """
    Прототип класса управления инсталляционным логом.
    """
    def __init__(self, sInstallLogFileName=None):
        """
        Конструктор.
        @param sInstallLogFileName: Имя файла инсталляционного лога.
        """
        self._install_log_file_name = sInstallLogFileName
        
    def get_install_log_file_name(self):
        """
        Полное имя файла install.log.
        """
        return self._install_log_file_name

    def is_installed_package(self, sPackageName):
        """
        Проверить проинсталлированн ли уже пакет с указанным именем.
        @return: Возвращает True/False.
        """
        install_log_file = None
        try:
            if not os.path.exists(self.get_install_log_file_name()):
                log.warning('File <%s> not found!' % self.get_install_log_file_name())
                return False
            
            install_log_file = open(self.get_install_log_file_name(), 'rt')
            lines = install_log_file.readlines()
            package_names = [line.split(';')[0].strip() for line in lines]
            install_log_file.close()
            install_log_file = None

            return bool(sPackageName.strip() in package_names)
        except:
            if install_log_file:
                install_log_file.close()
            raise            
        
    def _create_install_log_file(self, sInstallLogFileName=None):
        """
        Создание файла install.log.
        """
        if sInstallLogFileName is None:
            sInstallLogFileName = self.get_install_log_file_name()
            
        install_log_file = None
        try:
            if not os.path.exists(sInstallLogFileName):
                path = os.path.dirname(sInstallLogFileName)
                if not os.path.exists(path):
                    os.makedirs(path)
                install_log_file = open(sInstallLogFileName, 'wt')
                install_log_file.close()
                install_log_file = None
                log.info('File <%s> create!' % sInstallLogFileName)
                return True
            return False
        except:
            if install_log_file:
                install_log_file.close()
            raise
        
    def log_install_package(self, sPackageName, sPackagePath):
        """
        Зарегистрировать проинсталлированный пакет в логе.
        @param sPackageName: Наименование пакета.
        @param sPackagePath: Папка пакета.
        @return: Возвращает True/False.
        """
        install_log_file = None
        try:
            if not os.path.exists(self.get_install_log_file_name()):
                self._create_install_log_file()

            install_log_file = open(self.get_install_log_file_name(), 'at')
            install_log_file.write(sPackageName.strip()+' ; '+sPackagePath.strip()+'\n')
            install_log_file.close()
            return True
        except:
            if install_log_file:
                install_log_file.close()
            raise            
        return False
    
    def get_install_package_path(self, sPackageName):
        """
        Определить путь проинсталлированного пакета по его имени.
        @param sPackageName: Наименование пакета.
        @return: Возвращает путь до папки/файла происнталлированного пакета
        или None в случае ошибки.
        """
        install_log_file = None
        try:
            if not os.path.exists(self.get_install_log_file_name()):
                log.warning('File <%s> not found!' % self.get_install_log_file_name())
                return None
            
            install_log_file = open(self.get_install_log_file_name(), 'rt')
            lines = install_log_file.readlines()
            packages = dict([(line.split(';')[0].strip(), line.split(';')[1].strip()) for line in lines])
            install_log_file.close()
            install_log_file = None
            return packages[sPackageName]
        except:
            if install_log_file:
                install_log_file.close()
            return None

    def del_install_package(self, sPackageName):
        """
        Удалить из списка проинсталлированных пакетов 
        указанный пакет по наименованию.
        @param sPackageName: Наименование пакета.
        @return: True-удаление прошло нормально,
        False-удаление по каким то причинам не прошло.
        """
        install_log_file = None
        try:
            if not os.path.exists(self.get_install_log_file_name()):
                log.warning('File <%s> not found!' % self.get_install_log_file_name())
                return False
            
            install_log_file = open(self.get_install_log_file_name(), 'rt')
            lines = install_log_file.readlines()
            packages = dict([(line.split(';')[0].strip(), line.split(';')[1].strip()) for line in lines])
            package_names = [line.split(';')[0].strip() for line in lines]
            install_log_file.close()
            install_log_file = None
            
            if sPackageName.strip() in package_names:
                del packages[sPackageName.strip()]
                return self._save_packages(packages)
            return False
        except:
            if install_log_file:
                install_log_file.close()
            raise            
        
    def _save_packages(self, dPackagesDict):
        """
        Сохранить в логе пакеты, определенные словарем пакетов.
        @param dPackageDict: Словарь пакетов:
        {
        <Наименование пакета> : <Инсталляционная папка проинсталлированного пакета>,
        ...
        }
        @return: True/False.
        """
        install_log_file = None
        try:
            install_log_file = open(self.get_install_log_file_name(), 'wt')
            for package_name, package_path in dPackagesDict.items():
                package_line = package_name+' ; '+package_path+'\n'
                install_log_file.write(package_line)
            install_log_file.close()
            install_log_file = None
            return True
        except:
            if install_log_file:
                install_log_file.close()
            raise

    def gen_install_log_file_name(self):
        """
        Сгенерировать полное имя файла install.log.
        """
        home_dir = util.get_home_path(util.get_login())
        return home_dir+'/'+INSTALLATOR_SETTINGS_DIR+'/'+INSTALL_LOG_FILE_NAME
    
    def load_packages(self):
        """
        Загрузить из лога проинсталлированные пакеты, в виде словаря пакетов.
        @param PackageDict_: Словарь пакетов:
        {
        <Наименование пакета> : <Инсталляционная папка проинсталлированного пакета>,
        ...
        }
        @return: True/False.
        """
        install_log_file = None
        try:
            install_log_file = open(self.get_install_log_file_name(), 'rt')
            lines = install_log_file.readlines()
            packages = dict([(line.split(';')[0].strip(), line.split(';')[1].strip()) for line in lines])
            install_log_file.close()
            install_log_file = None
            return packages
        except:
            if install_log_file:
                install_log_file.close()
            raise


class icInstallLogManager(icInstallLogManagerPrototype):
    """
    Регистратор инсталлированных пакетов.
    Результатом работы регистратора является текстовый файл лога install.log
    следующего формата:
    <Название пакета> ; <Инсталляционная папка проинсталлированного пакета>
    ...
     
    Например:
    icservice ; /home/baluser/programms/icservice
    Прикладная система icRegistr ; /home/baluser/programms/registr
    ...
     
    Файл install.log храниться в папке $HOME/.icinstallator.
    При инсталляции дополнительных пакетов инсталляционный файл расширяется.
    Версия пакета может кодироваться в имени пакета.
    Два пакета с одним и темже именем установить нельзя.
    """
    def __init__(self, Wizard=None):
        """
        Конструктор. 
        @param Wizard: Главный визард инсталляции.
        Управление регистратором ведется через визард.
        """
        icInstallLogManagerPrototype.__init__(self, self.gen_install_log_file_name())


class icUninstallLogManager(icInstallLogManagerPrototype):
    """
    Менеджер деинсталляции пакетов.
    Результатом работы деинсталлятора является деинсталляция пакетов,
    указанных в файле install.log и создание текстового файла
    деинсталяционного лога uninstall.log. 
    uninstall.log имеет следующий формат:
    <Дата деинсталяции> ; <Время деинсталляции> ; <Название пакета> ; <Инсталляционная папка> 
    ...
    
    Например:
    21.01.2010 ; 10:50 ; icservice ; /home/baluser/programms/icservice
    21.01.2010 ; 10:50 ; Прикладная система icRegistr ; /home/baluser/programms/registr
    ...
    
    Файл uninstall.log храниться в папке $HOME/.icinstallator      
    Менеджер удаляет из файла install.log запись деинсталлированного пакета.
    Записи в файл uninstall.log только могут добавляться.
    Удяляется файл uninstall.log вручную при необходимости.    
    """
    def __init__(self, sInstallLogFileName=None):
        """
        Конструктор.
        @param sInstallLogFileName; Имя файла инсталляционного лога.
        """
        if sInstallLogFileName is None:
            sInstallLogFileName = self.gen_install_log_file_name()
        icInstallLogManagerPrototype.__init__(self, sInstallLogFileName)
        
        self._uninstall_log_file_name = self.gen_uninstall_log_file_name()
        
    def gen_uninstall_log_file_name(self):
        """
        Сгенерировать полное имя файла uninstall.log.
        """
        if self._install_log_file_name:
            # Файл лога деинсталляции располагается там же где и инсталляционный
            # файл лога
            return os.path.dirname(self.get_install_log_file_name())+'/'+UNINSTALL_LOG_FILE_NAME
        else:
            # Стандартный файл по умолчанию
            home_dir = util.get_home_path(util.get_login())
            return home_dir+'/'+INSTALLATOR_SETTINGS_DIR+'/'+UNINSTALL_LOG_FILE_NAME
    
    def get_uninstall_log_file_name(self):
        """
        Полное имя файла install.log.
        """
        return self._uninstall_log_file_name
    
    def log_uninstall_package(self, sPackageName):
        """
        Зарегистрировать деинсталлированный пакет.
        @param sPackageName: Наименование пакета.
        @return: Возвращает True если все ок, и False если регистраия не прошла.
        """
        # Сначала выяснить какая папка была/будет деинсталлирована
        install_path = self.get_install_package_path(sPackageName)
        if install_path:
            # Если пакет с таким наименованием точно был проинсталлирован,
            # то удалить его из списка
            self.del_install_package(sPackageName)
            
            # удалить инсталляционную папку/файл физически
            self._del_package(sPackageName, install_path)
            
            # и прописать деинсталлированный пакет в логе uninstall.log
            return self._log_uninstall_package(sPackageName, install_path)
        return False
        
    def _log_uninstall_package(self, sPackageName, sPackagePath):
        """
        Зарегистрировать деинсталлированный пакет в списке unionstall.log.
        @param sPackageName: Наименование пакета.
        @param sPackagePath: Инсталляционная папка/файл пакета.
        @return: True/False.
        """
        uninstall_log_file = None
        try:
            uninstall_log_file = open(self.get_uninstall_log_file_name(), 'at')
            cur_time_sec = time.localtime(time.time())
            cur_date = time.strftime('%Y.%m.%d', cur_time_sec)
            cur_time = time.strftime('%H:%M:%S', cur_time_sec)
            uninstall_package_info = '%s ; %s : %s : %s\n' % (cur_date, cur_time,
                                                              sPackageName.strip(),
                                                              sPackagePath.strip())
            uninstall_log_file.write(uninstall_package_info)
            uninstall_log_file.close()
            uninstall_log_file = None
            return True
        except:
            if uninstall_log_file:
                uninstall_log_file.close()
            raise

    def _del_package_path(self, sPackagePath):
        """
        Удаление инсталляционной папки пакета физически.
        @param sPackagePath: Инсталляционная папка/файл пакета.
        @return: True-все ок, False-удаление не произошло по какой-то причине.
        """
        try:
            if not sPackagePath:
                return False
            path=os.path.normpath(sPackagePath)
            if os.path.exists(path):
                shutil.rmtree(path, 1)
                return True
            return False
        except:
            log.error('Delete path: <%s>' % sPackagePath)
            raise
            
    def _is_deb_package(self, sPackageName):
        """
        Является пакет DEB пакетом?
        @param dPackageName: Имя пакета.
        @return: True/False.
        """
        return sPackageName[-4:].lower() == '.deb'
    
    def _del_package(self, sPackageName, sInstallDir):
        """
        Удалить пакет.
        @param dPackageName: Имя пакета.
        @param sInstallDir: Папка инсталяции пакета.
        @return: True-все ок, False-удаление не произошло по какой-то причине.
        """
        if self._is_deb_package(sPackageName):
            # Это дебианский пакет  и удаление здесь не пойдет
            return util.deb_pkg_uninstall(sInstallDir)
        else:
            # Это обычная программа и тогда просто удаляем инсталяционную папку
            return self._del_package_path(sInstallDir)
