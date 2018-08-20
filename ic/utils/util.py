#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Дополниетельные сервисные функции.
"""

# Imports
import sys
import sysconfig
import os
import os.path
import pwd
import stat
import getpass
import shutil
import apt_pkg

from . import log

__version__ = (0, 1, 1, 1)


def who_am_i():
    """
    Имя залогиненного пользователя.
    """
    return getpass.getuser()


def is_root_user():
    """
    Проверить текущий пользователь - root?
    @return: Функция возвращает True/False.
    """
    return bool(who_am_i().lower() == 'root')


def check_python_library_version(LibName_, LibVer_=None, Compare_='=='):
    """
    Проверка установлена ли библиотека указанной версии.
    @param LibName_: Имя библиотеки, например 'wx'.
    @param LibVer_: Версия библиотеки, например '2.8.8.1'.
    @param Compare_: Оператор сравнения.
    @return: Возвращает True/False.
    """
    import_cmd = 'import '+str(LibName_)
    try:
        exec(import_cmd)
        import_lib = eval(LibName_)
    except ImportError:
        # Нет такой библиотеки
        log.error(u'Ошибка проверки установленной библиотеки <%s>' % LibName_)
        return False

    if Compare_ == '==' and LibVer_ is not None:
        # Проверка на сравнение
        log.info(u'Библиотека Python <%s> версия [%s]' % (LibName_, import_lib.__version__))
        return bool(import_lib.__version__ == LibVer_)
    elif Compare_ in ('>=', '=>') and LibVer_ is not None:
        # Проверка на больше или равно
        log.info(u'Библиотека Python <%s> версия [%s]' % (LibName_, import_lib.__version__))
        return version_compare_greate_equal(import_lib.__version__, LibVer_)
    elif Compare_ is None or LibVer_ is None:
        # Не надо проверять версию
        # достаточно того что библиотека установлена
        return True
    else:
        log.warning(u'Не поддерживаемое сравнение %s' % Compare_)
    return False


def version_compare_greate_equal(Version1_, Version2_, Delimiter_='.'):
    """
    Сравнение версий на Version1_>=Version2_.
    @param Version1_: Версия 1. В строковом виде. Например '2.8.9.2'.
    @param Version2_: Версия 2. В строковом виде. Например '2.8.10.1'.
    @param Delimiter_: Разделитель. Например точка.
    """
    ver1 = tuple([int(sub_ver) for sub_ver in Version1_.split(Delimiter_)])
    ver2 = tuple([int(sub_ver) for sub_ver in Version2_.split(Delimiter_)])
    len_ver2 = len(ver2)
    for i, sub_ver1 in enumerate(ver1):
        if i >= len_ver2:
            return True
        sub_ver2 = ver2[i]
        if sub_ver1 < sub_ver2:
            return False
        elif sub_ver1 > sub_ver2:
            return True
    return True


def check_python_labraries(**kwargs):
    """
    Проверка установленных библиотек Python.
    """
    result = True
    for lib_name, lib_ver in kwargs.items():
        result = result and check_python_library_version(lib_name, lib_ver)
    return result


def check_linux_package(PackageName_, Version_=None, Compare_='=='):
    """
    Проверка установленного пакета Linux.
    @param PackageName_: Имя пакета, например 'libgnomeprintui'
    @param Version_: Версия пакета. Если None, то версия не проверяется.\
    @param Compare_: Метод проверки версии.
    @return: True-пакет установлен, False-не установлен,
        None-система пакетов не определена.
    """
    if is_deb_linux():
        log.debug(u'ОС Linux определена как Debian совместимая')
        return check_deb_linux_package(PackageName_, Version_, Compare_)
    else:
        log.debug(u'ОС linux определена как Debian не совместимая')
    return None


def check_deb_linux_package(PackageName_, Version_=None, Compare_='=='):
    """
    Проверка установленного пакета Linux.
    @param PackageName_: Имя пакета, например 'libgnomeprintui'
    @param Version_: Версия пакета. Если None, то версия не проверяется.\
    @param Compare_: Метод проверки версии.
    @return: True-пакет установлен, False-не установлен,
        None-система пакетов не определена.
    """
    cmd = 'dpkg-query --list | grep \'ii \' | grep \'%s\'' % PackageName_
    try:
        result = os.popen3(cmd)[1].readlines()
        return bool(result)
    except:
        log.error(u'Ошибка проверки Debian инсталлируемого пакета <%s>' % cmd)
        raise
    return None


def check_deb_package_install(sPackageName):
    """
    Проверка установленн ли пакет DEB.
    @param sPackageName: Имя пакета, например 'libgnomeprintui'
    @return: True-пакет установлен, False-не установлен,
        None-система пакетов не определена.
    """
    return check_deb_linux_package(sPackageName)


def get_uname(Option_='-a'):
    """
    Результат выполнения комманды uname.
    """
    cmd = 'uname %s' % Option_
    try:
        return os.popen3(cmd)[1].readline()
    except:
        log.error(u'Ошибка выполнения комманды Uname <%s>' % cmd)
        raise
    return None


def is_64_linux():
    """
    Определить разрядность Linux.
    @return: True - 64 разрядная ОС Linux. False - нет.
    """
    uname_result = get_uname()
    return 'x86_64' in uname_result


def get_linux_name():
    """
    Определить название Linux операционной системы и версии.
    """
    try:
        if os.path.exists('/etc/issue'):
            # Обычно Debian/Ubuntu Linux
            cmd = 'cat /etc/issue'
            return os.popen3(cmd)[1].readline().replace('\\n', '').replace('\\l', '').strip()
        elif os.path.exists('/etc/release'):
            # Обычно RedHat Linux
            cmd = 'cat /etc/release'
            return os.popen3(cmd)[1].readline().replace('\\n', '').replace('\\l', '').strip()
    except:
        log.error(u'Ошибка определения названия ОС Linux')
        raise
    return None


def is_apt_package_installed(package_name):
    """
    Проверка установлен ли пакет через apt-get.
    @param package_name: Имя пакета. Например ubuntu-desktop.
    @return: True - пакет установлен. False - пакет не установлен.
    """
    apt_pkg.init_config()
    apt_pkg.init_system()
    return apt_pkg.Cache()[package_name].current_state == apt_pkg.INSTSTATE_REINSTREQ     # CURSTATE_INSTALLED


UBUNTU_DESKTOP_PACKAGE_NAME = 'ubuntu-desktop'


def is_desktop():
    """
    Проверка является ли ОС вариантом Desktop.
    Проверка производиться проверкой наличия установленного пакета ubuntu-desktop.
    @return: True - это вариант Desktop. False - нет.
    """
    return is_apt_package_installed(UBUNTU_DESKTOP_PACKAGE_NAME)


def is_linux_version(version='16.04', distrib_name='Ubuntu'):
    """
    Проверка на соответствующую версию Linux.
    @param version: Версия дистрибутива. Например: '16.04'. Также может задаваться числом.
    @param distrib_name: Наименование дистрибутива. Например: 'Ubuntu'.
    @return: True - Текущая версия Linux соответствует указанной.
        False - дистрибутив другой версии.
    """
    if isinstance(version, float) or isinstance(version, int):
        version = str(version)

    compare_str = distrib_name + ' ' + version
    linux_name = get_linux_name()
    return linux_name.startswith(compare_str)


def in_linux_versions(distrib_name='Ubuntu', versions=('16.04',)):
    """
    Проверка является ли версия Linux одной из указанных.
    @param distrib_name: Наименование дистрибутива. Например: 'Ubuntu'.
    @param versions: Список версий.
    @return: True - Текущая версия Linux соответствует указанным.
    """
    in_valid = [is_linux_version(ver, distrib_name) for ver in versions]
    return max(in_valid)


DEBIAN_LINUX_NAMES = ('Ubuntu', 'Debian', 'Mint', 'Knopix')


def is_deb_linux():
    """
    Проверка является ли дистрибутив c системой пакетов Debian.
    @return: Возвращает True/False.
    """
    linux_name = get_linux_name()
    log.debug(u'Название ОС Linux <%s>' % linux_name)
    return bool([name for name in DEBIAN_LINUX_NAMES if name in linux_name])


def is_deb_linux_uname():
    """
    Проверка является ли дистрибутив c системой пакетов Debian.
    Проверка осуществляется с помощью команды uname.
    ВНИМАНИЕ! Это не надежный способ.
    Функция переписана.
    @return: Возвращает True/False.
    """
    uname_result = get_uname()
    return (u'Ubuntu' in uname_result) or (u'Debian' in uname_result)


def get_dist_packages_path():
    """
    Путь к папке 'dist-packages' или 'site_packages'
    (в зависимости от дистрибутива) Python.
    """
    python_stdlib_path = sysconfig.get_path('stdlib')
    site_packages_path = os.path.normpath(os.path.join(python_stdlib_path, 'site-packages'))
    dist_packages_path = os.path.normpath(os.path.join(python_stdlib_path, 'dist-packages'))
    if os.path.exists(site_packages_path):
        return site_packages_path
    elif os.path.exists(dist_packages_path):
        return dist_packages_path
    return None


def create_pth_file(PthFileName_, Path_):
    """
    Создание *.pth файла в папке site_packages.
    @param PthFileName_: Не полное имя pth файла, например 'ic.pth'.
    @param Path_: Путь который указывается в pth файле.
    @return: Возвращает результат выполнения операции True/False.
    """
    pth_file = None
    try:
        dist_packages_path = get_dist_packages_path()
        pth_file_name = os.path.join(dist_packages_path, PthFileName_)
        pth_file = open(pth_file_name, 'wt')
        pth_file.write(Path_)
        pth_file.close()
        pth_file = None

        # Установить права на PTH файл
        try:
            os.chmod(pth_file_name, stat.S_IRWXO | stat.S_IRWXG | stat.S_IRWXU)
        except:
            log.error(u'Ошибка выполнения комманды Chmod в create_pth_file')
        log.info(u'Создание PTH файла <%s>. Путь <%s>' % (pth_file_name, Path_))
        return True
    except:
        if pth_file:
            pth_file.close()
            pth_file = None
        raise
    return False


def unzip_to_dir(ZipFileName_, Dir_, bOverwrite=True, bConsole=True):
    """
    Распаковать *.zip архив в папку.
    @param ZipFileName_: Полное имя *.zip архива.
    @param Dir_: Указание папки, в которую будет архив разворачиваться.
    @param bOverwrite: Перезаписать существующие файлы без запроса?
    @param bConsole: Вывод в консоль?
    @return: Возвращает результат выполнения операции True/False.
    """
    unzip_cmd = u''
    try:
        overwrite = ''
        if bOverwrite:
            overwrite = '-o'
        unzip_cmd = 'unzip %s %s -d %s' % (overwrite, ZipFileName_, Dir_)
        log.info(u'Unzip. Комманда разархивирования <%s>' % unzip_cmd)
        if bConsole:
            os.system(unzip_cmd)
            return None
        else:
            return os.popen3(unzip_cmd)
    except:
        log.error('Unzip. Ошибка разархивирования <%s>' % unzip_cmd)
        raise
    return None


CLI_PROGRESS_BAR_TOOL = '/bar-1.4/bar'


def targz_extract_to_dir(TarFileName_, Dir_, bConsole=True):
    """
    Распаковать *.tar архив в папку.
    @param TarFileName_: Полное имя *.tar архива.
    @param Dir_: Указание папки, в которую будет архив разворачиваться.
    @param bConsole: Вывод в консоль?
    @return: Возвращает результат выполнения операции True/False.
    """
    targz_extract_cmd = ''
    try:
        progress_bar = '%s%s' % (os.path.dirname(__file__), CLI_PROGRESS_BAR_TOOL)
        if os.path.exists(progress_bar):
            targz_extract_cmd = '%s %s | tar --extract --gzip --directory="%s" --file=-' % (progress_bar,
                                                                                          TarFileName_, Dir_)
        else:
            targz_extract_cmd = 'tar --extract --verbose --directory="%s" --file=%s' % (Dir_, TarFileName_)
        log.info(u'TarGz. Комманда разархивирования <%s>. Проверка наличия <%s>' % (targz_extract_cmd, os.path.exists(TarFileName_)))
        if bConsole:
            os.system(targz_extract_cmd)
            return None
        else:
            # ВНИМАНИЕ! В данном случае запуск разархивирования
            # происходит в другом процессе
            # Программа не дожидается выполнения разархивирования
            # и работает дальше. В случае с <os.system> программа
            # дожидается процесса разархивирования
            return os.popen3(targz_extract_cmd)
    except:
        log.fatal(u'TarGz. Ошибка разархивирования <%s>' % targz_extract_cmd)
        # raise
    return None


def deb_pkg_install(sDEBFileName):
    """
    Установить deb пакет.
    @param sDEBFileName: Полное имя *.deb пакета.
    @return: Возвращает результат выполнения операции True/False.
    """
    deb_install_cmd = 'dpkg --install %s' % sDEBFileName
    try:
        log.info(u'Комманда инсталяции DEB пакета <%s>. Проверка наличия <%s>' % (deb_install_cmd, os.path.exists(sDEBFileName)))
        os.system(deb_install_cmd)
        return True
    except:
        log.error(u'Ошибка инсталляции DEB пакета <%s>' % deb_install_cmd)
        raise
    return None


def deb_pkg_uninstall(sDEBPackageName):
    """
    Деинсталлировать DEB пакет.
    @param sDEBPackageName: Имя пакета. Например dosemu.
    @return: Возвращает .
    """
    deb_uninstall_cmd = u''
    try:
        if check_deb_package_install:
            deb_uninstall_cmd = 'dpkg --remove %s' % sDEBPackageName
            log.info(u'Комманда реинсталляции DEB пакета <%s>' % deb_uninstall_cmd)
            os.system(deb_uninstall_cmd)
            return deb_uninstall_cmd
        else:
            log.warning('Package <%s> not installed' % sDEBPackageName)
    except:
        log.error(u'Ошибка деинсталяции DEB пакета <%s>' % deb_uninstall_cmd)
        raise
    return None


def get_home_path(UserName_=None):
    """
    Определить домашнюю папку.
    """
    if sys.platform[:3].lower() == 'win':
        home = os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']
        home = home.replace('\\', '/')
    else:
        if UserName_ is None:
            home = os.environ['HOME']
        else:
            user_struct = pwd.getpwnam(UserName_)
            home = user_struct.pw_dir
    return home


def get_login():
    """
    Имя залогинненного пользователя.
    """
    username = os.environ.get('USERNAME', None)
    if username != 'root':
        return username
    else:
        return os.environ.get('SUDO_USER', None)


def dir_dlg(Title_='', DefaultPath_=''):
    """
    Диалог выбора каталога.
    @param Title_: Заголовок диалогового окна.
    @param DefaultPath_: Путь по умолчанию.
    """
    import wx
    app = wx.GetApp()
    result = ''
    dlg = None

    if app:
        try:
            main_win = app.GetTopWindow()

            dlg = wx.DirDialog(main_win, Title_,
                               style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)

            # Установка пути по умолчанию
            if not DefaultPath_:
                DefaultPath_ = os.getcwd()
            dlg.SetPath(DefaultPath_)
            if dlg.ShowModal() == wx.ID_OK:
                result = dlg.GetPath()
            else:
                result = ''
        finally:
            if dlg:
                dlg.Destroy()
                dlg = None

    return result


def file_dlg(Title_='', Filter_='', DefaultPath_=''):
    """
    Открыть диалог выбора файла для открытия/записи.
    @param Title_: Заголовок диалогового окна.
    @param Filter_: Фильтр файлов.
    @param DefaultPath_: Путь по умолчанию.
    @return: Возвращает полное имя выбранного файла.
    """
    import wx
    app = wx.GetApp()
    result = ''
    dlg = None

    if app:
        try:
            main_win = app.GetTopWindow()

            wildcard = Filter_+'|All Files (*.*)|*.*'
            dlg = wx.FileDialog(main_win, Title_, '', '', wildcard, wx.FD_OPEN)
            if DefaultPath_:
                dlg.SetDirectory(normpath(DefaultPath_, get_login()))
            else:
                dlg.SetDirectory(os.getcwd())

            if dlg.ShowModal() == wx.ID_OK:
                result = dlg.GetPaths()[0]
            else:
                result = ''
            dlg.Destroy()
        finally:
            if dlg:
                dlg.Destroy()

    return result


def get_dosemu_dir(UserName_=None):
    """
    Определить папку установленного dosemu.
    """
    home = get_home_path(UserName_)
    dosemu_dir = os.path.join(home, '.dosemu')
    if os.path.exists(dosemu_dir):
        return dosemu_dir

    return None


def check_dir(Dir_):
    """
    Проверить папку, если ее нет то она создается.
    """
    norm_dir = normpath(Dir_, get_login())
    if not os.path.exists(norm_dir):
        try:
            os.makedirs(norm_dir)
            return True
        except:
            log.error(u'Ошибка создания директории <%s>' % norm_dir)
            return False
    else:
        return True


def save_file_txt(FileName_, Txt_=''):
    """
    Запись текста в файл.
    @param FileName_; Имя файла.
    @param Txt_: Записываемый текст.
    @return: True/False.
    """
    file = None
    try:
        file = open(FileName_, 'wt')
        file.write(Txt_)
        file.close()
        return True
    except:
        if file:
            file.close()
        log.error(u'Ошибка сохранения текстового файла <%s>' % FileName_)
    return False


def copy_file_to(SrcFileName_, DstPath_, ReWrite_=True):
    """
    Копировать файл в указанную папку.
    @param SrcFileName_: Имя файла-источника.
    @param DstPath_: Папка-назначение.
    @param ReWrite_: Перезаписать файл, если он уже существует?
    """
    try:
        DstPath_ = normpath(DstPath_, get_login())
        if not os.path.exists(DstPath_):
            os.makedirs(DstPath_)
        dst_file_name = os.path.join(DstPath_, os.path.basename(SrcFileName_))
        if ReWrite_:
            if os.path.exists(dst_file_name):
                os.remove(dst_file_name)
        shutil.copyfile(SrcFileName_, dst_file_name)
        return True
    except:
        log.fatal(u'Ошибка копирования файла <%s> в <%s>' % (SrcFileName_, DstPath_))
        return False


def set_chown_login(sPath):
    """
    Установить владельца файла/папки залогиненного пользователя.
    @param sPath: Указание полного пути до файла/папки.
    @return: True/False.
    """
    username = get_login()
    return set_chown_user(sPath, username=username)


def set_chown_user(sPath, username):
    """
    Установить владельца файла/папки явно указанного пользователя.
    @param sPath: Указание полного пути до файла/папки.
    @param username: Наименование пользователя.
    @return: True/False.
    """
    # Сначала преобразовать путь, а потом с ним работать
    path = normpath(sPath, username)
    if not os.path.exists(path):
        # Если нет такого пути, то нечего и устанавливать
        return False
    user_struct = pwd.getpwnam(username)
    uid = user_struct.pw_uid
    gid = user_struct.pw_gid
    log.info(u'Установка владельца <%s> для директоории <%s>' % (username, path))
    return os.chown(path, uid, gid)


def set_public_chmod(sPath):
    """
    Установить свободный режим доступа (0x777) к файлу/папке.
    """
    return set_chmod(sPath, stat.S_IRWXO | stat.S_IRWXG | stat.S_IRWXU)


def set_chmod(sPath, mode=stat.S_IRWXO | stat.S_IRWXG | stat.S_IRWXU):
    """
    Установить режим доступа (по умолчанию 0x777) к файлу/папке.
    """
    path = normpath(sPath, get_login())
    if os.path.exists(path):
        # log.info(u'Set public chmod path <%s>' % path)
        os.chmod(path, mode)
        return True
    else:
        log.warning(u'Путь <%s> не найден' % path)

    return False


def set_public_chmode_tree(sPath):
    """
    Установить свободный режим доступа (0x777) к файлу/папке рекурсивно.
    """
    path = normpath(sPath, get_login())
    result = set_public_chmod(path)
    if os.path.isdir(path):
        for f in os.listdir(path):
            pathname = os.path.join(path, f)
            set_public_chmode_tree(pathname)
    return result


def set_public_chmod_tree_cmd(sPath):
    """
    Установить свободный режим доступа (0x777) к файлу/папке рекурсивно.
    Функция выполняется с помощью команды OS.
    """
    path = normpath(sPath, get_login())
    if os.path.exists(path):
        try:
            # if isinstance(path, unicode):
            #    path = path.encode(sys.getfilesystemencoding())
            cmd = 'sudo chmod --recursive 777 "%s"' % path
            log.info(u'Запуск комманды ОС <%s>' % cmd)   # sys.getfilesystemencoding()))
            os.system(cmd)
            return True
        except:
            log.fatal(u'Ошибка установки прав доступа')
    else:
        log.warning(u'Путь <%s> не найден' % path)
    return False


def sym_link(sLinkPath, sLinkName, sUserName=None, bOverwrite=True):
    """
    Создать символическую ссылку.
    @param sLinkPath: На что ссылается ссылка.
    @param sLinkName: Имя ссылки.
    @param sUserName: Имя пользователя.
    @param bOverwrite: Перезаписать ссылку, если она существует?
    """
    username = sUserName
    if username is None:
        username = get_login()
    link_path = normpath(sLinkPath, username)
    link_name = normpath(sLinkName, username)

    if os.path.exists(link_name) and bOverwrite:
        # Перезаписать?
        os.remove(link_name)
    try:
        return os.symlink(link_path, link_name)
    except:
        log.error(u'Ошибка создания символической ссылки <%s> -> <%s>' % (link_name, link_path))
    return None


def get_options(lArgs=None):
    """
    Преобразование параметров коммандной строки в словарь python.
    Параметры коммандной строки в виде --ключ=значение.
    @param lArgs: Список строк параметров.
    @return: Словарь значений или None в случае ошибки.
    """
    if lArgs is None:
        lArgs = sys.argv[1:]

    opts = {}
    args = []
    while lArgs:
        if lArgs[0][:2] == '--':
            if '=' in lArgs[0]:
                # поиск пар "--name=value"
                i = lArgs[0].index('=')
                opts[lArgs[0][:i]] = lArgs[0][i+1:]     # ключами словарей будут имена параметров
            else:
                # поиск "--name"
                opts[lArgs[0]] = True   # ключами словарей будут имена параметров
        else:
            args.append(lArgs[0])
        lArgs = lArgs[1:]
    return opts, args


def normpath(path, sUserName=None):
    """
    Нормировать путь.
    @param path: Путь.
    @param sUserName: Имя пользователя.
    """
    home_dir = get_home_path(sUserName)
    return os.path.abspath(os.path.normpath(path.replace('~', home_dir)))


def text_file_append(sTextFileName, sText, CR='\n'):
    """
    Добавить строки в текстовый файл.
    @param sTextFileName: Имя текстового файла.
    @param sText: Добавляемый текст.
    @param CR: Символ возврата каретки.
    @return: True/False.
    """
    txt_filename = normpath(sTextFileName, get_login())
    if os.path.exists(txt_filename):
        f = None
        try:
            f = open(txt_filename, 'rt')
            txt = f.read()
            txt += CR
            txt += sText
            log.debug(u'Добавление текста <%s> к файлу <%s>' % (sText, txt_filename))
            f.close()
            f = None
            f = open(txt_filename, 'wt')
            f.write(txt)
            f.close()
            f = None
            return True
        except:
            log.error(u'Ошибка добавления текста к файлу <%s>' % txt_filename)
            if f:
                f.close()
                f = None
    else:
        log.warning(u'Файл <%s> не существует' % txt_filename)
    return False


def text_file_replace(sTextFileName, sOld, sNew, bAutoAdd=True, CR='\n'):
    """
    Замена строки в текстовом файле.
    @param sTextFileName: Имя текстового файла.
    @param sOld: Старая строка.
    @param sNew: Новая строка.
    @param bAutoAdd: Признак автоматического добавления новой строки.
    @param CR: Символ возврата каретки.
    @return: True/False.
    """
    txt_filename = normpath(sTextFileName, get_login())
    if os.path.exists(txt_filename):
        f = None
        try:
            f = open(txt_filename, 'rt')
            txt = f.read()
            txt = txt.replace(sOld, sNew)
            if bAutoAdd and (sNew not in txt):
                txt += CR
                txt += sNew
                log.debug(u'Замена текста на <%s> в файле <%s>' % (sNew, txt_filename))
            f.close()
            f = None
            f = open(txt_filename, 'wt')
            f.write(txt)
            f.close()
            f = None
            return True
        except:
            log.error(u'Ошибка замены в текстовом файле <%s>' % txt_filename)
            if f:
                f.close()
                f = None
    else:
        log.warning(u'Файл <%s> не существует' % txt_filename)
    return False


def text_file_find(sTextFileName, sFind, sFindMethod='in'):
    """
    Поиск строки в текстовом файле.
    @param sTextFileName: Имя текстового файла.
    @param sFind: Сирока поиска.
    @param sFindMethod: Метод поиска подстроки:
        'in' - просто поиск подстроки в текущей строке
        'startswith' - поиск подстроки в начале текущей строки
        'endswith' - поиск подстроки в конце текущей строки
    @return: True/False.
    """
    txt_filename = normpath(sTextFileName, get_login())
    if os.path.exists(txt_filename):
        f = None
        try:
            f = open(txt_filename, 'rt')
            txt = f.read()
            result = False
            if sFindMethod == 'in':
                result = sFind in txt
            elif sFindMethod == 'startswith':
                result = txt.startswith(sFind)
            elif sFindMethod == 'endswith':
                result = txt.endswith(sFind)
            f.close()
            f = None
            return result
        except:
            log.error(u'Ошибка поиска <%s> в текстовом файле <%s>' % (sFind, txt_filename))
            if f:
                f.close()
                f = None
    else:
        log.warning(u'Файл <%s> не существует' % txt_filename)
    return False


def text_file_subreplace(sTextFileName, sSubStr, sNew, bAutoAdd=True, CR='\n', sFindMethod='in'):
    """
    Замена строки в текстовом файле с поиском подстроки.
    @param sTextFileName: Имя текстового файла.
    @param sSubStr: Под строка  выявления строки замены.
    @param sNew: Новая строка.
    @param bAutoAdd: Признак автоматического добавления новой строки.
    @param CR: Символ возврата каретки.
    @param sFindMethod: Метод поиска подстроки:
        'in' - просто поиск подстроки в текущей строке
        'startswith' - поиск подстроки в начале текущей строки
        'endswith' - поиск подстроки в конце текущей строки
    @return: True/False.
    """
    txt_filename = normpath(sTextFileName, get_login())
    if os.path.exists(txt_filename):
        f = None
        try:
            f = open(txt_filename, 'rt')
            lines = f.readlines()
            is_replace = False
            for i, line in enumerate(lines):
                if sFindMethod == 'in' and sSubStr in line:
                    lines[i] = sNew
                    is_replace = True
                elif sFindMethod == 'startswith' and line.startswith(sSubStr):
                    lines[i] = sNew
                    is_replace = True
                elif sFindMethod == 'endswith' and line.endswith(sSubStr):
                    lines[i] = sNew
                    is_replace = True

                if is_replace:
                    log.debug(u'Замена <%s> -> <%s> в текстовом файле <%s>' % (line, sNew, txt_filename))
            if bAutoAdd and not is_replace:
                lines += [CR]
                lines += [sNew]
                log.debug(u'Добавление <%s> в текстовом файле <%s>' % (sNew, txt_filename))
            f.close()
            f = None
            f = open(txt_filename, 'w')
            f.writelines(lines)
            f.close()
            f = None
            return True
        except:
            log.error(u'Ошибка замены в текстовом файле <%s>' % txt_filename)
            if f:
                f.close()
                f = None
    else:
        log.warning(u'Файл <%s> не существует' % txt_filename)
    return False


def text_file_subdelete(sTextFileName, sSubStr, sFindMethod='in'):
    """
    Удаление строки в текстовом файле с поиском подстроки.
    @param sTextFileName: Имя текстового файла.
    @param sSubStr: Под строка  выявления строки удаления.
    @param sFindMethod: Метод поиска подстроки:
        'in' - просто поиск подстроки в текущей строке
        'startswith' - поиск подстроки в начале текущей строки
        'endswith' - поиск подстроки в конце текущей строки
    @return: True/False.
    """
    txt_filename = normpath(sTextFileName, get_login())
    if os.path.exists(txt_filename):
        f = None
        try:
            result_lines = []
            f = open(txt_filename, 'rt')
            lines = f.readlines()
            for line in lines:
                if sFindMethod == 'in' and sSubStr not in line:
                    result_lines.append(line)
                elif sFindMethod == 'startswith' and not line.startswith(sSubStr):
                    result_lines.append(line)
                elif sFindMethod == 'endswith' and not line.endswith(sSubStr):
                    result_lines.append(line)
                else:
                    log.debug('Text file delete line <%s> from <%s>' % (line, txt_filename))
            f.close()
            f = None
            f = open(txt_filename, 'wt')
            f.writelines(result_lines)
            f.close()
            f = None
            return True
        except:
            log.error(u'Ошибка удаления в текстовом файле <%s>' % txt_filename)
            if f:
                f.close()
                f = None
    else:
        log.warning(u'Файл <%s> не существует' % txt_filename)
    return False


def text_file_subdelete_between(sTextFileName, sSubStrStart, sSubStrStop, sFindMethod='in'):
    """
    Удаление строк в текстовом файле, находящихся между подстрок.
    @param sTextFileName: Имя текстового файла.
    @param sSubStrStart: Подстрока сигнатуры выявления первой строки удаления.
    @param sSubStrStop: Подстрока сигнатуры выявления последней строки удаления.
    @param sFindMethod: Метод поиска подстроки:
        'in' - просто поиск подстроки в текущей строке
        'startswith' - поиск подстроки в начале текущей строки
        'endswith' - поиск подстроки в конце текущей строки
    @return: True/False.
    """
    txt_filename = normpath(sTextFileName, get_login())
    if os.path.exists(txt_filename):
        f = None
        del_flag = False
        try:
            result_lines = []
            f = open(txt_filename, 'rt')
            lines = f.readlines()
            for line in lines:
                if sFindMethod == 'in' and sSubStrStart in line:
                    del_flag = True
                elif sFindMethod == 'startswith' and line.startswith(sSubStrStart):
                    del_flag = True
                elif sFindMethod == 'endswith' and line.endswith(sSubStrStart):
                    del_flag = True

                if not del_flag:
                    result_lines.append(line)
                else:
                    log.debug(u'Удаление строки <%s> из текстового файла <%s>' % (line, txt_filename))

                if sFindMethod == 'in' and sSubStrStop in line:
                    del_flag = False
                elif sFindMethod == 'startswith' and line.startswith(sSubStrStop):
                    del_flag = False
                elif sFindMethod == 'endswith' and line.endswith(sSubStrStop):
                    del_flag = False

                f.close()
            f = None
            f = open(txt_filename, 'wt')
            f.writelines(result_lines)
            f.close()
            f = None
            return True
        except:
            log.fatal(u'Ошибка удаления из текстового файла <%s>' % txt_filename)
            if f:
                f.close()
                f = None
    else:
        log.warning(u'Файл <%s> не существует' % txt_filename)
    return False


INSTALL_PACKAGES_DIR_DEFAULT = '/packages/'

# Режимы доступа к инсталлируемым файлам/папкам
PUBLIC_MODE = 'public'
PROTECT_MODE = 'protect'


def install_programm(dProgramm=None, LogManager=None):
    """
    Запуск инсталяции программы.
    @param Programm_: Структура описания инсталируемой программы.
    @param LogManager: Менеджер журналирования инсталляции.
    @return: True/False
    """
    if dProgramm is None:
        log.warning(u'Не определены програмы для инсталляции')
        return False

    # Имя программы
    prg_name = dProgramm.get('programm', dProgramm.get('name', '-'))

    # Не инсталлировать уже инсталлированные пакеты
    is_installed = LogManager.is_installed_package(prg_name) if LogManager else False
    log.info(u'Инсталляция <%s> ... %s' % (prg_name, not is_installed))
    if not is_installed:

        install_dir = os.getcwd()

        if 'dir' in dProgramm:
            if dProgramm['dir'] is None:
                install_dir = os.path.join(get_temp_dir(), prg_name)
                log.warning(u'Не определена инсталляционная директория. Используется <%s>' % install_dir)
            else:
                install_dir = normpath(dProgramm['dir'])
                log.debug(u'Установка инсталляционной директории <%s>' % install_dir)

        # Если перед инсталяцией инсталляционная папка определена
        # но такой папки на диске не , то создать ее
        if install_dir and not os.path.exists(install_dir):
            log.info(u'Создание инсалляционной директории <%s>' % install_dir)
            os.makedirs(install_dir)

        # Определить папку пакета
        package_dir = install_dir
        if 'package_dir' in dProgramm:
            package_dir += '/'+dProgramm['package_dir']
            # если папка пакета уже существует, то удалить ее
            if os.path.exists(package_dir):
                log.info(u'Удаление директории пакета <%s>' % package_dir)
                shutil.rmtree(package_dir, 1)

        if dProgramm.get('programm', None) is None:
            log.warning(u'Не определенн инсталляционный пакет программы <%s>' % prg_name)
        elif dProgramm['programm'][-4:].lower() == '.zip':
            # Разархивировать ZIP файл
            unzip_programm(dProgramm)
        elif dProgramm['programm'][-7:].lower() == '.tar.gz':
            # Разархивировать .tar.gz файл
            targz_extract_programm(dProgramm)
        elif dProgramm['programm'][-4:].lower() == '.deb':
            deb_install_programm(dProgramm)
            # Т.к. DEB пакеты не деинсталлируются удалением, то вместо директории
            # пакета указываем имя пакета, которое потом будет использоваться
            # в dpkg --remove комманде
            package_dir = dProgramm['name']

        if 'mode' in dProgramm:
            if dProgramm['mode'].lower() == PUBLIC_MODE:
                # Если режим установлен, как публичный, то установить режим для
                # инсталляционной папки и поменять владельца на залогинненного
                set_chown_login(install_dir)
                set_public_chmod(install_dir)

        # Если нужно, то создать pth файл
        if 'pth' in dProgramm:
            create_pth_file_programm(dProgramm['pth'], install_dir)

        if LogManager:
            LogManager.log_install_package(prg_name, package_dir)
        return True
    return False


def create_pth_file_programm(dPth, sInstallDir):
    """
    Создать pth файл.
    @param dPth: Структура:
        {
            'name':'имя генерируемого pth-файла',
            'dir':'указание папки, которую содержит pth-файл',
            'var':'пересенная из окружения визарда, которая содержит путь до папки',
        }
    """
    if dPth['dir'] is None:
        dPth['dir'] = os.path.normpath(os.path.join(sInstallDir, dPth.get('package', '')))

    return create_pth_file(dPth['name'], dPth['dir'])


def remove_programm(dProgramm=None):
    """
    Произвести дополнительные удаления перед установкой.
    """
    if 'remove' in dProgramm:
        for remove_name in dProgramm['remove']:
            if os.path.exists(remove_name):
                if os.path.isfile(remove_name):
                    log.info(u'Удаление файла <%s>' % remove_name)
                    os.remove(remove_name)
                elif os.path.isdir(remove_name):
                    log.info(u'Удаление директории <%s>' % remove_name)
                    shutil.rmtree(remove_name)
            elif os.path.sep not in remove_name:
                # Если нет разделителей папок в имени, значит это указание
                # DEB пакета
                cmd = deb_pkg_uninstall(remove_name)
                log.info(u'Деинсталяция DEB пакета <%s>. Комманда <%s>' % (remove_name, cmd))
            else:
                log.warning(u'Не удален <%s>' % remove_name)


def unzip_programm(dProgramm=None, sPackageDir=INSTALL_PACKAGES_DIR_DEFAULT):
    """
    Распаковать zip архив.
    """
    if dProgramm is None:
        log.warning(u'Unzip. Не определен пакет дял разархивирования')
        return False

    remove_programm(dProgramm)

    install_dir = None
    if 'dir' in dProgramm:
        install_dir = dProgramm['dir']
    if install_dir is None:
        log.warning(u'Unzip. Не определена инсталяционная директория для пакета <%s>' % dProgramm.get('name', None))
        return False

    # Если инсталляционной папки нет, то создать ее
    if install_dir and not os.path.exists(install_dir):
        log.info(u'Создание инсталляционной директории <%s>' % install_dir)
        os.makedirs(install_dir)

    zip_file_name = normpath(os.path.join('.', sPackageDir, dProgramm['programm']))

    console = dProgramm.get('console', True)
    return unzip_to_dir(zip_file_name, install_dir, bConsole=console)


def targz_extract_programm(dProgramm=None, sPackageDir=INSTALL_PACKAGES_DIR_DEFAULT):
    """
    Распаковать tar архив.
    """
    if dProgramm is None:
        log.warning(u'Targz. Не определен пакет для разархивирования')
        return False

    remove_programm(dProgramm)

    install_dir = None
    if 'dir' in dProgramm:
        install_dir = normpath(dProgramm['dir'])
    if install_dir is None:
        log.warning(u'Targz. Не определена инсталляционная директория для пакета <%s>' % dProgramm.get('name', None))
        return False

    # Если инсталляционной папки нет, то создать ее
    if install_dir and not os.path.exists(install_dir):
        log.info(u'Создание инсталляционной директории <%s>' % install_dir)
        os.makedirs(install_dir)

    tar_file_name = normpath(os.path.join('.', sPackageDir, dProgramm['programm']))

    console = dProgramm.get('console', True)
    return targz_extract_to_dir(tar_file_name, install_dir, bConsole=console)


def deb_install_programm(dProgramm=None, sPackageDir=INSTALL_PACKAGES_DIR_DEFAULT):
    """
    Установить DEB пакет.
    """
    if dProgramm is None:
        log.warning(u'Deb. Не определен пакет для инсталляции')
        return False

    # Если необходимо. то деинсталлировать пакеты
    remove_programm(dProgramm)

    deb_file_name = normpath(os.path.join('.', sPackageDir, dProgramm['programm']))

    return deb_pkg_install(deb_file_name)


def uninstall_programms(lProgramms=None, LogManager=None):
    """
    Метод деинсталляции выбранных программ/пакетов.
    @param lProgramms: Структура описания деинсталируемых программ.
    @param LogManager: Менеджер журналирования инсталляции.
    @return: True/False.
    """
    if lProgramms is None:
        log.warning(u'Не определены пакеты для деинсталляции')
        return False

    uninstalled_programms = []
    for i, programm in enumerate(lProgramms):
        ok = uninstall_programm(programm, LogManager)
        uninstalled_txt = programm.get('programm', 'programm_%d' % i)+'...'+('YES' if ok else 'NO')
        uninstalled_programms.append(uninstalled_txt)

    # В конце вывести сообщение об деинстллированных пакетах
    txt = '\n'.join(uninstalled_programms)
    log.info(u'Деинсталяция пакетов:')
    log.info(txt)
    return True


def uninstall_programm(dProgramm=None, LogManager=None):
    """
    Метод деинсталляции выбранных программ/пакетов.
    @param dProgramm: Структура описания деинсталируемой программы.
    @param LogManager: Менеджер журналирования инсталляции.
    @return: True/False.
    """
    if dProgramm is None:
        log.warning(u'Не определен пакет для деинсталяции')
        return False

    # Имя программы
    prg_name = dProgramm.get('programm', dProgramm.get('name', '-'))

    if 'dir' in dProgramm:
        ok = LogManager.log_uninstall_package(prg_name) if LogManager else False
        yes_no = 'YES' if ok else 'NO'
        programm_name = dProgramm.get('programm', dProgramm.get('description', prg_name))
        log.info(u'Деинсталяция пакета <%s> ... %s' % (programm_name, yes_no))
        return ok
    return False


def exec_sys_command(sCommand):
    """
    Функция выполнения команды ОС.
    @param sCommand: Текст команды.
    """
    try:
        os.system(sCommand)
        log.info(u'Выполнение команды ОС <%s>' % sCommand)
    except:
        log.error(u'Ошибка выполнения команды %s' % sCommand)
        raise


def targz_install_python_package(targz_package_filename=None):
    """
    Установить Python пакет в виде tar.gz архива.
    @param targz_package_filename: Имя файла архива поставки Python пакета.
    @return: True/False.
    """
    if not targz_package_filename:
        log.warning(u'Targz. Не определен файл пакета TARGZ python для инсталяции')
        return False

    if not os.path.exists(targz_package_filename):
        log.warning(u'Не существует <%s> файл python пакета' % targz_package_filename)
        return False

    log.info(u'Запуск инсталляции python пакета. Имя файла TarGz <%s>' % targz_package_filename)

    pkg_dir = os.path.dirname(targz_package_filename)
    set_public_chmod(pkg_dir)
    targz_extract_to_dir(targz_package_filename, pkg_dir)

    targz_basename = os.path.splitext(os.path.basename(targz_package_filename))[0]
    setup_dir = os.path.normpath(os.path.join(pkg_dir, targz_basename))
    setup_filename = os.path.normpath(os.path.join(setup_dir, 'setup.py'))
    if os.path.exists(setup_filename):
        cmd = 'cd %s; sudo python setup.py install' % setup_dir
        log.info(u'Инсталяция библиотеки <%s>. Команда <%s>' % (targz_basename, cmd))
        os.system(cmd)
        # Удалить после инсталляции распакованный архив
        if os.path.exists(setup_dir):
            cmd = 'sudo rm -R %s' % setup_dir
            log.info(u'Удаление директории <%s>. Комманда <%s>' % (setup_dir, cmd))
            os.system(cmd)
        return True
    else:
        log.warning(u'Не существует setup.py файл <%s>' % setup_filename)
    return False


def get_temp_dir():
    """
    Определение временной директории.
    """
    return os.path.dirname(os.tempnam())


def check_section(prg_list, section, check=True):
    """
    Установка отметки секции для инсталляции.
    @param prg_list: Список секций.
    @param section: Указание секции.
        Секция может задаваться как индекс в списке описаний, так и по имени секции
    @param check: True - Ставить отметку. False - убрать отметку.
    @return: Измененный список секций.
    """
    i_section = None
    if isinstance(section, int):
        # Секция задается индексом
        i_section = section
    else:
        # Секция задается именем
        section_names = [section_dict['name'] for section_dict in prg_list]
        if section in section_names:
            i_section = section_names.index(section)
    if i_section is not None:
        prg_list[i_section]['check'] = check
        if check:
            log.info(u'[v] Вкл. секции <%s>' % prg_list[i_section].get('description', prg_list[i_section]['name']))
        else:
            log.info(u'[ ] Выкл. секции <%s>' % prg_list[i_section].get('description', prg_list[i_section]['name']))
    else:
        log.warning(u'Ошибка определения секции <%s>' % str(section))

    return prg_list


def test():
    """
    Функция тестирования.
    """
    result = get_options(['--dosemu=/home/user/.dosemu', '--option2', 'aaaa'])


if __name__ == '__main__':
    test()
