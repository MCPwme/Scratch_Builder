"""
Scratch Builder Package
https://github.com/MCPwme/Scratch_Builder
"""
from .output import initialize_output_system, log_message
from .assets import AssetManager
from .blocks import Block, BlockBuilder
from .sprite import Sprite
from .project import ScratchProject

# 初始化输出系统
initialize_output_system(False)

__version__ = "1.0.0.dev20261018"

__all__ = [
    "ScratchProject",
    "Sprite",
    "AssetManager",
    "Block",
    "BlockBuilder",
    "initialize_output_system",
    "log_message"
]
