"""
Scratch Builder - Project Module
https://github.com/MCPwme/Scratch_Builder
"""
import json
import zipfile
import hashlib
import os
import traceback
from pathlib import Path
from .output import *
from .blocks import Block, BlockBuilder

initialize_output_system()

class AssetManager:
    """素材管理器 - 负责计算MD5并管理素材"""

    def __init__(self):
        self.assets = {}
        self.costume_counter = 0
        self.sound_counter = 0

    def _compute_md5_and_ext(self, file_path):
        """读取文件并返回 (md5哈希, 不带点的小写扩展名, 文件字节内容)"""
        with open(file_path, 'rb') as f:
            content = f.read()
        md5_hash = hashlib.md5(content).hexdigest()
        ext = Path(file_path).suffix.lower()
        if ext.startswith('.'):
            ext = ext[1:]
        return md5_hash, ext, content

    def add_costume(self, file_path, name=None):
        """添加造型素材，返回符合Scratch规范的引用信息"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"素材文件不存在: {file_path}")

        md5_hash, ext, content = self._compute_md5_and_ext(file_path)
        md5ext = f"{md5_hash}.{ext}"
        self.assets[md5ext] = content

        if name is None:
            self.costume_counter += 1
            name = f"costume{self.costume_counter}"

        return {
            "assetId": md5_hash,
            "name": name,
            "md5ext": md5ext,
            "dataFormat": ext,
            "rotationCenterX": 0,
            "rotationCenterY": 0
        }

    def add_sound(self, file_path, name=None):
        """添加声音素材"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"声音文件不存在: {file_path}")

        md5_hash, ext, content = self._compute_md5_and_ext(file_path)
        md5ext = f"{md5_hash}.{ext}"
        self.assets[md5ext] = content

        if name is None:
            self.sound_counter += 1
            name = f"sound{self.sound_counter}"

        return {
            "assetId": md5_hash,
            "name": name,
            "md5ext": md5ext,
            "dataFormat": ext,
            "rate": 44100,
            "sampleCount": 0
        }

    def get_all_assets(self):
        """获取所有素材"""
        return self.assets


class Sprite:
    """角色类"""

    def __init__(self, name="Sprite"):
        self.name = name
        self.costumes = []
        self.sounds = []
        self.blocks = {}
        self.variables = {}
        self.lists = {}
        self.comments = {}
        self.currentCostume = 0
        self.volume = 100
        self.layerOrder = 1
        self.visible = True
        self.x = 0
        self.y = 0
        self.size = 100
        self.direction = 90
        self.draggable = False
        self.rotationStyle = "all around"
        self._block_id_counter = 0
        self._broadcasts = {}

    def _generate_block_id(self):
        self._block_id_counter += 1
        return f"{self.name}_{self._block_id_counter}"

    def _register_block(self, block):
        block_id = self._generate_block_id()
        self.blocks[block_id] = block
        block.block_id = block_id
        return block_id

    def add_costume(self, asset_manager, file_path, name=None):
        """添加造型"""
        costume_info = asset_manager.add_costume(file_path, name)
        self.costumes.append(costume_info)
        return costume_info

    def add_sound(self, asset_manager, file_path, name=None):
        """添加声音"""
        sound_info = asset_manager.add_sound(file_path, name)
        self.sounds.append(sound_info)
        return sound_info

    def create_variable(self, name, default_value=0):
        self.variables[name] = [name, str(default_value)]
        return self

    def create_list(self, name, initial_items=None):
        self.lists[name] = [name, list(initial_items or [])]
        return self

    def _broadcast_id(self, message):
        message = str(message)
        self._broadcasts[message] = message
        return message

    def when_flag_clicked(self):
        """当绿旗被点击"""

        block = Block("event_whenflagclicked")
        block.top_level = True
        self._register_block(block)
        return BlockBuilder(self, block)

    def when_key_pressed(self, key="space"):
        block = Block("event_whenkeypressed",
            fields={"KEY_OPTION": [key, None]})
        block.top_level = True
        self._register_block(block)
        return BlockBuilder(self, block)

    def when_this_sprite_clicked(self):
        block = Block("event_whenthisspriteclicked")
        block.top_level = True
        self._register_block(block)
        return BlockBuilder(self, block)

    def when_i_receive(self, message):
        message_id = self._broadcast_id(message)
        block = Block("event_whenbroadcastreceived",
            fields={"BROADCAST_OPTION": [str(message), message_id]})
        block.top_level = True
        self._register_block(block)
        return BlockBuilder(self, block)

    def when_backdrop_switches_to(self, backdrop):
        block = Block("event_whenbackdropswitchesto",
            fields={"BACKDROP": [str(backdrop), None]})
        block.top_level = True
        self._register_block(block)
        return BlockBuilder(self, block)

    def when_greater_than(self, menu, value):
        block = Block("event_whengreaterthan",
            inputs={"VALUE": [1, [4, str(value)]]},
            fields={"WHENGREATERTHANMENU": [menu, None]})
        block.top_level = True
        self._register_block(block)
        return BlockBuilder(self, block)

    def when_i_start_as_a_clone(self):
        block = Block("control_start_as_clone")
        block.top_level = True
        self._register_block(block)
        return BlockBuilder(self, block)

    def to_dict(self):
        """序列化为 Scratch JSON 格式"""
        blocks_dict = {}

        # 第一遍：创建基础积木数据
        for block_id, block in self.blocks.items():
            try:
                blocks_dict[block_id] = {
                    "opcode": block.opcode,
                    "next": block.next_block.block_id if block.next_block else None,
                    "parent": block.parent_block.block_id if block.parent_block else None,
                    "inputs": block.inputs.copy() if hasattr(block, 'inputs') else {},
                    "fields": block.fields if hasattr(block, 'fields') else {},
                    "shadow": block.shadow if hasattr(block, 'shadow') else False,
                    "topLevel": block.top_level if hasattr(block, 'top_level') else False
                }
            except Exception as e:
                log_message('warning'f"⚠ 积木 {block_id} 序列化时出错，跳过：{e}")

        return {
            "isStage": False,
            "name": self.name,
            "variables": self.variables,
            "lists": self.lists,
            "broadcasts": {},
            "blocks": blocks_dict,
            "comments": {},
            "currentCostume": 0,
            "costumes": self.costumes,
            "sounds": self.sounds,
            "volume": 100,
            "layerOrder": 1,
            "visible": self.visible,
            "x": self.x,
            "y": self.y,
            "size": self.size,
            "direction": self.direction,
            "draggable": self.draggable,
            "rotationStyle": self.rotationStyle
        }


