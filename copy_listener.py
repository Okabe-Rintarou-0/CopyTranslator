import abc
from time import sleep

import win32clipboard as wcb
import win32con as wc

import utils


def test_copy():
    wcb.OpenClipboard()
    wcb.EmptyClipboard()
    wcb.SetClipboardData(wc.CF_TEXT, "你好，世界！".encode("gbk"))
    wcb.CloseClipboard()

    wcb.OpenClipboard()
    data = wcb.GetClipboardData(wc.CF_TEXT)
    wcb.CloseClipboard()
    print(data.decode("gbk"))


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
            data = wcb.GetClipboardData(wc.CF_TEXT)
            ret = data.decode("gbk")
            wcb.CloseClipboard()
        except Exception as e:
            print(e)
            ret = self.lastCopy
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
