from metagpt.actions import UserRequirement,VerifyFeasibility,WriteDevelopmentProposal,ReviseDevelopmentProposal

from metagpt.logs import logger
from metagpt.roles.role import Role, RoleReactMode
from metagpt.schema import Message
from metagpt.utils.common import any_to_name
from metagpt.llm import LLM
from metagpt.configs.llm_config import LLMConfig
from metagpt.const import MESSAGE_ROUTE_TO_ALL


class ValidationEngineer(Role):
    """
    Represents a validation engineer role responsible for product development and management.

    Attributes:
        name (str): Name of the validation engineer.
        profile (str): Role profile, default is 'validation engineer'.
        goal (str): Goal of the validation engineer.
        constraints (str): Constraints or limitations for the validation engineer.
    """
    name: str = "Bob"
    profile: str = "validation engineer"
    goal: str = "Efficiently identify any feasibility issues or risks with the development proposal and provide suggestions for handling them"
    constraints: str = ""
    todo_action: str = ""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.set_actions([VerifyFeasibility])
        self._watch([WriteDevelopmentProposal,ReviseDevelopmentProposal])
        self.rc.react_mode = RoleReactMode.REACT

    async def need_modification(self,rsp: str):
        llm_config= LLMConfig(model= "ft0820:latest")
        llm = LLM(llm_config=llm_config)
        prompt = """
# context
## validation engineer's feedback for a development proposal
{rsp}
        
# instruction
You are given a validation engineer's feedback for a development proposal,
you need to determine if the development proposal need to do some modification depend on validation engineer's feedback,

# format example
## example1
validation engineer's feedback for a development proposal:Congratulations on passing the feasibility test!
expeceted output:False

## example2
validation engineer's feedback for a development proposal 2:Some legacy applications may not be compatible with the new OS,modify the plan to update or replace incompatible applications and hardware.
expeceted output 2:True
"""    
        return "True"
        rsp = await llm.aask(prompt.format(rsp=rsp))
        return rsp

    

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo

        context = self.get_memories()
        rsp = await todo.run(context=context)

        tmp = await self.need_modification(rsp=rsp)
        print("#####test function need_modification")
        print(tmp)
        print("$$$$$$$$$$$")

        ## todo
        ## 考虑正则？
        if "True" in tmp:
            return Message(content=rsp, role=self.profile,cause_by=type(todo),send_to="Alice")
        else:
            return Message(content=rsp, role=self.profile,cause_by=type(todo),send_to="Carol")
        
    async def _observe(self, ignore_memory=False) -> int:
        """Prepare new messages for processing from the message buffer and other sources."""
        # Read unprocessed messages from the msg buffer.
        news = []
        if self.recovered:
            news = [self.latest_observed_msg] if self.latest_observed_msg else []
        if not news:
            news = self.rc.msg_buffer.pop_all()
        # Store the read messages in your own memory to prevent duplicate processing.
        old_messages = [] if ignore_memory else self.rc.memory.get()
        self.rc.memory.add_batch(news)
        # Filter out messages of interest.
        self.rc.news = [
            n for n in news if (n.cause_by in self.rc.watch or self.name in n.send_to) and (n not in old_messages) 
        ]
        logger.info(len(self.rc.news))
        self.latest_observed_msg = self.rc.news[-1] if self.rc.news else None  # record the latest observed msg

        # Design Rules:
        # If you need to further categorize Message objects, you can do so using the Message.set_meta function.
        # msg_buffer is a receiving buffer, avoid adding message data and operations to msg_buffer.
        news_text = [f"{i.role}: {i.content[:20]}..." for i in self.rc.news]
        if news_text:
            logger.debug(f"{self._setting} observed: {news_text}")
        return len(self.rc.news)