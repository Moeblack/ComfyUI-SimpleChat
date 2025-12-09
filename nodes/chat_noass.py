"""
Chat NoASS node - Roleplay-optimized conversation with NoASS format.
"""
import torch
from ..core import (
    get_provider,
    ChatConfig,
    format_noass_prompt,
    build_noass_messages,
    extract_noass_response,
    build_full_history,
    get_stop_sequences,
)


class SimpleChatNoASS:
    """NoASS format conversation for roleplay optimization."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "config": ("SIMPLECHAT_CONFIG",),
                "scenario_instructions": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "placeholder": "Define world setting, characters, and instructions here (The Scenario)."
                }),
                "user_action": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "placeholder": "Your current action or dialogue."
                }),
            },
            "optional": {
                "prefill_start": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "placeholder": "Force the start of the assistant's response (Prefill)."
                }),
                "history": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "image": ("IMAGE",),
                "user_name": ("STRING", {"default": "User"}),
                "char_name": ("STRING", {"default": "Assistant"}),
                "temperature": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1}),
                "max_tokens": ("INT", {"default": 2048, "min": 1, "max": 128000}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "history")
    FUNCTION = "chat"
    CATEGORY = "SimpleChat"
    DESCRIPTION = "NoASS (Experimental) - Hardcore Roleplay with Assistant Prefill. Uses single-turn context with giant assistant prefill to force formatting."

    async def chat(
        self,
        config: ChatConfig,
        scenario_instructions: str,
        user_action: str,
        prefill_start: str = "",
        history: str = "",
        image: torch.Tensor = None,
        user_name: str = "User",
        char_name: str = "Assistant",
        temperature: float = 1.0,
        max_tokens: int = 2048,
    ):
        # Format in NoASS style
        system_prompt, prefilled = format_noass_prompt(
            system=scenario_instructions,
            history=history if history.strip() else None,
            user_input=user_action,
            prefill_start=prefill_start,
            user_name=user_name,
            char_name=char_name,
        )

        # Build messages using the new prefill logic
        messages = build_noass_messages(
            system=scenario_instructions,
            history=history if history.strip() else None,
            user_input=user_action,
            prefill_start=prefill_start,
            user_name=user_name,
            char_name=char_name,
        )

        # Get provider
        provider = get_provider(config)

        # Prepare images
        images = [image] if image is not None else None

        # Get stop sequences
        stop_sequences = get_stop_sequences(user_name)

        # Directly await the async provider method
        response = await provider.chat(
            messages=messages,
            model=config.model,
            temperature=temperature,
            max_tokens=max_tokens,
            images=images,
            stop=stop_sequences,  # Some providers support this
        )

        # Extract response and build history
        response_text = extract_noass_response(
            response.text,
            user_name=user_name,
            char_name=char_name,
        )

        # Reconstruct the full text for the history output
        new_history = build_full_history(
            history=history if history.strip() else None,
            user_input=user_action,
            prefill_start=prefill_start,
            response=response_text,
            user_name=user_name,
            char_name=char_name,
        )

        # If we had a prefill, the returned 'text' should probably include it
        # so the user sees the full response in the text output node
        if prefill_start.strip():
            final_text_output = f"{prefill_start} {response_text}"
        else:
            final_text_output = response_text

        return (final_text_output, new_history)
