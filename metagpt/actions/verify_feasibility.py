from metagpt.actions.action import Action
from metagpt.logs import logger
from metagpt.schema import Message

class VerifyFeasibility(Action):
    name: str = "VerifyFeasibility"
    PROMPT_TEMPLATE: list = [
"""
    Context: {context}
    Determine if there are any feasibility issues with the lastest modified version of development proposal(perhaps there is only one original version) in the context.
    If there are indeed issues with the feasibility of the plan or something to improve in term of feasibility, identify the problems and provide your suggestions.
    Otherwise you just need to state:"Congratulations on passing the feasibility test!"
"""
    ]

    async def run(self, context: str,index: int = 0,*args, **kwargs):
        prompt = self.PROMPT_TEMPLATE[index].format(context = context)
        return await self._aask(prompt)
    