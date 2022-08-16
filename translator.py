import abc
import json
import logging
import re
import threading
import urllib
import urllib.parse
import urllib.request
from multiprocessing import cpu_count

import execjs
import requests


class Translator(object):
    @abc.abstractmethod
    def translate(self, target: str) -> str:
        pass

    @abc.abstractmethod
    def logError(self, err: Exception):
        pass


JS_CODE = """
function a(r, o) {
    for (var t = 0; t < o.length - 2; t += 3) {
        var a = o.charAt(t + 2);
        a = a >= "a" ? a.charCodeAt(0) - 87 : Number(a),
        a = "+" === o.charAt(t + 1) ? r >>> a: r << a,
        r = "+" === o.charAt(t) ? r + a & 4294967295 : r ^ a
    }
    return r
}
var C = null;
var token = function(r, _gtk) {
    var o = r.length;
    o > 30 && (r = "" + r.substr(0, 10) + r.substr(Math.floor(o / 2) - 5, 10) + r.substring(r.length, r.length - 10));
    var t = void 0,
    t = null !== C ? C: (C = _gtk || "") || "";
    for (var e = t.split("."), h = Number(e[0]) || 0, i = Number(e[1]) || 0, d = [], f = 0, g = 0; g < r.length; g++) {
        var m = r.charCodeAt(g);
        128 > m ? d[f++] = m: (2048 > m ? d[f++] = m >> 6 | 192 : (55296 === (64512 & m) && g + 1 < r.length && 56320 === (64512 & r.charCodeAt(g + 1)) ? (m = 65536 + ((1023 & m) << 10) + (1023 & r.charCodeAt(++g)), d[f++] = m >> 18 | 240, d[f++] = m >> 12 & 63 | 128) : d[f++] = m >> 12 | 224, d[f++] = m >> 6 & 63 | 128), d[f++] = 63 & m | 128)
    }
    for (var S = h,
    u = "+-a^+6",
    l = "+-3^+b+-f",
    s = 0; s < d.length; s++) S += d[s],
    S = a(S, u);
    return S = a(S, l),
    S ^= i,
    0 > S && (S = (2147483647 & S) + 2147483648),
    S %= 1e6,
    S.toString() + "." + (S ^ h)
}
"""


class BaiduTranslator(Translator):
    def logError(self, err: Exception):
        self.logger.error(err)

    def translate(self, target: str) -> str:
        respJson = self.__translate__(target, dst='zh', src='en')
        return respJson['trans_result']['data'][0]['dst']

    def __init__(self):
        self.sess = requests.Session()
        self.logger = logging.getLogger("Baidu")
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/71.0.3578.98 Safari/537.36 '
        }
        self.token = None
        self.gtk = None
        self.javascript = execjs.compile(JS_CODE)
        self.load()

    def load(self):
        # 获得token和gtk
        # 必须要加载两次保证token是最新的，否则会出现998的错误
        self.loadMainPage()
        self.loadMainPage()

    def loadMainPage(self):
        """
            load main page : https://fanyi.baidu.com/
            and get token, gtk
        """
        url = 'https://fanyi.baidu.com'

        try:
            r = self.sess.get(url, headers=self.headers)
            self.token = re.findall(r"token: '(.*?)',", r.text)[0]
            self.gtk = re.findall(r'window.gtk = "(.*?)";', r.text)[0]
        except Exception as e:
            raise e

    def langDetect(self, query):
        """
            post query to https://fanyi.baidu.com/langdetect
            return json like
            {"error":0,"msg":"success","lan":"en"}
        """
        url = 'https://fanyi.baidu.com/langdetect'
        data = {'query': query}
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/87.0.4280.66 Safari/537.36'}
            r = self.sess.post(url=url, data=data, headers=headers)
        except Exception as e:
            raise e

        respJson = r.json()
        if 'msg' in respJson and respJson['msg'] == 'success':
            return respJson['lan']
        return None

    def __translate__(self, query, dst='zh', src=None):
        """
            get translate result from https://fanyi.baidu.com/v2transapi
        """
        url = 'https://fanyi.baidu.com/v2transapi'

        sign = self.javascript.call('token', query, self.gtk)

        if not src:
            src = self.langDetect(query)

        data = {
            'from': src,
            'to': dst,
            'query': query,
            'simple_means_flag': 3,
            'sign': sign,
            'token': self.token,
        }
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/87.0.4280.66 Safari/537.36'}
            r = self.sess.post(url=url, data=data, headers=headers)
        except Exception as e:
            raise e

        if r.status_code == 200:
            respJson = r.json()
            if 'error' in respJson:
                raise Exception('baidu sdk error: {} msg: {}'.format(respJson['error'], respJson['errmsg']))
                # 998错误则意味需要重新加载主页获取新的token
            return respJson
        return None


