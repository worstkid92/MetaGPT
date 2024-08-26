from metagpt.actions.action import Action
from metagpt.logs import logger
from metagpt.schema import Message

class WriteDevelopmentProposal(Action):
    name: str = "WriteDevelopmentProposal"
    PROMPT_TEMPLATE: list = [
"""
    {requirement}
""",
"""
    You will be gien input hardware manual and requirements,
    you need to output technology selection or algorithm selection(depend on the concrete problem) Within the required specification range, 
    the concrete problem description is as follow:{problem}
""",

"""
    You will be given two or more design apporaches related to operating system,
    you need to compare and analyze the advantages and disadvantages of these two approaches.
    the concrete problem description is as follow:{problem}

"""
    ]

    async def run(self, requirement: str,index: int = 0,*args, **kwargs):
        #problem:用户（开发）需求
        prompt = self.PROMPT_TEMPLATE[index].format(requirement = requirement)
        prompt = prompt + "and be careful not to make it too long"
        return await self._aask(prompt)
    