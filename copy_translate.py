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

    def translateParagraph(self, target: str, results: list, idx: int):
        if not (0 <= idx < len(results)):
            raise Exception("invalid index")
        results[idx] = self.doTranslate(target)

    def separateTranslate(self, copied: str) -> str:
        targets = copied.split("\r")
        targets = [target for target in targets if len(target.strip()) > 0]
        numTargets = len(targets)
        results = ['' for _ in range(numTargets)]
        workers = [threading.Thread(target=self.translateParagraph, args=[targets[i], results, i]) for i in
                   range(numTargets)]

        for worker in workers:
            worker.start()
            worker.join()

        translated = str.join("\n", results)
        return translated

    def mergeTranslate(self, copied: str) -> str:
        target = copied.replace("\r", "").replace("\n", "")
        return self.doTranslate(target)

    def __copy_translate__(self, copied: str):
        if copied is None:
            return

        self.widget.setCopied(copied)
        if self.widget.isMerged():
            translated = self.mergeTranslate(copied)
        else:
            translated = self.separateTranslate(copied)
        self.widget.setTranslated(translated)

    def run(self):
        listenDaemon = Thread(target=self.listener.run, args=[self.interval, self.__copy_translate__])
        listenDaemon.setDaemon(True)
        listenDaemon.start()

        self.widget.open()
