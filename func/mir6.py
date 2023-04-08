# -*- coding: UTF-8 -*-
"""米人mir6.com功能"""

import random
import httpx
from fake_useragent import UserAgent


class Mir6():
    """米人mir6.com功能"""

    def __init__(self, func):
        self.func = func

    async def request_get(self, url, headers=None, params=None, use_ip='127.0.0.1'):
        """异步访问"""
        transport = httpx.AsyncHTTPTransport(local_address=use_ip)
        async with httpx.AsyncClient(
                headers=headers, params=params, transport=transport) as client:
            resp = await client.get(url)
        return resp

    async def get_weight(self, q):
        """权重查询"""
        use_ip = random.choice(self.func.get_ips())
        url = "https://api.mir6.com/api/bdqz"
        headers = {
            "user-agent": UserAgent().random
        }
        params = {
            "type": "json",
            "domain": q,
        }
        resp = await self.request_get(url, headers=headers, params=params, use_ip=use_ip)
        return resp.json()
