from threading import Thread

from copy_listener import CopyListenerFactory
from gui import Widget
from translator import *


class CopyTranslator(object):
    def __init__(self, translator: Translator, interval: float):
        self.translator = translator
        self.listener = CopyListenerFactory.newCopyListener()
        self.interval = interval
        self.widget = Widget()

    def __copy_translate__(self, target: str):
        if target is None:
            return
        target = target.replace("\r", "").replace("\n", "")
        translated = self.translator.translate(target)
        print(translated)
        self.widget.setCopied(target)
        self.widget.setTranslated(translated)

    def run(self):
        listenDaemon = Thread(target=self.listener.run, args=[self.interval, self.__copy_translate__])
        listenDaemon.setDaemon(True)
        listenDaemon.start()

        self.widget.open()
