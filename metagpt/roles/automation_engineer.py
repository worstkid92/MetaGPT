#!/usr/bin/env python
# -*- coding: utf-8 -*-


from metagpt.actions import DebugError, RunCode, BuildUK, DeployUK
from metagpt.actions.summarize_code import SummarizeCode
from metagpt.const import MESSAGE_ROUTE_TO_NONE
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Document, Message, RunCodeContext, TestingContext
from metagpt.utils.common import any_to_str_set, parse_recipient

import os

class Automation_engineer(Role):
    name: str = "Jokic"
    profile: str = "AutomationEngineer"
    goal: str = "Build and deploy software"
    constraints: str = (
        "The test code you write should conform to code standard like PEP8, be modular, easy to read and maintain."
        "Use same language as user requirement"
    )
    test_round_allowed: int = 5
    test_round: int = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # FIXME: a bit hack here, only init one action to circumvent _think() logic,
        #  will overwrite _think() in future updates
        self.set_actions([BuildUK])
        self._watch([SummarizeCode])
        self.test_round = 0


    async def _run_code(self, msg):
        run_code_context = RunCodeContext.loads(msg.content)
        src_makefile = await self.project_repo.with_src_path(self.context.src_workspace).srcs.get(
            os.path.join(self.context.src_workspace,"Makefile")
        ) 
        if not src_makefile:
            return
        run_code_context.code = src_makefile.content
        result = await BuildUK(i_context=run_code_context, context=self.context, llm=self.llm).run()
        await self.project_repo.test_outputs.save(
            filename=run_code_context.output_filename,
            content=result.model_dump_json(),
        )
        run_code_context.code = None
        run_code_context.test_code = None
        # the recipient might be Engineer or myself
        recipient = parse_recipient(result.summary)
        mappings = {"Engineer": "Alex", "QaEngineer": "Edward"}
        self.publish_message(
            Message(
                content=run_code_context.model_dump_json(),
                role=self.profile,
                cause_by=BuildUK,
                sent_from=self,
                send_to="Edward", ##name of QA
            )
        )

    async def _deploy_UK(self, msg):
        run_code_context = RunCodeContext.loads(msg.content)
        result = await DeployUK(i_context=run_code_context, context=self.context, llm=self.llm).run()
        await self.project_repo.test_outputs.save(
            filename=run_code_context.output_filename,
            content=result.model_dump_json(),
        )
        run_code_context.code = None
        run_code_context.test_code = None
        # the recipient might be Engineer or myself
        recipient = parse_recipient(result.summary)
        mappings = {"Engineer": "Alex", "QaEngineer": "Edward"}
        self.publish_message(
            Message(
                content=run_code_context.model_dump_json(),
                role=self.profile,
                cause_by=DeployUK,
                sent_from=self,
                send_to="Edward", ##name of QA
            )
        )

    async def _act(self) -> Message:

        run_filters = any_to_str_set({BuildUK})
        deploy_filters = any_to_str_set({DeployUK})
        for msg in self.rc.news:
            # Decide what to do based on observed msg type, currently defined by human,
            # might potentially be moved to _think, that is, let the agent decides for itself
            if msg.cause_by in run_filters:
                # I wrote or debugged my test code, time to run it
                await self._run_code(msg)
            if msg.cause_by in deploy_filters:
                # I wrote or debugged my test code, time to run it
                await self._deploy_UK(msg)

        self.test_round += 1
        return Message(
            content=f"Round {self.test_round} of tests done",
            role=self.profile,
            cause_by=BuildUK,
            sent_from=self.profile,
            send_to=MESSAGE_ROUTE_TO_NONE,
        )

    async def _observe(self, ignore_memory=False) -> int:
        # This role has events that trigger and execute themselves based on conditions, and cannot rely on the
        # content of memory to activate.
        return await super()._observe(ignore_memory=True)