class ScratchProject:
    """Scratch 项目主类"""

    def __init__(self, name="My Project"):
        self.name = name
        self.sprites = []
        self.asset_manager = AssetManager()
        self._init_stage()

    def _init_stage(self):
        """初始化舞台"""
        self.stage = {
            "isStage": True,
            "name": "Stage",
            "variables": {},
            "lists": {},
            "broadcasts": {},
            "blocks": {},
            "comments": {},
            "currentCostume": 0,
            "costumes": [],
            "sounds": [],
            "volume": 100,
            "layerOrder": 0,
            "tempo": 60,
            "videoTransparency": 50,
            "videoState": "on",
            "textToSpeechLanguage": None
        }

    def add_sprite(self, name="Sprite", costume_path=None):
        """添加角色"""
        sprite = Sprite(name)
        sprite._broadcasts = self.stage["broadcasts"]
        if costume_path:
            try:
                sprite.add_costume(self.asset_manager, costume_path, name)
            except Exception:
                log_message('warning',f"⚠ 素材文件未找到，精灵 [{name}] 将以无造型状态创建：{costume_path}")
                sprite.add_costume(self.asset_manager,os.path.join(os.path.dirname(os.path.abspath(__file__)),'empty.svg'),name)
        self.sprites.append(sprite)
        return sprite

    def set_backdrop(self, file_path, name="backdrop1"):
        """设置舞台背景"""
        try:
            costume_info = self.asset_manager.add_costume(file_path, name)
            self.stage["costumes"].append(costume_info)
        except Exception:
            print(f"⚠ 背景文件未找到：{file_path}")
    def save(self, output_path):
        """保存为 sb3 文件"""
        targets = [self.stage]

        for i, sprite in enumerate(self.sprites):
            try:
                target = sprite.to_dict()
                targets.append(target)
                log_message('info',f"✓ 已序列化精灵 [{sprite.name}]，积木数：{len(sprite.blocks)}，造型数：{len(sprite.costumes)}")
            except Exception as e:
                log_message('error',f"✗ 精灵 [{sprite.name}] 序列化失败，错误：{e}")
                traceback.print_exc()

        project_json = {
            "targets": targets,
            "monitors": [],
            "extensions": [],
            "meta": {
                "semver": "3.0.0",
                "vm": "0.2.0",
                "agent": "Scratch_Builder",
                "url": "https://github.com/MCPwme/Scratch_Builder"
            }
        }

        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            json_str = json.dumps(project_json, ensure_ascii=False, indent=2)
            zf.writestr('project.json', json_str.encode('utf-8'))

            for md5ext, content in self.asset_manager.get_all_assets().items():
                zf.writestr(md5ext, content)

        print(f"\n项目已保存到: {output_path}")
        print(f"包含 {len(self.sprites)} 个角色")
        print(f"包含 {len(self.asset_manager.assets)} 个素材文件")
        print(f"targets 总数: {len(targets)}（含舞台）")
