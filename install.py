#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import getopt

try:
    from . import config
    from .ic.utils import log
    from .ic.utils import utils
    from .ic.utils import util
except Exception:
    import config
    from ic.utils import log
    from ic.utils import utils
    from ic.utils import util


__version__ = (0, 1, 1, 1)


def install_script(wizard):
    """
    Функция основного инсталяционного скрипта.
    @param Wizard_: Объект главного визарда. Он создается в
    запускающей функции run/install.
    """
    from ic.cui import install_pages

    # Проверка запуска под рутом
    is_root = wizard.check_root()
    if not is_root:
        return False

    # Проверка установленных пакетов и их версий
    install_pages.add_wizard_package_control_page(wizard, config.PACKAGES)

    install_pages.add_wizard_programm_install_page(wizard, config.PROGRAMM)
    return True


def main(*argv):
    """
    Главноя функция запуска инсталляции.
    В качестве ключей могут быть параметры инсталяции.

    [Параметры]
        --debug             - включить все сервисы в режиме отладки
        --log               - включить все сервисы в режиме журналирования

        --dialog            - включить режим диалогов pythondialogs
        --urwid             - включить режим диалогов urwid (по умолчанию)

        --dosemu_dir=       - папка инсталляции dosemu
        --icservices_dir=   - папка инсталляции icservices

        --check=            - отметить секцию для установки
        --uncheck=          - снять отметку секции для установки
    """
    log.init(config)

    log.info(config.TITLE_TXT)

    # Проверка устанувки библиотеки pythondialog
    if not util.check_python_library_version('dialog'):
        from . import packages
        packages.install_pythondialog()
    # Проверка на устанвки библиотеки urwid
    if not util.check_python_library_version('urwid'):
        from . import packages
        packages.install_urwid()

    try:
        from .ic.cui import install_wizard
    except Exception:
        from ic.cui import install_wizard

    # Разбираем аргументы командной строки
    try:
        options, args = getopt.getopt(argv, 'DL',
                                      ['debug', 'log', 'dialog', 'urwid',
                                       'dosemu_dir=', 'icservices_dir=',
                                       'check=', 'uncheck='])
    except getopt.error as err:
        log.error(u'Ошибка параметров коммандной строки %s' % err.msg, bForcePrint=True)
        log.warning(__doc__, bForcePrint=True)
        sys.exit(2)

    for option, arg in options:
        if option in ('--debug', '-D'):
            utils.set_var('SERVICES_DEBUG_MODE', True)
            log.info(u'Инсталяция. Установка режима отладки')
        elif option in ('--log', '-L'):
            utils.set_var('SERVICES_LOG_MODE', True)
            log.info(u'Инсталяция. Установка режима журналирования')
        elif option in ('--dialog', ):
            utils.set_var('DIALOG_MODE', 'python-dialog')
        elif option in ('--urwid', ):
            utils.set_var('DIALOG_MODE', 'urwid')
        elif option in ('--dosemu_dir',):
            config.PROGRAMM[config.DRIVE_C_SECTION]['dir'] = arg
            log.info(u'Dosemu директория <%s>' % config.PROGRAMM[config.DRIVE_C_SECTION]['dir'])
        elif option in ('--icservices_dir',):
            config.PROGRAMM[config.ICSERVICES_SECTION]['dir'] = arg
            log.info(u'icservices директория <%s>' % config.PROGRAMM[config.ICSERVICES_SECTION]['dir'])
            config.PROGRAMM[config.ICDAEMON_SECTION]['dir'] = arg
            log.info(u'icdaemon директория <%s>' % config.PROGRAMM[config.ICDAEMON_SECTION]['dir'])
        elif option in ('--check',):
            section = int(arg) if arg.isdigit() else arg
            config.PROGRAMM = util.check_section(config.PROGRAMM, section, True)

        elif option in ('--uncheck',):
            section = int(arg) if arg.isdigit() else arg
            config.PROGRAMM = util.check_section(config.PROGRAMM, section, False)

    result = install_wizard.install(install_script, None, None)

    log.info(config.TITLE_TXT)
    return result


if __name__ == '__main__':
    import sys
    main(*sys.argv[1:])
