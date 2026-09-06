from llama_index.core.llms import (
    CustomLLM,
    CompletionResponse,
    CompletionResponseGen,
    LLMMetadata,
)
from llama_index.core.llms.callbacks import llm_completion_callback

from app.services.llm import LLMService


class OpsPilotLLM(CustomLLM):
    llm_service: LLMService

    def __init__(self, **kwargs):
        kwargs["llm_service"] = LLMService()
        super().__init__(**kwargs)

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=100000,
            num_output=4096,
            model_name="claude-opus-5",
        )

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs) -> CompletionResponse:

        response = self.llm_service.chat(prompt)

        return CompletionResponse(text=response)

    @llm_completion_callback()
    def stream_complete(self, prompt: str, **kwargs) -> CompletionResponseGen:

        response = self.llm_service.chat(prompt)

        yield CompletionResponse(text=response, delta=response)

    async def acomplete(self, prompt: str, **kwargs) -> CompletionResponse:

        return self.complete(prompt, **kwargs)

    async def astream_complete(self, prompt: str, **kwargs) -> CompletionResponseGen:

        response = self.llm_service.chat(prompt)

        yield CompletionResponse(text=response, delta=response)
