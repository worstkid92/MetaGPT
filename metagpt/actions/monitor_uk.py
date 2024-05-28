# -*- coding: utf-8 -*-
"""
@Time    : 2024-5-27
@Author  : zhangyifan
@File    : release.py
"""

import subprocess
from pathlib import Path

from metagpt.actions import Action
from metagpt.utils.exceptions import handle_exception


class MonitorUK(Action):

    name: str = "MonitorUK"

    async def run(self, *args, **kwargs):
        ##method1.用脚本检测
        ##method2.输出结果到文件
        pass
        
    @staticmethod
    @handle_exception(exception_type=subprocess.CalledProcessError)
    def _install_via_subprocess(cmd, check, cwd, env):
        return subprocess.run(cmd, check=check, cwd=cwd, env=env)

