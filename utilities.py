import json
import re
import urllib.error
import urllib.request

import bpy

OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
API_KEY_MAX_LENGTH = 4096


def get_api_key(context, addon_name):
    preferences = context.preferences
    addon_prefs = preferences.addons[addon_name].preferences
    return addon_prefs.api_key


def normalize_api_key(api_key):
    return re.sub(r"\s+", "", api_key or "")


def api_key_fingerprint(api_key):
    if not api_key:
        return "empty"
    if len(api_key) <= 8:
        return "***" + api_key[-2:]
    return api_key[:7] + "..." + api_key[-4:]


def init_props(chat_message_type):
    bpy.types.Scene.gpt4_chat_history = bpy.props.CollectionProperty(type=chat_message_type)
    bpy.types.Scene.gpt4_model = bpy.props.EnumProperty(
        name="GPT Model",
        description="Select the GPT model to use",
        items=[
            ("gpt-4.1", "GPT-4.1", "High quality code generation"),
            ("gpt-4.1-mini", "GPT-4.1 Mini", "Faster and cheaper code generation"),
            ("gpt-4o", "GPT-4o", "General purpose model"),
            ("gpt-4o-mini", "GPT-4o Mini", "Fast and low cost"),
            ("custom", "Custom", "Use the custom model ID below"),
        ],
        default="gpt-4.1",
    )
    bpy.types.Scene.gpt4_custom_model = bpy.props.StringProperty(
        name="Custom Model",
        description="Optional model ID to use when GPT Model is set to Custom.",
        default="",
        maxlen=128,
    )
    bpy.types.Scene.gpt4_chat_input = bpy.props.StringProperty(
        name="Message",
        description="Enter your message",
        default="",
        maxlen=8192,
    )
    bpy.types.Scene.gpt4_api_key_override = bpy.props.StringProperty(
        name="API Key",
        description="Optional API key for this Blender session. This takes precedence over add-on preferences.",
        default="",
        maxlen=API_KEY_MAX_LENGTH,
        subtype="PASSWORD",
    )
    bpy.types.Scene.gpt4_use_clipboard_api_key = bpy.props.BoolProperty(
        name="Use API key from clipboard",
        description="Read the API key directly from the clipboard when Execute is clicked.",
        default=False,
    )
    bpy.types.Scene.gpt4_button_pressed = bpy.props.BoolProperty(default=False)


def clear_props():
    for prop_name in (
        "gpt4_chat_history",
        "gpt4_model",
        "gpt4_custom_model",
        "gpt4_chat_input",
        "gpt4_api_key_override",
        "gpt4_use_clipboard_api_key",
        "gpt4_button_pressed",
    ):
        if hasattr(bpy.types.Scene, prop_name):
            delattr(bpy.types.Scene, prop_name)


def _response_text(response_data):
    text = response_data.get("output_text")
    if text:
        return text

    parts = []
    for item in response_data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                parts.append(content["text"])
    return "".join(parts)


def _extract_python_code(text):
    fenced_blocks = re.findall(r"```(?:python)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    code = fenced_blocks[0] if fenced_blocks else text
    return code.strip()


def _create_response(api_key, payload):
    request = urllib.request.Request(
        OPENAI_RESPONSES_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        try:
            error_data = json.loads(details)
            message = error_data.get("error", {}).get("message", details)
        except json.JSONDecodeError:
            message = details
        raise RuntimeError(f"OpenAI API error {error.code}: {message}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"Could not connect to OpenAI API: {error.reason}") from error


def generate_blender_code(prompt, chat_history, context, system_prompt, api_key):
    messages = [{"role": "system", "content": system_prompt}]
    for message in list(chat_history)[-10:]:
        if message.type == "assistant":
            messages.append({"role": "assistant", "content": "```\n" + message.content + "\n```"})
        else:
            messages.append({"role": message.type.lower(), "content": message.content})

    messages.append(
        {
            "role": "user",
            "content": (
                "Write Blender 4.2 Python code for this task: "
                + prompt
                + "\nReturn only executable Python code. Do not include explanations."
            ),
        }
    )

    payload = {
        "model": context.scene.gpt4_custom_model.strip() if context.scene.gpt4_model == "custom" else context.scene.gpt4_model,
        "input": messages,
        "max_output_tokens": 2000,
        "reasoning": {"effort": "low"},
        "text": {"verbosity": "low"},
    }

    response_data = _create_response(api_key, payload)
    completion_text = _response_text(response_data)
    return _extract_python_code(completion_text) if completion_text else None


def split_area_to_text_editor(context):
    area = context.area
    for region in area.regions:
        if region.type == 'WINDOW':
            with context.temp_override(area=area, region=region):
                bpy.ops.screen.area_split(direction='VERTICAL', factor=0.5)
            break

    new_area = context.screen.areas[-1]
    new_area.type = 'TEXT_EDITOR'
    return new_area
