"""
API routes for fetching model lists from various providers.
"""
import json
import aiohttp
from aiohttp import web

try:
    from server import PromptServer
    HAS_SERVER = True
except ImportError:
    HAS_SERVER = False


# Predefined model lists for each provider
PREDEFINED_MODELS = {
    "openai": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
        "o1-preview",
        "o1-mini",
    ],
    "claude": [
        "claude-sonnet-4-20250514",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ],
    "gemini": [
        "gemini-2.5-flash-preview-05-20",
        "gemini-2.0-flash",
        "gemini-2.0-flash-exp",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-2.5-flash-image",
        "gemini-3-pro-image-preview",
    ],
}


async def fetch_openai_models(api_key: str, base_url: str) -> list[str]:
    """Fetch model list from OpenAI-compatible API."""
    url = f"{base_url.rstrip('/')}/models"
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = [m["id"] for m in data.get("data", [])]
                    # Return all models, sorted alphabetically
                    return sorted(models) if models else PREDEFINED_MODELS["openai"]
    except Exception as e:
        print(f"[SimpleChat] Failed to fetch OpenAI models: {e}")

    return PREDEFINED_MODELS["openai"]


async def fetch_claude_models(api_key: str, base_url: str) -> list[str]:
    """
    Fetch models for Claude provider.
    Tries to hit the /models endpoint (supported by some proxies and newer Anthropic API).
    Falls back to predefined list if fails.
    """
    # Anthropic API format for models list is /v1/models
    # Note: Official Anthropic API recently added models endpoint support
    url = f"{base_url.rstrip('/')}/models"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Anthropic format: {"data": [{"id": "...", ...}]} similar to OpenAI
                    # Some proxies might return OpenAI format
                    models = []

                    # Handle both standard formats just in case
                    items = data.get("data", []) if "data" in data else data.get("models", [])

                    if isinstance(items, list):
                        for m in items:
                            if isinstance(m, dict):
                                models.append(m.get("id", m.get("name", "")))
                            elif isinstance(m, str):
                                models.append(m)

                    # Filter out empty strings
                    models = [m for m in models if m]

                    if models:
                        return sorted(models)
    except Exception as e:
        # Silently fail for Claude since it's common for this endpoint to not exist/fail
        pass

    return PREDEFINED_MODELS["claude"]


async def fetch_gemini_models(api_key: str, base_url: str) -> list[str]:
    """Fetch model list from Gemini API."""
    url = f"{base_url.rstrip('/')}/models?key={api_key}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = []
                    for m in data.get("models", []):
                        name = m.get("name", "")
                        # Extract model name from full path (models/gemini-xxx)
                        if name.startswith("models/"):
                            name = name[7:]
                        if name:
                            models.append(name)
                    # Return all models
                    return sorted(models) if models else PREDEFINED_MODELS["gemini"]
    except Exception as e:
        print(f"[SimpleChat] Failed to fetch Gemini models: {e}")

    return PREDEFINED_MODELS["gemini"]


def get_all_predefined_models_list() -> list[str]:
    """Get a flat list of all predefined models."""
    all_models = []
    for provider_models in PREDEFINED_MODELS.values():
        all_models.extend(provider_models)
    return all_models


def setup_routes():
    """Setup API routes for SimpleChat."""
    if not HAS_SERVER:
        return

    @PromptServer.instance.routes.get("/simplechat/models/{provider}")
    async def get_models(request):
        """
        Get available models for a provider.

        Query params:
            - api_key: API key for the provider
            - base_url: (optional) Custom base URL
        """
        provider = request.match_info.get("provider", "").lower()
        api_key = request.query.get("api_key", "")
        base_url = request.query.get("base_url", "")

        # Return predefined models if no API key provided
        if not api_key:
            models = PREDEFINED_MODELS.get(provider, [])
            return web.json_response(models)

        # Default base URLs
        default_urls = {
            "openai": "https://api.openai.com/v1",
            "claude": "https://api.anthropic.com/v1",
            "gemini": "https://generativelanguage.googleapis.com/v1beta",
        }

        if not base_url:
            base_url = default_urls.get(provider, "")

        # Fetch models based on provider
        if provider == "openai":
            models = await fetch_openai_models(api_key, base_url)
        elif provider == "claude":
            models = await fetch_claude_models(api_key, base_url)
        elif provider == "gemini":
            models = await fetch_gemini_models(api_key, base_url)
        else:
            models = []

        return web.json_response(models)

    @PromptServer.instance.routes.get("/simplechat/models")
    async def get_all_models_list(request):
        """
        Get all predefined models as a flat list (for COMBO remote input).
        Returns a simple array of model names.
        """
        return web.json_response(get_all_predefined_models_list())

    @PromptServer.instance.routes.get("/simplechat/models_dict")
    async def get_all_predefined_models(request):
        """Get all predefined models organized by provider."""
        return web.json_response(PREDEFINED_MODELS)

    print("[SimpleChat] API routes registered")
