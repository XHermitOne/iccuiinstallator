#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
Консольный визард.
"""

try:
    from iccuiinstallator import config
    from iccuiinstallator.ic.utils import log
except ImportError:
    import config
    from ic.utils import log

__version__ = (0, 1, 1, 1)

NEXT_PAGE_CODE = 1
PREV_PAGE_CODE = -1
CANCEL_PAGE_CODE = 2
FINISH_PAGE_CODE = 0


class icCUIWizard:
    """
    Консольный визард.
    """
    def __init__(self, sTitle, *args, **kwargs):
        """
        Конструктор.
        @param sTitle: Заголовок визарда.
        """
        self.title = sTitle
        
        # Список порядка следования страниц
        self.pages = []
        
        # Сценарий исполнения
        self.scenario = []
        # Альтернативная функция обработка сценариев
        self.do_scenario = None

    def _initPage(self, Page):
        """
        Инициализировать кнопки страницы.
        """
        if Page.getNext() is None:
            buttons = [(u'Пред', PREV_PAGE_CODE),
                       (u'Отмена', CANCEL_PAGE_CODE),
                       (u'OK', FINISH_PAGE_CODE)]
        if Page.getPrev() is None:
            buttons = [(u'След', NEXT_PAGE_CODE),
                       (u'Отмена', CANCEL_PAGE_CODE)]
        if Page.getPrev() is None and Page.getNext() is None:
            buttons = [(u'Отмена', CANCEL_PAGE_CODE),
                       (u'OK', FINISH_PAGE_CODE)]
        if Page.getPrev() is not None and Page.getNext() is not None:
            buttons = [(u'Пред', PREV_PAGE_CODE),
                       (u'След', NEXT_PAGE_CODE),
                       (u'Отмена', CANCEL_PAGE_CODE)]
            
        Page.add_buttons(buttons)
        
    def appendPage(self, Page):
        """
        Установка следующей страницы.
        """
        if Page:
            if self.pages:
                # Установить связи между страницами
                Page.setPrev(self.pages[-1])
                self.pages[-1].setNext(Page)
            self.pages.append(Page)
            # Пересоздать кнопки на страницах
            for page in self.pages:
                self._initPage(page)
        
    def runFirstPage(self):
        """
        Запуск первой страницы.
        """
        if self.pages:
            first_page = self.pages[0]
            if first_page:
                code = self.runWizard(first_page)
                log.debug(u'Результирующий код <%s>' % code)
                if code == FINISH_PAGE_CODE or code is True:
                    # Нажата кнопка <OK>
                    # Сохранить настройки
                    self.saveSettings()
                    # Запустить сценарий на исполнение
                    return self.doScenario()
                else:
                    # Нажата кнопка <Cancel>
                    pass
        return False
        
    def runWizard(self, Page):
        """
        Запуск визарда с указанной страницы.
        """
        code = CANCEL_PAGE_CODE
        if Page:
            code = Page.main()
            while code in (PREV_PAGE_CODE, NEXT_PAGE_CODE, True):

                log.debug(u'Страница %s. Результирующий код <%s>' % (Page.__class__.__name__, code))

                if code == PREV_PAGE_CODE:
                    Page.delScenarioScript()
                    Page = Page.getPrev()                    
                elif code == NEXT_PAGE_CODE:
                    Page.addScenarioScript()
                    Page = Page.getNext()
                elif code is True:
                    Page.addScenarioScript()
                    Page = Page.getNext()
                if Page:
                    code = Page.main()
                else:
                    code = FINISH_PAGE_CODE
            if code == FINISH_PAGE_CODE or code is True:
                if Page:
                    Page.addScenarioScript()
        return code
        
    def doScenario(self, lScenario=None):
        """
        Функция выполнения сценария.
        @param lScenario: Сценарий-список шагов сценария.
            Основным элементом визарда является сценарий:
            Сценарий - это список кортежей:
            [(Идентификатор,
            Функция обработки шага сценария,
            Аргументы,
            Именованные аргументы),
            ...]
            Исполнение сценария запускается по кнопке 
            <OK> на последней странице визарда.
        """
        if lScenario is None:
            lScenario = self.scenario
        
        # Проверить определена ли альтернативная функция обработки сценария
        if self.do_scenario:
            return self.do_scenario(lScenario)
        else:
            result = True
            # обработка сценария по шагам
            for step in lScenario:
                if step:
                    id = step[0]
                    func = step[1]
                    args = step[2]
                    kwargs = step[3]
                    enable = step[4]
                    if func and enable:
                        try:
                            log.info(u'Выполнение сценария %s args: %s kwargs: %s' % (func.__name__, args, kwargs))
                            step_result = func(*args, **kwargs)
                        except:
                            log.fatal(u'Ошибка выполнения функции сценария <%s>' % func)
                            step_result = False
                            if config.DEBUG_MODE:
                                raise
                        
                        result = result and step_result
            return result
        
    def addScenarioScript(self, sName, fFunc, tArgs, dKWArgs, bEnable=True):
        """
        Добавить скрипт сценария в  сценария.
        """
        script = sName, fFunc, tArgs, dKWArgs, bEnable
        self.scenario.append(script)


def test():
    wiz = icCUIWizard()
    wiz.main()


if __name__ == '__main__':
    test()
