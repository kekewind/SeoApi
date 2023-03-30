"""百度功能"""

import random
import re
from urllib.parse import quote, unquote
from fake_useragent import UserAgent
import httpx
from lxml import etree
from func.function import Func


class Google():
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

    async def search(self, q):
        """搜索查询"""
        text = unquote(q)
        url = 'https://www.google.com/search'
        params = {"q": text,
                  "oq": text,
                  "source": "hp",
                  "sclient": "gws-wiz",
                  "newwindow": 1,
                  "num": 50}
        use_ip = random.choice(self.func.get_ips())
        # user_agent = UserAgent().random
        user_agent = "APIs-Google (+https://developers.google.com/webmasters/APIs-Google.html)"
        headers = {
            "user-agent": user_agent,
            "referer": "https://www.google.com/",
        }
        resp = await self.request_get(url, headers=headers, params=params, use_ip=use_ip)
        return resp.text

    async def get_source(self, q):
        """获取搜索结果源码"""
        result = await self.search(q)
        return result

    async def get_data(self, q):
        """获取搜索结果data数据"""
        resp_text = await self.search(q)
        with open('index.html', 'w', encoding='utf-8')as f:
            f.write(resp_text)
        tree = etree.HTML(resp_text)
        divs = tree.xpath('//div[@class="egMi0 kCrYT"]')
        datas = []
        for index, div in enumerate(divs):
            try:
                title = div.xpath('.//h3')[0].xpath('string(.)').strip()
                real_url = div.xpath('./a/@href')[0].replace('/url?q=', '')
                real_url = real_url.split('&sa=U&')[0]
                real_url = unquote(unquote(real_url))
                full_domain, root_domain = self.func.get_domain_info(real_url)[
                    1:]
                datas.append({"id": index + 1, "title": title,
                             "full_domain": full_domain, "domain": root_domain, "link": real_url})
            except Exception as e:
                print(index, e)
        # 相关搜索 关键词
        related = tree.xpath('//div[@class="kjGX2"]/span/div/text()')
        # 其他人搜
        more = tree.xpath('//div[@class="Lt3Tzc"]/text()')
        return {"keyword": q, "related": related, "more":more,"data": datas}

    def get_included(self, q):
        """获取搜索结果源码"""
        return 'source'
