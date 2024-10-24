from typing import Iterable

from openai import OpenAI


class OpenRouterClient(OpenAI):
    model_name: str
    tools_list: list
    temperature: float

    extra_headers = {  # replace with your own project url and name here
        'HTTP-Referer': 'https://pxl-research.be/',
        'X-Title': 'PXL Smart ICT'
    }

    def __init__(self,
                 api_key: str,
                 base_url: str = 'https://openrouter.ai/api/v1',
                 model_name: str = 'openai/gpt-4o-mini',
                 tools_list: list = None,
                 temperature: float = 0):
        super().__init__(base_url=base_url,
                         api_key=api_key)

        self.model_name = model_name
        self.tools_list = tools_list
        self.temperature = temperature

    def create_completions_stream(self, message_list: Iterable, stream=True):
        return self.chat.completions.create(model=self.model_name,
                                            messages=message_list,
                                            tools=self.tools_list,
                                            stream=stream,
                                            temperature=self.temperature,
                                            extra_headers=self.extra_headers)

    def set_model(self, model_name: str):
        self.model_name = model_name


# some affordable models with tool calling
JAMBA_LARGE = 'ai21/jamba-1-5-large'
JAMBA_MINI = 'ai21/jamba-1-5-mini',
CLAUDE3_HAIKU = 'anthropic/claude-3-haiku',
DEEPSEEK = 'deepseek/deepseek-chat',
GEMINI_FLASH_15 = 'google/gemini-flash-1.5',
GEMINI_PRO = 'google/gemini-pro',
GEMINI_PRO_15 = 'google/gemini-pro-1.5',
LLAMA_405B_I = 'meta-llama/llama-3.1-405b-instruct',
LLAMA_70B_I = 'meta-llama/llama-3.1-70b-instruct',
LLAMA_8B_I = 'meta-llama/llama-3.1-8b-instruct',
MISTRAL_NEMO = 'mistralai/mistral-nemo',
GPT_4O_0608 = 'openai/gpt-4o-2024-08-06',
GPT_4O_MINI = 'openai/gpt-4o-mini',
GPT_4O_MINI_1807 = 'openai/gpt-4o-mini-2024-07-18'
