#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import getopt

try:
    from iccuiinstallator import config
    from iccuiinstallator.ic.utils import log
    from iccuiinstallator.ic.utils import utils
    from iccuiinstallator.ic.utils import util
except ImportError:
    import config
    from ic.utils import log
    from ic.utils import utils
    from ic.utils import util

__version__ = (0, 0, 2, 2)


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
        import packages
        packages.install_pythondialog()
    # Проверка на устанвки библиотеки urwid
    if not util.check_python_library_version('urwid'):
        import packages
        packages.install_urwid()

    try:
        from iccuiinstallator.ic.cui import install_wizard
    except ImportError:
        from ic.cui import install_wizard

    # Разбираем аргументы командной строки
    try:
        options, args = getopt.getopt(argv, 'DL',
                                      ['debug', 'log', 'dialog', 'urwid',
                                       'dosemu_dir=', 'icservices_dir=',
                                       'check=', 'uncheck='])
    except getopt.error as err:
        log.error('ERROR: %s' % err.msg, bForcePrint=True)
        sys.exit(2)

    for option, arg in options:
        if option in ('--debug', '-D'):
            utils.set_var('SERVICES_DEBUG_MODE', True)
            log.info('Install. Set DEBUG mode')
        elif option in ('--log', '-L'):
            utils.set_var('SERVICES_LOG_MODE', True)
            log.info('Install. Set LOG mode')
        elif option in ('--dialog', ):
            utils.set_var('DIALOG_MODE', 'python-dialog')
        elif option in ('--urwid', ):
            utils.set_var('DIALOG_MODE', 'urwid')
        elif option in ('--dosemu_dir',):
            config.PROGRAMM[config.DRIVE_C_SECTION]['dir'] = arg
            log.info('Set Dosemu directory <%s>' % config.PROGRAMM[config.DRIVE_C_SECTION]['dir'])
        elif option in ('--icservices_dir',):
            config.PROGRAMM[config.ICSERVICES_SECTION]['dir'] = arg
            log.info('Set icservices directory <%s>' % config.PROGRAMM[config.ICSERVICES_SECTION]['dir'])
            config.PROGRAMM[config.ICDAEMON_SECTION]['dir'] = arg
            log.info('Set icdaemon directory <%s>' % config.PROGRAMM[config.ICDAEMON_SECTION]['dir'])
        elif option in ('--check',):
            i_section = int(arg)
            config.PROGRAMM[i_section]['check'] = True
            log.info('Check section <%s>' % config.PROGRAMM[i_section].get('description', config.PROGRAMM[i_section]['name']))
        elif option in ('--uncheck',):
            i_section = int(arg)
            config.PROGRAMM[i_section]['check'] = False
            log.info('Uncheck section <%s>' % config.PROGRAMM[i_section].get('description', config.PROGRAMM[i_section]['name']))

    result = install_wizard.install(install_script, None, None)

    log.info(config.TITLE_TXT)
    return result


if __name__ == '__main__':
    import sys
    main(*sys.argv[1:])
