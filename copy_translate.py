from threading import Thread
from typing import Optional

from copy_listener import CopyListenerFactory
from gui import Widget
from translator import *


class CopyTranslator(object):
    def __init__(self, translators: list, interval: float):
        self.translators: list[Translator] = translators
        self.listener = CopyListenerFactory.newCopyListener()
        self.interval = interval
        self.widget = Widget()
        logging.basicConfig(level=logging.ERROR, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %('
                                                        'message)s')
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %('
                                                       'message)s')

    def doTranslate(self, target: str) -> Optional[str]:
        for translator in self.translators:
            try:
                return translator.translate(target=target)
            except Exception as e:
                translator.logError(e)
        self.widget.error("错误", "翻译失败（各平台 api 均调用失败，请稍后再试）")
        return None

    def __copy_translate__(self, target: str):
        if target is None:
            return
        target = target.replace("\r", "").replace("\n", "")
        translated = self.doTranslate(target)
        self.widget.setCopied(target)
        self.widget.setTranslated(translated)

    def run(self):
        listenDaemon = Thread(target=self.listener.run, args=[self.interval, self.__copy_translate__])
        listenDaemon.setDaemon(True)
        listenDaemon.start()

        self.widget.open()
