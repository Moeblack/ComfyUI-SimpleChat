"""
API Config node - Configure API connection with dynamic model selection.
"""
from ..core.providers import ChatConfig


class SimpleChatConfig:
    """
    Configure API connection for SimpleChat nodes.
    Supports dynamic model fetching via the "Refresh Models" button.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "provider": (["openai", "claude", "gemini"], {
                    "default": "openai",
                    "tooltip": "Select the LLM provider",
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "tooltip": "Your API key for the selected provider",
                }),
                # Defined as STRING to bypass ComfyUI's strict list validation.
                # Frontend JS will convert this to a COMBO widget for dropdown functionality.
                "model": ("STRING", {
                    "default": "",
                    "tooltip": "Select a model. Use the Refresh button to fetch available models.",
                }),
            },
            "optional": {
                "base_url": ("STRING", {
                    "default": "",
                    "placeholder": "Leave empty for default URL",
                    "tooltip": "Custom API base URL (for proxies or self-hosted deployments)",
                }),
            }
        }

    RETURN_TYPES = ("SIMPLECHAT_CONFIG",)
    RETURN_NAMES = ("config",)
    FUNCTION = "create_config"
    CATEGORY = "SimpleChat"
    DESCRIPTION = """Configure API connection.

    Usage:
    1. Select Provider
    2. Enter API Key
    3. Click 'Refresh Models' button to fetch available models
    4. Select Model
    """

    def create_config(
        self,
        provider: str,
        api_key: str,
        model: str,
        base_url: str = "",
    ):
        # Default URLs map
        DEFAULT_URLS = {
            "openai": "https://api.openai.com/v1",
            "claude": "https://api.anthropic.com/v1",
            "gemini": "https://generativelanguage.googleapis.com/v1beta",
        }

        # Use default URL if not provided
        if not base_url.strip():
            base_url = DEFAULT_URLS.get(provider, "")

        config = ChatConfig(
            provider=provider,
            api_key=api_key,
            base_url=base_url,
            model=model,
        )

        return (config,)
