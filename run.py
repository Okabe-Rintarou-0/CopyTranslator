from copy_translate import CopyTranslator
from translator import BaiduTranslator

interval = 0.5

if __name__ == '__main__':
    translator = BaiduTranslator()
    ct = CopyTranslator(translator, interval)
    ct.run()
