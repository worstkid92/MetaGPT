from metagpt.actions import Action
from metagpt.logs import logger
from metagpt.schema import Message

#and DON'T forget some key points from the previous modification process in the Context(if the Context is not empty).
#Context: {context}

class ReviseDevelopmentProposal(Action):
    name: str = "ReviewDevelopmentProposal"
    PROMPT_TEMPLATE: list = [
"""
NOTICE
Role: You are a professional designer,
there is a development proposal writen by designer to meet the origin user's development requirement,
the development proposal was sent to a reviewer to verify its feasibility and feedback is provided,
your main goal is to revise the development proposal refer to the feedback from the reviewer.

# origin user's development requirement: {requirement}

# the development proposal:{proposal}

# feedback from the reviewer:{feedback}

REMEMBER what you need to give is the development proposal which you have already revised,rather than just give some suggestions on how to revise the development proposal 
and you don't need to output some title,such as:" # Revised development proposal:",you just need to ouput the content of the modified development proposal.
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

    async def run(self, context: str,feedback: str,proposal: str,requirement: str,index: int = 0,*args, **kwargs):
        #context:包括用户（开发）需求，历史版本的开发建议
        #feedback:来自reviewer的反馈/修改建议
        logger.info(context)
        prompt = self.PROMPT_TEMPLATE[index].format(context = context, feedback = feedback,proposal = proposal,requirement = requirement)
        logger.info(prompt)
        return await self._aask(prompt)
    