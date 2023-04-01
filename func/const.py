# -*- coding: UTF-8 -*-
"""常量配置"""

from enum import Enum

class BaiduAction(str, Enum):
    """百度接口数据限制"""
    SOURCE = "source"
    DATA = "data"
    INCLUDED = "included"
    PULLDOWN = "pulldown"
    
class GoogleAction(str, Enum):
    """百度接口数据限制"""
    SOURCE = "source"
    DATA = "data"
    INCLUDED = "included"
