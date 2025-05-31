"""
ComfyUI-NS-PromptList
A ComfyUI custom node for managing prompts with YAML files
"""

from .prompt_list_node import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

WEB_DIRECTORY = "./web"