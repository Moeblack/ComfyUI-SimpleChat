"""
Chat node - Basic text conversation.
"""
from ..core import get_provider, ChatConfig


class SimpleChatText:
    """Basic text conversation with LLM."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "config": ("SIMPLECHAT_CONFIG",),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
            },
            "optional": {
                "system": ("STRING", {"multiline": True, "default": ""}),
                "temperature": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1}),
                "max_tokens": ("INT", {"default": 2048, "min": 1, "max": 128000}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "chat"
    CATEGORY = "SimpleChat"
    DESCRIPTION = "Send a text prompt to LLM and get a response."

    async def chat(
        self,
        config: ChatConfig,
        prompt: str,
        system: str = "",
        temperature: float = 1.0,
        max_tokens: int = 2048,
    ):
        # Build messages
        messages = []
        if system.strip():
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        # Get provider and send request
        provider = get_provider(config)

        # Directly await the async provider method
        response = await provider.chat(
            messages=messages,
            model=config.model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return (response.text,)
