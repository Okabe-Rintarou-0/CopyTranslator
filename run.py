from copy_translate import CopyTranslator
from translator import *

interval = 0.5

if __name__ == '__main__':
    ct = CopyTranslator([BaiduTranslator(), BingTranslator(), YoudaoTranslator()], interval)
    ct.run()
