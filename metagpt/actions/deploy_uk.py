#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
from pathlib import Path
from typing import Tuple

from pydantic import Field

from metagpt.actions.action import Action
from metagpt.logs import logger
from metagpt.schema import RunCodeContext, RunCodeResult
from metagpt.utils.exceptions import handle_exception

PROMPT_TEMPLATE = """
Role: You are a senior development and automation engineer, your role is summarize the code build result.
If the running result does not include an error, you should explicitly approve the result.
On the other hand, if the running result indicates some error, you should point out which part, the development code or the test code, produces the error,
and give specific instructions on fixing the errors. Here is the code info:
{context}
Now you should begin your analysis
---
## instruction:
Please summarize the cause of the errors and give correction instruction
## File To Rewrite:
Determine the ONE file to rewrite in order to fix the error, for example, xyz.py, or test_xyz.py
## Status:
Determine if all of the code works fine, if so write PASS, else FAIL,
WRITE ONLY ONE WORD, PASS OR FAIL, IN THIS SECTION
## Send To:
Please write NoOne if there are no errors, Engineer if the errors are due to problematic development codes, else QaEngineer,
WRITE ONLY ONE WORD, NoOne OR Engineer OR QaEngineer, IN THIS SECTION.
---
You should fill in necessary instruction, status, send to, and finally return all content between the --- segment line.
"""

TEMPLATE_CONTEXT = """
## Development Code File Name
{code_file_name}
## Development Code
```python
{code}
```
## Test File Name
{test_file_name}
## Test Code
```python
{test_code}
```
## Running Command
{command}
## Running Output
standard output: 
```text
{outs}
```
standard errors: 
```text
{errs}
```
"""

command = """
qemu-system-aarch64 \
-M raspi3b \
-cpu cortex-a53 \
-kernel kernel8.img \
-dtb bcm2710-rpi-3-b-plus.dtb \
"""

class DeployUK(Action):
    name: str = "DeployUK"
    i_context: RunCodeContext = Field(default_factory=RunCodeContext)

    async def run_qemu(self, working_directory) -> Tuple[str, str]:
        working_directory = str(working_directory)

        

        # Start the subprocess
        process = subprocess.Popen(
            command, cwd=working_directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env
        )
        logger.info(" ".join(command))

        try:
            # Wait for the process to complete, with a timeout
            stdout, stderr = process.communicate()
        except subprocess.TimeoutExpired:
            logger.info("The command did not complete within the given timeout.")
            process.kill()  # Kill the process if it times out
            stdout, stderr = process.communicate()
        return stdout.decode("utf-8"), stderr.decode("utf-8")

    async def run(self, *args, **kwargs) -> RunCodeResult:
        logger.info(f"Running Qemu to Deploy")
        if self.i_context.mode == "qemu":
            outs, errs = await self.run_qemu()

        logger.info(f"{outs=}")
        logger.info(f"{errs=}")

        context = TEMPLATE_CONTEXT.format(
            code=self.i_context.code,
            code_file_name=self.i_context.code_filename,
            test_code=self.i_context.test_code,
            test_file_name=self.i_context.test_filename,
            command=" ".join(self.i_context.command),
            outs=outs[:500],  # outs might be long but they are not important, truncate them to avoid token overflow
            errs=errs[:10000],  # truncate errors to avoid token overflow
        )

        prompt = PROMPT_TEMPLATE.format(context=context)
        rsp = await self._aask(prompt)
        return RunCodeResult(summary=rsp, stdout=outs, stderr=errs)

    @staticmethod
    @handle_exception(exception_type=subprocess.CalledProcessError)
    def _install_via_subprocess(cmd, check, cwd, env):
        return subprocess.run(cmd, check=check, cwd=cwd, env=env)
    