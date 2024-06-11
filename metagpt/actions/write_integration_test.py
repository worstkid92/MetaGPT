#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 22:12
@Author  : alexanderwu
@File    : write_test.py
@Modified By: mashenquan, 2023-11-27. Following the think-act principle, solidify the task parameters when creating the
        WriteTest object, rather than passing them in when calling the run function.
"""

from typing import Optional

from metagpt.actions.action import Action
from metagpt.const import TEST_CODES_FILE_REPO
from metagpt.logs import logger
from metagpt.schema import Document, TestingContext
from metagpt.utils.common import CodeParser

PROMPT_TEMPLATE = """
NOTICE
---
You are a Quality Assurance (QA) Engineer tasked with ensuring the robustness and functionality of a system post-operating system deployment. Your first responsibility involves meticulously designing a suite of integration test cases derived from the provided design documentation. Following the successful installation of the OS, you will then execute these test scenarios to validate system performance and adherence to specifications.

**Phase 1: Design Integration Test Cases**

1. **Review Design Documentation**: Carefully analyze the system's design documentation context , paying close attention to key functionalities, interfaces between components, expected user flows, and any noted performance or security requirements.
   
2. **Identify Critical Pathways**: Determine the most critical paths and interactions within the system that are fundamental to its operation. These should cover not only basic functionalities but also edge cases and failure recovery mechanisms.
   
3. **Craft Test Scenarios**: Based on your analysis, devise comprehensive test scenarios that target each identified aspect. Include both positive (expected behavior) and negative (error handling, boundary conditions) test cases. Ensure the tests are designed to be automated where feasible.

4. **Document Test Cases**: Clearly document each test case, including its purpose, inputs, expected outputs, and any setup or teardown procedures required. Use a structured format for easy execution and tracking.


Note that the design document to test is at {source_file_path}, we will put your test code at {workspace}/tests/{test_file_name}, and run your test code from {workspace},
you should correctly import the necessary libraries based on these file locations!
## {test_file_name}: Write test code with triple quote. Do your best to implement THIS ONLY ONE FILE.
"""


class WriteIntegrationTest(Action):
    name: str = "WriteIntegrationTest"
    i_context: Optional[TestingContext] = None

    async def write_code(self, prompt):
        code_rsp = await self._aask(prompt)

        try:
            code = CodeParser.parse_code(block="", text=code_rsp)
        except Exception:
            # Handle the exception if needed
            logger.error(f"Can't parse the code: {code_rsp}")

            # Return code_rsp in case of an exception, assuming llm just returns code as it is and doesn't wrap it inside ```
            code = code_rsp
        return code

    async def run(self, *args, **kwargs) -> TestingContext:
        fake_root = self.context.src_workspace + "drivcers/watchdog"
        prompt = PROMPT_TEMPLATE.format(
            code_to_test=self.i_context.code_doc.content,
            test_file_name=self.i_context.test_doc.filename,
            source_file_path=fake_root + "/" + self.i_context.code_doc.root_relative_path,
            workspace=self.i_context.code_doc.root_relative_path + "../",
        )
        self.i_context.test_doc.content = await self.write_code(prompt)
        return self.i_context
