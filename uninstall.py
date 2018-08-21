#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

import copy
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


def uninstall(*argv):
    """
    Главноя функция запуска деинсталляции.
    В качестве ключей могут быть параметры деинсталляции.

    [Параметры]
        --debug             - включить все сервисы в режиме отладки
        --log               - включить все сервисы в режиме журналирования

        --dialog            - включить режим диалогов pythondialogs
        --urwid             - включить режим диалогов urwid (по умолчанию)

        --check=            - отметить секцию для установки
        --uncheck=          - снять отметку секции для установки
    """
    log.init(config)
    log.info(config.TITLE_TXT)

    try:
        from .ic.cui import install_wizard
    except Exception:
        from ic.cui import install_wizard

    # Разбираем аргументы командной строки
    try:
        options, args = getopt.getopt(argv, 'DL',
                                      ['debug', 'log', 'dialog', 'urwid',
                                       'check=', 'uncheck='])
    except getopt.error as msg:
        log.error(u'Ошибка параметров коммандной строки %s' % str(msg), bForcePrint=True)
        log.warning(__doc__, bForcePrint=True)
        sys.exit(2)

    programms = copy.deepcopy(config.UNINSTALL_PROGRAMM)

    for option, arg in options:
        if option in ('--debug', '-D'):
            utils.set_var('SERVICES_DEBUG_MODE', True)
            log.info(u'Деинсталяция. Установка режима отладки')
        elif option in ('--log', '-L'):
            utils.set_var('SERVICES_LOG_MODE', True)
            log.info('Деинсталяция. Установка режима журналирования')
        elif option in ('--dialog', ):
            utils.set_var('DIALOG_MODE', 'python-dialog')
        elif option in ('--urwid', ):
            utils.set_var('DIALOG_MODE', 'urwid')

        elif option in ('--check',):
            section = int(arg) if arg.isdigit() else arg
            programms = util.check_section(programms, section, True)

        elif option in ('--uncheck',):
            section = int(arg) if arg.isdigit() else arg
            programms = util.check_section(programms, section, False)

    result = install_wizard.uninstall(dProgramms=programms)
    log.info(config.TITLE_TXT)

    return result


if __name__ == '__main__':
    import sys
    uninstall(*sys.argv[1:])
