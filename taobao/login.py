import asyncio
import random
import time
from pyppeteer import launch
from retrying import retry
import hashlib
from taobao.settings import  cookieDb


def set_md5(username: str):
    """
    将用户名进行md5加密
    :param username:用户名
    :return:
    """
    return hashlib.md5(username.encode()).hexdigest()


def input_time_random():
    """
    缓冲
    :return:
    """
    return random.randint(100, 151)


async def init_page(url):
    """
    初始化配置
    :param url:登录网址
    :return: page
    """
    # 创建浏览器
    browser = await launch({'headless': False, 'args': ['--no-sandbox'], 'userDataDir': './bs1-cache-data'})
    # 创建新页面
    page = await browser.newPage()
    await page.setViewport({'width': 1920, 'height': 1080})
    # 设置请求头
    await page.setUserAgent(
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    )

    # 打开网页
    await page.goto(url)
    # 以下为插入中间js，将淘宝会为了检测浏览器而调用的js修改其结果
    await page.evaluate(
        '''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
    await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
    await page.evaluate('''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
    await page.evaluate('''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')

    return page


def retry_if_result_none(result):
    return result is None


@retry(retry_on_result=retry_if_result_none)
async def mouse_slide(page=None):
    await asyncio.sleep(2)
    try:
        # 鼠标移动到滑块，按下，滑动到头（然后延时处理），松开按键
        await page.hover('#nc_1_n1z')  # 不同场景的验证码模块能名字不同。
        await page.mouse.down()
        await page.mouse.move(2000, 0, {'delay': random.randint(1000, 2000)})
        await page.mouse.up()
    except Exception as e:
        print(e, ':验证失败')
        return None, page
    else:
        await asyncio.sleep(2)
        # 判断是否通过
        slider_again = await page.Jeval('.nc-lang-cnt', 'node => node.textContent')
        if slider_again != '验证通过':
            return None, page
        else:
            # await page.screenshot({'path': './headless-slide-result.png'}) # 截图测试
            print('验证通过')
            return 1, page


# 获取登录后cookie
async def get_cookie(page):
    # res = await page.content()
    cookies_list = await page.cookies()
    cookies = ''
    for cookie in cookies_list:
        str_cookie = '{0}={1};'
        str_cookie = str_cookie.format(cookie.get('name'), cookie.get('value'))
        cookies += str_cookie
    # print(cookies)
    return cookies


async def taobao_login(username, password, url):
    """
    淘宝登录主程序
    :param username: 用户名
    :param password: 密码
    :param url: 登录网址
    :return: 登录cookies
    """
    from taobao.Client.dbcookie import CookieMongo
    page = await init_page(url)
    # 等待页面加载完成
    await page.waitForXPath('//*[@id="login-form"]', {'timeout': 3000})
    await page.type('#fm-login-id', username, {'delay': input_time_random() - 50})  # 账号
    await page.type('#fm-login-password', password, {'delay': input_time_random()})  # 密码
    await page.click('#login-form > div.fm-btn > button')  # 登录
    # 等待滑块出现
    await asyncio.sleep(3)
    slider = await page.Jx('//*[@id="nc_1_n1t"]')  # 是否有滑块
    if slider:
        print('出现滑块')
        flag, page = await mouse_slide(page=page)  # js拉动滑块过去。
        # 验证通过
        if flag:
            # 点击登录
            await page.click('#login-form > div.fm-btn > button')
    await asyncio.sleep(2)
    try:
        await page.Jeval('#login-error', 'node => node.textContent')
    except:
        # 添加cookie到cookie_db中
        cookieDb.update_cookie_flag(user=set_md5(username), cookies=await get_cookie(page), t=str(int(time.time())))
    else:
        print("登录名或登录密码不正确")
        # 程序退出。


if __name__ == '__main__':
    username = '17872006502'
    password = 'xq1988'
    url = 'https://login.taobao.com/member/login.jhtml?redirectURL=http%3A%2F%2Fi.taobao.com%2Fmy_taobao.htm%3Fspm%3Da2e15.8261149.754894437.3.198329b4hH4fXH%26pm_id%3D1501036000a02c5c3739'
    asyncio.get_event_loop().run_until_complete(taobao_login(username, password, url))
