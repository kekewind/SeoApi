# -*- coding: UTF-8 -*-
"""功能函数"""

import linecache
import os
import json
import random
import sys
from urllib.parse import quote
import aiofiles
import tldextract
from ruamel import yaml


class Func():
    """功能函数"""

    def __init__(self):
        self.ips = self.get_ips()

    def get_ips(self):
        """获取当前服务器所有IP"""
        nowsys = sys.platform
        if 'win' in nowsys:
            return []
        try:
            ips_list = os.popen('ip addr').readlines()
            ips = []
            for i in ips_list:
                if "inet " in i:
                    i = i.strip().split(' ')[1].split('/')[0]
                    ips.append(i)
            if "127.0.0.1" in ips:
                ips.remove('127.0.0.1')
            return ips
        except Exception as err:
            print(err)
            return []

    def get_domain_info(self, domain):
        """获取域名前后缀"""
        tld = tldextract.extract(domain)
        subdomain = tld.subdomain.lower()
        full_domain = ".".join(
            [tld.subdomain, tld.domain, tld.suffix]).strip(".").lower()
        root_domain = ".".join([tld.domain, tld.suffix]).strip(".").lower()
        return subdomain, full_domain, root_domain

    def is_domain(self, link):
        """判断是否为域名"""
        root_domain = self.get_domain_info(link)[-1]
        if '.' in root_domain:
            return True
        return False

    def get_yaml(self, path):
        """yaml文件解析"""
        linecache.checkcache(path)
        yml = "".join(linecache.getlines(path))
        result = yaml.load(yml, Loader=yaml.SafeLoader)
        return result
