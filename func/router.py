# -*- coding: UTF-8 -*-
"""路由解析器"""

import os
from fastapi import Response, Request, Form, Body
from starlette.responses import JSONResponse, RedirectResponse, FileResponse
from func.baidu import Baidu
from func.google import Google
from func.const import *
from func.function import Func
from func.mir6 import Mir6

class Router():
    """路由解析器"""

    def __init__(self):
        self.func = Func()
        if not os.path.exists('cookie_cache'):
            os.mkdir('cookie_cache')

    async def baidu(self, action, wd,rn=50):
        """百度接口"""
        baidu = Baidu(self.func)
        if action == BaiduAction.SOURCE:
            result = await baidu.get_source(wd,rn)
            return Response(content=result, media_type='text/html;charset=utf-8')
        elif action == BaiduAction.DATA:
            result = await baidu.get_data(wd,rn)
        elif action == BaiduAction.INCLUDED:
            result = await baidu.get_included(wd,rn)
        elif action == BaiduAction.PULLDOWN:
            result = await baidu.get_pulldown(wd)
        return JSONResponse(result)

    async def google(self, action, q,num=50):
        """谷歌接口"""
        google = Google(self.func)
        if action == GoogleAction.SOURCE:
            result = await google.get_source(q,num)
            return Response(content=result, media_type='text/html;charset=utf-8')
        elif action == GoogleAction.DATA:
            result = await google.get_data(q,num)
        elif action == GoogleAction.INCLUDED:
            result = await google.get_included(q,num)
        return JSONResponse(result)
    
    async def mir6(self, action, q):
        """谷歌接口"""
        mir6 = Mir6(self.func)
        if action == Mir6Action.WEIGHT:
            result = await mir6.get_weight(q)
        return JSONResponse(result)
