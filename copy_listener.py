import abc
from time import sleep

import win32clipboard as wcb
import win32con as wc

import utils


class CopyListener(object):
    def __init__(self):
        self.lastCopy = ""

    @abc.abstractmethod
    def run(self, interval, handler):
        pass


class WinCopyListener(CopyListener):
    def run(self, interval, handler):
        assert interval > 0
        self.lastCopy = self.getCopyContent()
        handler(self.lastCopy)
        while True:
            copy = self.getCopyContent()
            if copy != self.lastCopy:
                self.lastCopy = copy
                handler(copy)
            sleep(interval)

    def getCopyContent(self) -> str:
        ret = ""
        try:
            wcb.OpenClipboard()
            if wcb.IsClipboardFormatAvailable(wc.CF_UNICODETEXT):
                ret = wcb.GetClipboardData(wc.CF_UNICODETEXT)
            wcb.CloseClipboard()
        except Exception as e:
            print(e)
            ret = self.lastCopy
            sleep(0.1)
        finally:
            return ret


class CopyListenerFactory(object):
    @staticmethod
    def newCopyListener():
        if utils.isWindows():
            return WinCopyListener()
        else:
            return None


if __name__ == '__main__':
    copyListener = CopyListenerFactory.newCopyListener()
    copyListener.run(0.5, lambda content: print("content is: {}".format(content)))
