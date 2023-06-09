# -*- coding: UTF-8 -*-

from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from fastapi import Response, Request, Form, Body
from fastapi import FastAPI
import uvicorn
from starlette.responses import JSONResponse, RedirectResponse, FileResponse
from func.function import Func
from func import middle
from func.router import Router
from func.const import *


app = FastAPI(
    title="SeoApi",
    description="seo网络服务api - by TG@seo888",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "百度",
            "description": "百度相关api",
        },
        {
            "name": "谷歌",
            "description": "谷歌相关api",
        },
        {
            "name": "米人",
            "description": "米人相关api",
        },
        {
            "name": "域名",
            "description": "域名相关api",
        },
        {
            "name": "telegram",
            "description": "telegram相关api",
        },
    ],
    docs_url="/",
    redoc_url=None,
    openapi_url="/api/v1/openapi.json",
)
func = Func()
# 路由引用
router = Router()

@app.middleware("http")
async def middleware(request: Request, call_next):
    """中间件 访问前后"""
    return await middle.middleware(request, call_next, func)

@app.get("/s")
async def baidu_(wd: str = None,rn:int = 50):
    """百度接口 搜索输入跳转"""
    if wd is None:
        return JSONResponse(status_code=404, content={"error": '参数错误'})
    search_url = f"/baidu/source?q={wd}&num={rn}"
    return RedirectResponse(url=search_url,status_code=301)

@app.get("/baidu/{action}", tags=["百度"])
async def baidu(action: BaiduAction, q: str = None,num:int = 50):
    """百度接口"""
    if q is None:
        return JSONResponse(status_code=404, content={"error": '参数错误'})
    return await router.baidu(action, q,num=num)

@app.get("/search")
async def google_(q: str = None,num: int = 50):
    """谷歌接口 搜索输入跳转"""
    if q is None:
        return JSONResponse(status_code=404, content={"error": '参数错误'})
    search_url = f"/google/source?q={q}&num={num}"
    return RedirectResponse(url=search_url,status_code=301)


@app.get("/google/{action}", tags=["谷歌"])
async def google(action: GoogleAction, q: str = None,num: int = 50):
    """谷歌接口"""
    if q is None:
        return JSONResponse(status_code=404, content={"error": '参数错误'})
    return await router.google(action, q,num=num)

@app.get("/url")
async def url(q: str=''):
    """google 搜索结果url跳转"""
    if q[:len("http")] == "http":
        return RedirectResponse(url=q,status_code=301)
    return {'q':q}

@app.get("/mir6/{action}", tags=["米人"])
async def mir6(action: Mir6Action, q: str = None):
    """米人mir6.com接口"""
    if q is None:
        return JSONResponse(status_code=404, content={"error": '参数错误'})
    return await router.mir6(action, q)


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=17888)
