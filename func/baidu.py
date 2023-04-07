# -*- coding: UTF-8 -*-
"""百度功能"""

import json
import linecache
import os
import random
import re
from urllib.parse import quote, unquote
import aiofiles
import arrow
from fake_useragent import UserAgent
import httpx
from lxml import etree
from tenacity import retry, stop_after_attempt


class Baidu():
    """百度功能"""

    def __init__(self, func):
        self.func = func
        os.makedirs("cookie_cache",exist_ok=True)

    async def request_get(self, url, headers=None, params=None, use_ip='127.0.0.1'):
        """异步访问"""
        transport = httpx.AsyncHTTPTransport(local_address=use_ip)
        async with httpx.AsyncClient(
                headers=headers, params=params, http2=True, transport=transport) as client:
            resp = await client.get(url)
        return resp

    async def get_cookie(self, use_ip):
        """获取cookie"""
        url = 'http://www.baidu.com'
        user_agent = UserAgent().random
        headers = {'User-Agent': user_agent}
        transport = httpx.AsyncHTTPTransport(local_address=use_ip)
        async with httpx.AsyncClient(http2=True, transport=transport) as client:
            resp = await client.get(url, headers=headers)
        cookie = resp.headers['set-cookie'].strip()
        return {"cookie": cookie, "User-Agent": user_agent, 'use_ip': use_ip}

    async def search(self, q):
        """搜索查询"""
        text = unquote(q)
        url = "http://www.baidu.com/s"
        params = {"wd": text,
                  "rn": 50,
                  "ie": "UTF-8"}
        use_ip = random.choice(self.func.get_ips())
        ip_path_dir = os.path.join("cookie_cache", arrow.now(
            "Asia/Shanghai").format('YYYY-MM-DD'))
        os.makedirs(ip_path_dir, exist_ok=True)
        ip_path = os.path.join(ip_path_dir, use_ip)+".json"
        if not os.path.exists(ip_path):
            cache = await self.get_cookie(use_ip)
            async with aiofiles.open(ip_path, "w", encoding='utf-8')as json_f:
                await json_f.write(json.dumps(cache))
        else:
            linecache.checkcache(ip_path)
            cache_text = "".join(linecache.getlines(ip_path))
            cache = json.loads(cache_text)
        headers = {'User-Agent': cache["User-Agent"],
                   'Accept': 'text/html,application/xhtml+xml,application/xml;'
                   'q=0.9,image/avif,image/webp,image/apng,*/*;'
                   'q=0.8,application/signed-exchange;v=b3;q=0.7',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Accept-Language': 'zh-CN,zh;q=0.9',
                   'Connection': 'keep-alive',
                   'Cookie': cache['cookie'],
                   'Host': 'www.baidu.com',
                   'Referer': 'http://www.baidu.com/',
                   'Sec-Fetch-Dest': 'document',
                   'Sec-Fetch-Mode': 'navigate',
                   'Sec-Fetch-Site': 'same-origin',
                   'Upgrade-Insecure-Requests': '1'}
        resp = await self.request_get(url, headers=headers, params=params, use_ip=use_ip)
        source_data = resp.content.decode('utf-8')
        return source_data, cache

    async def get_source(self, q):
        """获取搜索结果源码"""
        resp_text, cache = await self.search(q)
        return resp_text

    @retry(stop=stop_after_attempt(2))
    async def get_real_url(self, link, user_agent, use_ip):
        """获取百度链接真实地址"""
        transport = httpx.AsyncHTTPTransport(local_address=use_ip)
        headers = {"User-Agent": user_agent}
        async with httpx.AsyncClient(transport=transport) as client:
            resp = await client.get(link, headers=headers, follow_redirects=False, timeout=15)
        real_url = resp.headers['Location']
        return real_url

    async def get_data(self, q):
        """获取搜索结果data数据"""
        resp_text, cache = await self.search(q)
        tree = etree.HTML(resp_text)
        others_source = tree.xpath("//div[@class='c-font-medium list_1V4Yg']//a/text()")
        if len(others_source) > 0:
            more = [i.strip() for i in others_source]
        related_source = tree.xpath(
            "//table[@class='rs-table_3RiQc']//a/text()")
        if len(related_source) > 0:
            related = [i.strip() for i in related_source]
        results = tree.xpath(
            "//div[contains(concat(' ', @class, ' '), 'result')]")
        datas = []
        for index, result in enumerate(results):
            srcid_ = result.xpath("@srcid")
            srcid = srcid_[0] if len(srcid_) > 0 else ""
            id_ = result.xpath("@id")
            index_id = id_[0] if len(id_) > 0 else ""
            mu_ = result.xpath("@mu")
            real_url = mu_[0] if len(mu_) > 0 else ""
            title = result.xpath("string(div//h3/a)")
            if len(title.strip()) > 1:
                if srcid == "1599":
                    des = result.xpath(
                        "string(div//span[@class='content-right_8Zs40'])")
                    origin = result.xpath(
                        "string(div//span[@aria-hidden='true'])")
                    full_domain, domain = self.func.get_domain_info(real_url)[1:]
                    datas.append({'id': index_id, 'title': title, 'origin': origin,
                                 "full_domain": full_domain, "domain": domain, "link": real_url, 'des': des})
        return {"keyword": q, "related": related, "more": more, "data": datas}

    async def get_included(self, q):
        """获取收录数据"""
        link = q.replace('http://', '').replace('https://', '')
        full_domain, domain = self.func.get_domain_info(link)[1:]
        if "." in domain:
            # 查询链接自身收录
            resp_text, cache = await self.search(link)
            if '没有找到该URL' in resp_text:
                included = False
                return {'url': q, 'included': included, 'success': True}
            else:
                included = True
                resp_text, cache = await self.search(q)
                tree = etree.HTML(resp_text)
                results = tree.xpath(
                    "//div[contains(concat(' ', @class, ' '), 'result')]")
                for result in results:
                    srcid_ = result.xpath("@srcid")
                    srcid = srcid_[0] if len(srcid_) > 0 else ""
                    id_ = result.xpath("@id")
                    index_id = id_[0] if len(id_) > 0 else ""
                    title = result.xpath("string(div//h3/a)")
                    if len(title.strip()) > 1:
                        if srcid == "1599" and index_id == "1":
                            des = result.xpath(
                                "string(div//span[@class='content-right_8Zs40'])")
                            origin = result.xpath(
                                "string(div//span[@aria-hidden='true'])")
                            break
                return {'url': q, 'included': included, 'title': title, 'origin': origin, "full_domain": full_domain, "domain": domain, 'des': des, 'success': True}
        else:
            return {'url': q, 'info': f'{q} 非url链接', 'success': False}

    async def get_pulldown(self, q):
        """百度下拉词"""
        url = f"https://www.baidu.com/sugrec?pre=1&p=3&ie=utf-8&json=1&prod=pc&from=pc_web&sugsid=34647,34068,34749,34654,34711,34597,34584,34107,26350,34502,34423,22157,34691&cb=jQuery11020383424710195859_1632731774592&_=1632731774608&wd={q}"
        use_ip = random.choice(self.func.ips)
        transport = httpx.AsyncHTTPTransport(local_address=use_ip)
        async with httpx.AsyncClient(transport=transport) as client:
            resp = await client.get(url, timeout=15)
        pull_down_words = []
        h_text = resp.text
        h_text = re.sub('jQuery.*?\(', '', h_text).strip(')')
        a = json.loads(h_text)
        if '"g":[{' in resp.text:
            pull_down_words.extend(i["q"] for i in a["g"])
        return {"keyword": q, "pull_down_words": pull_down_words}
