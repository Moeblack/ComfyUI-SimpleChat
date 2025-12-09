"""
NoASS (No Assistant) format processing for roleplay optimization.

NoASS transforms traditional chat into a unified narrative where all dialogue
is combined into a single assistant message, with character prefixes marking speakers.
"""


def format_noass_prompt(
    system: str,
    history: str | None,
    user_input: str,
    prefill_start: str = "",
    user_name: str = "User",
    char_name: str = "Assistant",
) -> tuple[str, str]:
    """
    Format conversation in NoASS style.

    Args:
        system: System prompt / world setting
        history: Previous conversation history (NoASS format)
        user_input: Current user input
        prefill_start: Optional starting text for assistant response
        user_name: User's character name
        char_name: AI character name

    Returns:
        Tuple of (system_prompt, prefilled_content)
        - system_prompt: Instructions for the model
        - prefilled_content: The conversation to continue from
    """
    user_prefix = f"**{user_name}:**"
    char_prefix = f"**{char_name}:**"

    # Build the conversation history structure
    content_parts = []

    # 1. Add existing history if any
    if history:
        content_parts.append(history)

    # 2. Add current user input
    content_parts.append(f"{user_prefix} {user_input}")

    # 3. Add character prefix to prompt response
    if prefill_start.strip():
        # If we have a forced start, include it
        content_parts.append(f"{char_prefix} {prefill_start}")
    else:
        # Otherwise just the prefix
        content_parts.append(f"{char_prefix}")

    prefilled = "\n\n".join(content_parts)

    return system, prefilled


def build_noass_messages(
    system: str,
    history: str | None,
    user_input: str,
    prefill_start: str = "",
    user_name: str = "User",
    char_name: str = "Assistant",
) -> list[dict[str, str]]:
    """
    Build message list for NoASS format using proper Assistant Prefill where possible.

    Structure:
    [
        {"role": "user", "content": system},  # System/Scenario as first user message
        {"role": "assistant", "content": [History] + [User Input] + [Prefill]} # The entire story so far
    ]

    The API is expected to continue directly from the end of the assistant message.
    """
    messages = []

    # 1. System/Scenario (as User message to ensure it's read as instructions)
    # Using 'system' role is also fine but 'user' often works better for "Instruction" in NoASS context
    # However, standard practice is still system role for actual instructions.
    # Let's stick to 'user' for the "Scenario Description" as requested by the user's mental model.
    if system:
        messages.append({"role": "user", "content": system})
    else:
        # Fallback if system is empty
        messages.append({"role": "user", "content": "Narrative Roleplay."})

    # 2. Build the giant Assistant Prefill block
    user_prefix = f"**{user_name}:**"
    char_prefix = f"**{char_name}:**"

    story_blocks = []

    if history:
        story_blocks.append(history)

    # Append current user action
    story_blocks.append(f"{user_prefix} {user_input}")

    # Append the start of the assistant's turn
    if prefill_start:
        story_blocks.append(f"{char_prefix} {prefill_start}")
    else:
        # Just the prefix to cue the AI
        story_blocks.append(f"{char_prefix}")

    full_prefill = "\n\n".join(story_blocks)

    messages.append({
        "role": "assistant",
        "content": full_prefill
    })

    return messages


def extract_noass_response(
    response_text: str,
    user_name: str = "User",
    char_name: str = "Assistant",
) -> str:
    """
    Extract the character's response from NoASS output.

    Since we are using prefill, the API might return JUST the continuation,
    or (depending on provider behavior) might repeat some text.
    Standard OpenAI/Claude behavior for prefill is to return just the NEW tokens.
    """
    user_prefix = f"**{user_name}:**"

    # If response contains user prefix (hallucinated next turn), truncate there
    if user_prefix in response_text:
        response_text = response_text.split(user_prefix)[0]

    return response_text.strip()


def build_full_history(
    history: str | None,
    user_input: str,
    prefill_start: str,
    response: str,
    user_name: str = "User",
    char_name: str = "Assistant",
) -> str:
    """
    Build complete conversation history after a response.
    Reconstructs the full text including the prefill and the new response.
    """
    user_prefix = f"**{user_name}:**"
    char_prefix = f"**{char_name}:**"

    # Construct the assistant's full turn
    if prefill_start:
        full_response = f"{char_prefix} {prefill_start} {response}"
    else:
        full_response = f"{char_prefix} {response}"

    # Append to history
    if history:
        return f"{history}\n\n{user_prefix} {user_input}\n\n{full_response}"
    else:
        return f"{user_prefix} {user_input}\n\n{full_response}"


def get_stop_sequences(user_name: str = "User") -> list[str]:
    """
    Get stop sequences for NoASS mode.
    The model should stop when it tries to write for the user.
    """
    user_prefix = f"**{user_name}:**"
    return [user_prefix, f"\n{user_prefix}", f"\n\n{user_prefix}"]
