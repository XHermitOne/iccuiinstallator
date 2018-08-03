#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

import getopt

try:
    from iccuiinstallator import config
    from iccuiinstallator.ic.utils import utils
    from iccuiinstallator.ic.utils import log
except ImportError:
    import config
    from ic.utils import utils
    from ic.utils import log


def uninstall(*argv):
    """
    Главноя функция запуска деинсталляции.
    В качестве ключей могут быть параметры деинсталляции.

    [Параметры]
        --debug             - включить все сервисы в режиме отладки
        --log               - включить все сервисы в режиме журналирования

        --dialog            - включить режим диалогов pythondialogs
        --urwid             - включить режим диалогов urwid (по умолчанию)
    """
    log.init(config)
    log.info(config.TITLE_TXT)

    try:
        from iccuiinstallator.ic.cui import install_wizard
    except ImportError:
        from ic.cui import install_wizard

    # Разбираем аргументы командной строки
    try:
        options, args = getopt.getopt(argv, 'DL',
                                      ['debug', 'log', 'dialog', 'urwid'])
    except getopt.error, msg:
        log.error('ERROR: %s' % msg)
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

    result = install_wizard.uninstall(dProgramms=config.UNINSTALL_PROGRAMM)
    log.info(config.TITLE_TXT)

    return result


if __name__ == '__main__':
    import sys
    uninstall(*sys.argv[1:])
