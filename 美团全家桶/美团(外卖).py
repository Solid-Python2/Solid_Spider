import requests

url = 'http://meishi.meituan.com/i/api/channel/deal/list'
data = {"uuid": "a1cb33d007664b6b925a.1602985471.1.0.0", "version": "8.3.3", "platform": 3, "app": "", "partner": 126,
          "riskLevel": 1, "optimusCode": 10,
          "originUrl": "http://meishi.meituan.com/i/?ci=1&stid_b=1&cevent=imt%2Fhomepage%2Fcategory1%2F1", "offset": 0,
          "limit": 15, "cateId": 1, "lineId": 0, "stationId": 0, "areaId": 0, "sort": "default", "deal_attr_23": "",
          "deal_attr_24": "", "deal_attr_25": "", "poi_attr_20043": "", "poi_attr_20033": ""}
headers = {
    'Host': 'meishi.meituan.com',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Mobile Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
    'Accept': 'application/json',
    'Cookie': '__mta=220617255.1602945986080.1602986281099.1602986395600.7; _lxsdk_cuid=1753447cc5043-0a6334322b7d95-7b2d3714-144000-1753447cc51c8; _hc.v=e1f098cb-96b2-4a01-14b8-996e29d7fbe3.1602900040; mtcdn=K; _lxsdk=C082368707A3F2CBB95285B68189E70F278B4EF52CC5105E0E5C3D0EA4E54390; iuuid=C082368707A3F2CBB95285B68189E70F278B4EF52CC5105E0E5C3D0EA4E54390; _ga=GA1.2.512209238.1602916009; _gid=GA1.2.285258540.1602916009; webp=1; rvct=1%2C151%2C801%2C122%2C8001%2C20%2C30; uuid=a1cb33d007664b6b925a.1602985471.1.0.0; lat=39.880397; lng=116.317906; IJSESSIONID=x72ld1ee6r871fa0np2aq1gwp; latlng=22.765484,113.554218,1602986245171; ci3=1; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; i_extend=H__a100001__b2; cityname=%E5%8C%97%E4%BA%AC; __utma=74597006.512209238.1602916009.1602945981.1602986245.2; __utmb=74597006.4.9.1602986261269; __utmc=74597006; __utmz=74597006.1602986245.2.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; logan_session_token=yekh3w635b92pxx6ryhu; _lxsdk_s=17539613091-e69-601-66%7C2%7C612; client-id=4c751a24-7f45-4ee6-972b-0aa8f3a7597b; ci=1; meishi_ci=1; cityid=1; uuid=870dde7faa044491b1b7.1602986213.1.0.0; client-id=4c751a24-7f45-4ee6-972b-0aa8f3a7597b',
    'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW',
    'Referer': 'http://meishi.meituan.com/i/?ci=1&stid_b=1&cevent=imt%2Fhomepage%2Fcategory1%2F1',
}
print(requests.post(url,  headers=headers,data=data).json())
