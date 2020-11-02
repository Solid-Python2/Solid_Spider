import math
import random
from datetime import datetime
import requests, json, re
import hashlib

if __name__ == '__main__':
    key = 'rain'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
        'Referer': 'http://fanyi.sogou.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Cookie': 'YYID=D832CE22323DA4E13D30F316600BFD4D; IMEVER=9.3.0.3129; SUV=004EC7C50EDCE77A5CD8EC629688D985; CXID=B37E0E718CDB6032AE47178CECB439C1; SUID=6AE7DC0E3665860A5CFB7D65000C079F; IPLOC=CN4419; ssuid=8255104706; wuid=AAEmjU2WKAAAAAqLFCRHyw4AGwY=; SNUID=55704A9B959301E530428D6E96C6E4D2; ad=AZllllllll2N0xdQlllllVLG4CYlllllRH8XVkllll9lllllpklll5@@@@@@@@@@; ABTEST=0|1566913274|v17; SELECTION_SWITCH=1; HISTORY_SWITCH=1'
    }
    M = []
    for i in range(9):
        M.append(hex(math.floor((random.random() + 1) * 65536)).split('0x1')[1])
    uuid = M[0] + M[1] + '-' + M[2] + '-' + M[3] + '-' + M[4] + '-' + ''.join(M[-3:])
    s = hashlib.md5(f'autozh-CHS{key}8511813095152'.encode()).hexdigest()
    url = 'https://fanyi.sogou.com/reventondc/translateV2'
    data = {
        'from': 'auto',
        'to': 'zh-CHS',
        'text': key,
        'client': 'pc',
        'fr': 'browser_pc',
        'pid': 'sogou-dict-vr',
        'dict': 'true',
        'word_group': 'true',
        'second_query': 'true',
        'uuid':uuid,
        'needQc': 1,
        's': s
    }
    rep=requests.post(url, headers=headers, data=data).json()
    #翻译
    translate=rep['data']['translate']['dit']
    print(key,translate)

