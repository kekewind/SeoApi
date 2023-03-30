"""百度功能"""

import random
from urllib.parse import quote, unquote
from fake_useragent import UserAgent
import httpx
from lxml import etree
from func.function import Func


class Baidu():
    """百度功能"""

    def __init__(self):
        self.func = Func()

    async def request_get(self, url, headers=None, params=None, use_ip='127.0.0.1'):
        """异步访问"""
        transport = httpx.AsyncHTTPTransport(local_address=use_ip)
        async with httpx.AsyncClient(
                headers=headers, params=params, http2=True, transport=transport) as client:
            resp = await client.get(url)
        return resp

    async def get_cookie(self, use_ip):
        """获取cookie"""
        url = 'https://www.baidu.com'
        user_agent = UserAgent().random
        headers = {'User-Agent': user_agent}
        transport = httpx.AsyncHTTPTransport(local_address=use_ip)
        async with httpx.AsyncClient(http2=True, transport=transport) as client:
            resp = await client.get(url, headers=headers)
        with open('./baidu.html','w',encoding='utf-8')as f:
            f.write(resp.content.decode('utf-8'))
        cookie = resp.headers['set-cookie'].strip()
        return cookie, user_agent

    async def search(self, q):
        """搜索查询"""
        text = unquote(q)
        url = "https://www.baidu.com/s"
        params = {"wd": text,
                  "rn": 50,
                  "ie": "UTF-8"}
        use_ip = random.choice(self.func.get_ips())
        print(use_ip)
        cookie, user_agent = await self.get_cookie(use_ip)
        headers = {'User-Agent': user_agent,
                   'Accept': 'text/html,application/xhtml+xml,application/xml;'
                   'q=0.9,image/avif,image/webp,image/apng,*/*;'
                   'q=0.8,application/signed-exchange;v=b3;q=0.7',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Accept-Language': 'zh-CN,zh;q=0.9',
                   'Connection': 'keep-alive',
                   'Cookie': cookie,
                   'Host': 'www.baidu.com',
                   'Referer': 'https://www.baidu.com/',
                   'Sec-Fetch-Dest': 'document',
                   'Sec-Fetch-Mode': 'navigate',
                   'Sec-Fetch-Site': 'same-origin',
                   'Upgrade-Insecure-Requests': '1',
                   'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", '
                   '"Chromium";v="111"',
                   'sec-ch-ua-mobile': '?0',
                   'sec-ch-ua-platform': '"Windows"'}
        resp = await self.request_get(url, headers=headers, params=params, use_ip=use_ip)
        source_data = resp.content.decode('utf-8')
        return source_data

    async def get_source(self, q):
        """获取搜索结果源码"""
        result = await self.search(q)
        return result

    async def get_data(self, q):
        """获取搜索结果data数据"""
        resp_text = await self.search(q)
        tree = etree.HTML(resp_text)
        results = tree.xpath(
            "//div[contains(concat(' ', @class, ' '), 'result')]")
        datas = []
        for index, result in enumerate(results):
            srcid_ = result.xpath("@srcid")
            srcid = srcid_[0] if len(srcid_) > 0 else ""
            id_ = result.xpath("@id")
            index_id = id_[0] if len(id_) > 0 else ""
            title = result.xpath("string(div//h3/a)")
            if len(title.strip()) > 1:
                if srcid == "1599":
                    link = result.xpath("string(div//h3/a/@href)")
                    des = result.xpath(
                        "string(div//span[@class='content-right_8Zs40'])")
                    origin = result.xpath(
                        "string(div//span[@aria-hidden='true'])")
                    print(title, link, des, origin)
                    datas.append({'id': index_id, 'title': title,
                                 'origin': origin, 'des': des, 'link': link})
        return {"data": datas}

    def get_included(self, q):
        """获取搜索结果源码"""
        return 'source'
