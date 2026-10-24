"""
Scratch Builder - Sprite Module
https://github.com/MCPwme/Scratch_Builder
"""
from .blocks import Block, BlockBuilder


class Sprite:
    """Scratch 角色（精灵）"""
    
    def __init__(self, name="Sprite"):
        self.name = name
        self.blocks = {}
        self.costumes = []
        self.sounds = []
        self.variables = {}
        self.lists = {}
        self._broadcasts = {}
        self._block_id_counter = 0
        
        # 角色属性
        self.x = 0
        self.y = 0
        self.size = 100
        self.direction = 90
        self.visible = True
        self.draggable = False
        self.rotation_style = "all around"
    
    def _generate_block_id(self):
        self._block_id_counter += 1
        return f"{self.name}_{self._block_id_counter}"
    
    def _register_block(self, block):
        block_id = self._generate_block_id()
        self.blocks[block_id] = block
        block.block_id = block_id
        return block_id
    
    def add_costume(self, file_path, name=None):
        """添加造型"""
        self.costumes.append({"file_path": file_path, "name": name})
        return self
    
    def add_sound(self, file_path, name=None):
        """添加声音"""
        self.sounds.append({"file_path": file_path, "name": name})
        return self
    
    # ===== 变量管理 =====
    def create_variable(self, name, default_value=0):
        """创建变量"""
        self.variables[name] = [name, str(default_value)]
        return self
    
    def get_variable(self, name):
        """获取变量值"""
        return self.variables.get(name, [name, "0"])
    
    # ===== 列表管理 =====
    def create_list(self, name, initial_items=None):
        """创建列表"""
        self.lists[name] = [name, list(initial_items or [])]
        return self
    
    def get_list(self, name):
        """获取列表内容"""
        return self.lists.get(name, [name, []])

    def _broadcast_id(self, message):
        message = str(message)
        self._broadcasts[message] = message
        return message
    
    # ===== 事件触发积木 =====
    def when_flag_clicked(self):
        """当绿旗被点击"""
        block = Block("event_whenflagclicked")
        block.top_level = True
        self._register_block(block)
        return BlockBuilder(self, block)
    
    def when_key_pressed(self, key="space"):
        """当按下某个键"""
        block = Block("event_whenkeypressed",
            fields={"KEY_OPTION": [key, None]})
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
    
    def when_this_sprite_clicked(self):
        """当角色被点击"""
        block = Block("event_whenthisspriteclicked")
        block.top_level = True
        self._register_block(block)
        return BlockBuilder(self, block)
    
    def when_i_receive(self, message):
        """当接收到广播消息"""
        message_id = self._broadcast_id(message)
        block = Block("event_whenbroadcastreceived",
            fields={"BROADCAST_OPTION": [message, message_id]})
        block.top_level = True
        self._register_block(block)
        return BlockBuilder(self, block)

    def when_backdrop_switches_to(self, backdrop):
        block = Block("event_whenbackdropswitchesto",
            fields={"BACKDROP": [str(backdrop), None]})
        block.top_level = True
        self._register_block(block)
        return BlockBuilder(self, block)

    def when_i_start_as_a_clone(self):
        block = Block("control_start_as_clone")
        block.top_level = True
        self._register_block(block)
        return BlockBuilder(self, block)
    
    def to_dict(self, asset_manager):
        """序列化为 Scratch JSON 格式"""
        blocks_dict = {}
        for block_id, block in self.blocks.items():
            blocks_dict[block_id] = {
                "opcode": block.opcode,
                "next": block.next_block.block_id if block.next_block else None,
                "parent": block.parent_block.block_id if block.parent_block else None,
                "inputs": block.inputs,
                "fields": block.fields,
                "shadow": block.shadow,
                "topLevel": block.top_level
            }
        
        # 处理造型
        costumes_list = []
        for costume in self.costumes:
            asset_info = asset_manager.add_costume(
                costume["file_path"],
                costume.get("name")
            )
            costumes_list.append(asset_info)
        
        # 处理声音
        sounds_list = []
        for sound in self.sounds:
            asset_info = asset_manager.add_sound(
                sound["file_path"],
                sound.get("name")
            )
            sounds_list.append(asset_info)
        
        return {
            "isStage": False,
            "name": self.name,
            "variables": self.variables,
            "lists": self.lists,
            "broadcasts": self._broadcasts,
            "blocks": blocks_dict,
            "comments": {},
            "currentCostume": 0,
            "costumes": costumes_list,
            "sounds": sounds_list,
            "volume": 100,
            "layerOrder": 1,
            "visible": self.visible,
            "x": self.x,
            "y": self.y,
            "size": self.size,
            "direction": self.direction,
            "draggable": self.draggable,
            "rotationStyle": self.rotation_style
        }
