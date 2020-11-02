import requests
import re
import execjs
import ast


class Baidu_Translate():
    """
    1.获取当前用户要转化的语言即lan
    2.获取身份标识:token和cookie
    我们可以通过正则表达式获取token,获取网站的cookie有二种,这里我们可以用其中一种即创建一个session,因为session会自动保存cookie
    3.通过python利用第三方库调用js中的函数,从而获取sign
    4.通过正则获取语言列表
    """
    def __init__(self, keyword):
        #要翻译的内容
        self.keyword = keyword
        #首页链接
        home_page_url = "https://fanyi.baidu.com/"
        #设置请求头
        self.headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
            "x-requested-with": "XMLHttpRequest",
            "origin": "https://fanyi.baidu.com",
            "referer": "https://fanyi.baidu.com/?aldtype=16047"
        }
        #获取cookie
        self.session = requests.session()
        self.lan = self.getlan()
        #获取首页
        result = self.session.get(home_page_url).text
        self.session.headers = self.headers
        # 获取token
        self.token = re.findall(r"token: '(.*?)'", result)[0]
        #获取Sign
        with open("baidujs.js", "r") as fp:
            jsData = fp.read()
        self.sign = execjs.compile(jsData).call("e", self.keyword)
        #获取语言列表
        self.langList_string = re.findall(r"langList: (.*?)account:", result,
                                          re.S)[0]
        self.langlist = ast.literal_eval(
            self.langList_string.replace('\n', '').replace(' ', '')[:-1])

    # 获取lan(当前要转化的语言)
    def getlan(self):
        try:
            lan_url = "https://fanyi.baidu.com/langdetect"
            response_dict = self.session.post(lan_url,
                                              data={
                                                  'query': self.keyword
                                              }).json()
            if not response_dict.get('error'):
                lan = response_dict["lan"]
                return lan
        except Exception as e:
            print(e)

    #获取结果
    def translate(self):
        data = {
            'from': self.lan,
            'to': 'en' if self.lan != 'en' else 'zh',
            'query': self.keyword,
            'transtype': 'realtime',
            'simple_means_flag': 3,
            'sign': self.sign,
            'token': self.token
        }
        try:
            #百度翻译的链接
            url = "https://fanyi.baidu.com/v2transapi"
            result = self.session.post(url, data=data).json()
            if not result.get("error"):
                ret = result['trans_result']['data'][0]['dst']
                if self.lan != 'en':
                    print(self.langlist[self.lan] + ":" + self.keyword + "\t" +
                          self.langlist["en"] + ":" + ret)
                else:
                    print(self.langlist[self.lan] + ":" + self.keyword + "\t" +
                          self.langlist["zh"] + ":" + ret)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    trans = Baidu_Translate("こんにちは")
    trans.translate()