class YoudaoTranslator(Translator):
    def __init__(self):
        self.logger = logging.getLogger("Youdao")
        self.numWorkers = cpu_count()

    def logError(self, err: Exception):
        self.logger.error(err)

    def translateSentence(self, sentences: list, results: list, idxs: list):
        for idx in idxs:
            if not (0 <= idx < len(results) and idx < len(sentences)):
                raise Exception("invalid index")
            results[idx] = self.__translate__(sentences[idx])

    def translate(self, target: str) -> str:
        sentences = target.split(".")
        numSentences = len(sentences)
        numWorkers = min(self.numWorkers, numSentences)
        results = ['' for _ in range(numSentences)]
        jobPerWorker = numSentences // numWorkers
        workers = [threading.Thread(target=self.translateSentence,
                                    args=[sentences, results, range(i * jobPerWorker, (i + 1) * jobPerWorker)])
                   for i in range(numWorkers)]
        for worker in workers:
            worker.start()
            worker.join()

        return str.join(".", results)

    @staticmethod
    def __translate__(target: str) -> str:
        url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&sessionFrom=https://www.baidu.com' \
              '/link '
        data = {
            'from': 'AUTO',
            'to': 'AUTO',
            'smartresult': 'dict',
            'client': 'fanyideskweb',
            'salt': '1500092479607',
            'sign': 'c98235a85b213d482b8e65f6b1065e26',
            'doctype': 'json',
            'version': '2.1',
            'keyfrom': 'fanyi.web',
            'action': 'FY_BY_CL1CKBUTTON',
            'typoResult': 'true',
            'i': target
        }

        data = urllib.parse.urlencode(data).encode('utf-8')
        wy = urllib.request.urlopen(url, data)
        html = wy.read().decode('utf-8')
        ta = json.loads(html)
        return ta['translateResult'][0][0]['tgt']


class BingTranslator(Translator):

    def logError(self, err: Exception):
        self.logger.error(err)

    def __init__(self):
        self.url = "http://api.microsofttranslator.com/v2/ajax.svc/TranslateArray2?"
        self.logger = logging.getLogger("Youdao")

    def translate(self, target: str) -> str:
        return self.__translate__(src="en", dst="zh", target=target)

    def __translate__(self, src: str, dst: str, target: str):
        data = {'from': '"' + src + '"', 'to': '"' + dst + '"', 'texts': '["'}
        data['texts'] += target
        data['texts'] += '"]'
        data['options'] = "{}"
        data['oncomplete'] = 'onComplete_3'
        data['onerror'] = 'onError_3'
        data['_'] = '1430745999189'
        data = urllib.parse.urlencode(data).encode('utf-8')
        strUrl = self.url + data.decode() + "&appId=%223DAEE5B978BA031557E739EE1E2A68CB1FAD5909%22"
        response = urllib.request.urlopen(strUrl)
        str_data = response.read().decode('utf-8')
        tmp, str_data = str_data.split('"TranslatedText":')
        translate_data = str_data[1:str_data.find('"', 1)]
        return translate_data
