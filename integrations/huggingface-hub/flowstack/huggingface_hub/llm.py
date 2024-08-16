from flowstack.ai.llm import BaseLLM
from flowstack.messages import BaseMessage
from flowstack.prompts import PromptStack

class HfApiLLM(BaseLLM):
    def _generate(self, stack: PromptStack, **kwargs) -> BaseMessage:
        pass