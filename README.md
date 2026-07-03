# BlenderGPT
![Header](https://user-images.githubusercontent.com/63528145/227160213-6862cd5e-b31f-43ea-a5e5-6cc340a95617.png)






Blender can be controlled using program scripts written in Python. Recent OpenAI GPT models can generate these Python scripts from simple English and execute them. This plugin provides an easy to use interface that integrates OpenAI GPT models right in the UI, allowing you to use natural language commands to control Blender.

# Note

This fork targets Blender 4.2 and OpenAI's Responses API. It defaults to `gpt-5.5`, with GPT-5.4, GPT-4.1, GPT-4o, and a custom model field available in the add-on panel. GPT-5.5 requires access for the OpenAI project attached to your API key.

## Installation

1. Clone this repository by clicking `Code > Download ZIP` on GitHub
2. Open Blender, go to `Edit > Preferences > Add-ons > Install`
3. Select the downloaded ZIP file and click `Install Add-on`
4. Enable the add-on by checking the checkbox next to `GPT Blender Assistant`
5. Paste your OpenAI API key in the Addon preferences menu.
5. To view the code generations in realtime, go to `Window > Toggle System Console`

## Usage

1. In the 3D View, open the sidebar (press `N` if not visible) and locate the `GPT Assistant` tab
2. Type a natural language command in the input field, e.g., "create a cube at the origin"
3. Click the `Execute` button to generate and execute the Blender Python code


## Requirements

- Blender 4.2 or later
- OpenAI API key (Accessible at https://platform.openai.com/account/api-keys)
- No third-party Python package install is required; the add-on calls the OpenAI Responses API directly with Blender's bundled Python.


## Demonstration
https://user-images.githubusercontent.com/63528145/227158577-d92c6e8d-df21-4461-a69b-9e7cde8c8dcf.mov
