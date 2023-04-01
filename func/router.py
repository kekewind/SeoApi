import os
from fastapi import Response, Request, Form, Body
from starlette.responses import JSONResponse, RedirectResponse, FileResponse
from func.baidu import Baidu
from func.google import Google
from func.const import *
from func.function import Func

class Router():
    """路由解析器"""

    def __init__(self):
        self.func = Func()
        if not os.path.exists('cookie_cache'):
            os.mkdir('cookie_cache')

    async def baidu(self, action, q):
        """百度接口"""
        baidu = Baidu(self.func)
        if action == BaiduAction.SOURCE:
            result = await baidu.get_source(q)
            return Response(content=result, media_type='text/html;charset=utf-8')
        elif action == BaiduAction.DATA:
            result = await baidu.get_data(q)
        elif action == BaiduAction.INCLUDED:
            result = await baidu.get_included(q)
        elif action == BaiduAction.PULLDOWN:
            result = await baidu.get_pulldown(q)
        return JSONResponse(result)

    async def google(self, action, q):
        """谷歌接口"""
        google = Google(self.func)
        if action == GoogleAction.SOURCE:
            result = await google.get_source(q)
            return Response(content=result, media_type='text/html;charset=utf-8')
        elif action == GoogleAction.DATA:
            result = await google.get_data(q)
        elif action == GoogleAction.INCLUDED:
            result = google.get_included(q)
        return JSONResponse(result)
