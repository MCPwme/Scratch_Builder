"""
Scratch Builder - Block Builder
https://github.com/MCPwme/Scratch_Builder
"""
import uuid

class Block:
    """单个积木的表示"""

    def __init__(self, opcode, inputs=None, fields=None):
        self.opcode = opcode
        self.inputs = inputs or {}
        self.fields = fields or {}
        self.next_block = None
        self.parent_block = None
        self.shadow = False
        self.top_level = False
        self.block_id = str(uuid.uuid4()).replace('-', '')[:16]
    
    def set_next(self, block):
        self.next_block = block
        if block:
            block.parent_block = self
        return block

class BlockBuilder:
    """积木构建器,支持链式调用"""
    
    def __init__(self, sprite, first_block):
        self.sprite = sprite
        self.current_block = first_block

    @staticmethod
    def _literal(value, value_type=4):
        if isinstance(value, (BlockBuilder, Block)):
            return [1, value]
        return [1, [value_type, str(value)]]

    def _prepare_inputs(self, block, inputs):
        prepared = {}
        for name, value in (inputs or {}).items():
            if (isinstance(value, (list, tuple)) and len(value) == 2
                    and isinstance(value[1], (BlockBuilder, Block))):
                child_value = value[1]
                child = child_value.current_block if isinstance(child_value, BlockBuilder) else child_value
                child.parent_block = block
                child.shadow = False
                prepared[name] = [value[0], child.block_id]
                continue
            if isinstance(value, BlockBuilder):
                child = value.current_block
                child.parent_block = block
                child.shadow = False
                prepared[name] = [1, child.block_id]
            elif isinstance(value, Block):
                value.parent_block = block
                value.shadow = False
                prepared[name] = [1, value.block_id]
            else:
                prepared[name] = value
        return prepared

    def _set_menu_input(self, block, input_name, menu_opcode, field_name, value):
        menu = Block(menu_opcode, fields={field_name: [str(value), None]})
        menu.shadow = True
        menu.parent_block = block
        self.sprite._register_block(menu)
        block.inputs[input_name] = [1, menu.block_id]
    
    def _add_block(self, opcode, inputs=None, fields=None):
        """在当前积木后添加新积木"""
        new_block = Block(opcode, inputs, fields)
        new_block.inputs = self._prepare_inputs(new_block, new_block.inputs)
        self.sprite._register_block(new_block)
        if getattr(self, "_branch_pending", False):
            new_block.parent_block = self._branch_block
            self._branch_block.inputs[self._branch_input] = [2, new_block.block_id]
            self._branch_pending = False
        else:
            self.current_block.set_next(new_block)
        self.current_block = new_block
        return self
    
    def _create_reporter_block(self, opcode, inputs=None, fields=None):
        """创建报告器积木（返回值积木），不连接到积木链，返回 BlockBuilder 以便嵌套调用"""
        new_block = Block(opcode, inputs, fields)
        new_block.inputs = self._prepare_inputs(new_block, new_block.inputs)
        new_block.shadow = True
        self.sprite._register_block(new_block)
        return BlockBuilder(self.sprite, new_block)

    def _build_substack(self, block, input_name, callback):
        if not callable(callback):
            raise TypeError("{} must be callable".format(input_name))
        branch = BlockBuilder(self.sprite, block)
        branch._branch_block = block
        branch._branch_input = input_name
        branch._branch_pending = True
        callback(branch)
        first = block.inputs.get(input_name)
        if first:
            return first[1]
        return None

    @staticmethod
    def _validate_callbacks(*callbacks):
        if any(not callable(callback) for callback in callbacks):
            raise TypeError("Control block bodies must be callable")
    
    # ===== 运动类积木 =====
    def move_steps(self, steps=10):
        return self._add_block("motion_movesteps",
            inputs={"STEPS": self._literal(steps)})
    
    def turn_right(self, degrees=15):
        return self._add_block("motion_turnright",
            inputs={"DEGREES": self._literal(degrees)})
    
    def turn_left(self, degrees=15):
        return self._add_block("motion_turnleft",
            inputs={"DEGREES": self._literal(degrees)})
    
    def go_to_xy(self, x=0, y=0):
        return self._add_block("motion_gotoxy",
            inputs={
                "X": self._literal(x),
                "Y": self._literal(y)
            })

    def go_to(self, target="random position"):
        self._add_block("motion_goto")
        self._set_menu_input(
            self.current_block, "TO", "motion_goto_menu", "TO", target)
        return self

    def glide_to(self, target="random position", seconds=1):
        self._add_block("motion_glideto",
            inputs={"SECS": self._literal(seconds)})
        self._set_menu_input(
            self.current_block, "TO", "motion_glideto_menu", "TO", target)
        return self
    
    def glide_to_xy(self, x, y, seconds=1):
        return self._add_block("motion_glidesecstoxy",
            inputs={
                "X": self._literal(x),
                "Y": self._literal(y),
                "SECS": self._literal(seconds)
            })
    
    def set_x(self, x):
        return self._add_block("motion_setx",
            inputs={"X": self._literal(x)})
    
    def set_y(self, y):
        return self._add_block("motion_sety",
            inputs={"Y": self._literal(y)})
    
    def change_x_by(self, dx):
        return self._add_block("motion_changexby",
            inputs={"DX": self._literal(dx)})
    
    def change_y_by(self, dy):
        return self._add_block("motion_changeyby",
            inputs={"DY": self._literal(dy)})
    
    def point_in_direction(self, direction=90):
        return self._add_block("motion_pointindirection",
            inputs={"DIRECTION": self._literal(direction)})
    
    def point_towards(self, target="mouse-pointer"):
        self._add_block("motion_pointtowards")
        self._set_menu_input(
            self.current_block, "TOWARDS", "motion_pointtowards_menu", "TOWARDS", target)
        return self
    
    def goto_random_position(self):
        return self.go_to("random position")
    
    def if_on_edge_bounce(self):
        return self._add_block("motion_ifonedgebounce")
    
    def set_rotation_style(self, style="left-right"):
        return self._add_block("motion_setrotationstyle",
            fields={"STYLE": [style, None]})
    
    def x_position(self):
        """x 坐标 - 返回报告器积木"""
        return self._create_reporter_block("motion_xposition")
    
    def y_position(self):
        """y 坐标 - 返回报告器积木"""
        return self._create_reporter_block("motion_yposition")
    
    def direction(self):
        """方向 - 返回报告器积木"""
        return self._create_reporter_block("motion_direction")

    # ===== 运算类积木 (Operators) =====
    def add(self, a, b):
        """a + b - 返回报告器积木"""
        return self._create_reporter_block("operator_add",
            inputs={
                "NUM1": self._literal(a),
                "NUM2": self._literal(b)
            })
    
    def subtract(self, a, b):
        """a - b - 返回报告器积木"""
        return self._create_reporter_block("operator_subtract",
            inputs={
                "NUM1": self._literal(a),
                "NUM2": self._literal(b)
            })
    
    def multiply(self, a, b):
        """a * b - 返回报告器积木"""
        return self._create_reporter_block("operator_multiply",
            inputs={
                "NUM1": self._literal(a),
                "NUM2": self._literal(b)
            })
    
    def divide(self, a, b):
        """a / b - 返回报告器积木"""
        return self._create_reporter_block("operator_divide",
            inputs={
                "NUM1": self._literal(a),
                "NUM2": self._literal(b)
            })
    
    def pick_random(self, min_val, max_val):
        """在 min 和 max 之间取随机数 - 返回报告器积木"""
        return self._create_reporter_block("operator_random",
            inputs={
                "FROM": self._literal(min_val),
                "TO": self._literal(max_val)
            })
    
    def greater_than(self, a, b):
        """a > b - 返回报告器积木"""
        return self._create_reporter_block("operator_gt",
            inputs={
                "OPERAND1": self._literal(a),
                "OPERAND2": self._literal(b)
            })
    
    def less_than(self, a, b):
        """a < b - 返回报告器积木"""
        return self._create_reporter_block("operator_lt",
            inputs={
                "OPERAND1": self._literal(a),
                "OPERAND2": self._literal(b)
            })
    
    def equals(self, a, b):
        """a = b - 返回报告器积木"""
        return self._create_reporter_block("operator_equals",
            inputs={
                "OPERAND1": self._literal(a),
                "OPERAND2": self._literal(b)
            })
    
    def and_op(self, a, b):
        """a 且 b - 返回报告器积木"""
        return self._create_reporter_block("operator_and",
            inputs={
                "OPERAND1": self._literal(a),
                "OPERAND2": self._literal(b)
            })
    
    def or_op(self, a, b):
        """a 或 b - 返回报告器积木"""
        return self._create_reporter_block("operator_or",
            inputs={
                "OPERAND1": self._literal(a),
                "OPERAND2": self._literal(b)
            })
    
    def not_op(self, a):
        """非 a - 返回报告器积木"""
        return self._create_reporter_block("operator_not",
            inputs={"OPERAND": self._literal(a)})
    
    def join(self, str1, str2):
        """连接字符串 - 返回报告器积木"""
        return self._create_reporter_block("operator_join",
            inputs={
                "STRING1": self._literal(str1, 10),
                "STRING2": self._literal(str2, 10)
            })
    
    def letter_of(self, index, string):
        """字符串的第 index 个字符 - 返回报告器积木"""
        return self._create_reporter_block("operator_letter_of",
            inputs={
                "LETTER": self._literal(index),
                "STRING": self._literal(string, 10)
            })
    
    def length_of(self, string):
        """字符串长度 - 返回报告器积木"""
        return self._create_reporter_block("operator_length",
            inputs={"STRING": self._literal(string, 10)})
    
    def contains(self, string, substring):
        """... 包含 ... ? - 返回报告器积木"""
        return self._create_reporter_block("operator_contains",
            inputs={
                "STRING1": self._literal(string, 10),
                "STRING2": self._literal(substring, 10)
            })
    
    def mod(self, a, b):
        """a mod b - 返回报告器积木"""
        return self._create_reporter_block("operator_mod",
            inputs={
                "NUM1": self._literal(a),
                "NUM2": self._literal(b)
            })
    
    def round_num(self, n):
        """四舍五入 - 返回报告器积木"""
        return self._create_reporter_block("operator_round",
            inputs={"NUM": self._literal(n)})
    
    def math_function(self, operator, n):
        """数学函数: abs, floor, ceiling, sqrt, sin, cos, tan, asin, acos, atan, ln, log, e^, 10^ - 返回报告器积木"""
        return self._create_reporter_block("operator_mathop",
            inputs={"NUM": self._literal(n)},
            fields={"OPERATOR": [operator, None]})

    # ===== 侦测类积木 (Sensing) =====
    def touching_mouse_pointer(self):
        """碰到鼠标指针? - 返回报告器积木"""
        reporter = self._create_reporter_block("sensing_touchingobject")
        self._set_menu_input(
            reporter.current_block, "TOUCHINGOBJECTMENU", "sensing_touchingobjectmenu",
            "TOUCHINGOBJECTMENU", "_mouse_")
        return reporter
    
    def touching_edge(self):
        """碰到边缘? - 返回报告器积木"""
        reporter = self._create_reporter_block("sensing_touchingobject")
        self._set_menu_input(
            reporter.current_block, "TOUCHINGOBJECTMENU", "sensing_touchingobjectmenu",
            "TOUCHINGOBJECTMENU", "_edge_")
        return reporter
    
    def touching_sprite(self, sprite_name):
        """碰到指定角色? - 返回报告器积木"""
        reporter = self._create_reporter_block("sensing_touchingobject")
        self._set_menu_input(
            reporter.current_block, "TOUCHINGOBJECTMENU", "sensing_touchingobjectmenu",
            "TOUCHINGOBJECTMENU", sprite_name)
        return reporter
    
    def key_pressed(self, key):
        """按下指定键? - 返回报告器积木"""
        key_map = {
            "space": "space",
            "up arrow": "up arrow",
            "down arrow": "down arrow",
            "right arrow": "right arrow",
            "left arrow": "left arrow",
            "any": "any"
        }
        actual_key = key_map.get(key.lower(), key)
        reporter = self._create_reporter_block("sensing_keypressed")
        self._set_menu_input(
            reporter.current_block, "KEY_OPTION", "sensing_keyoptions", "KEY_OPTION", actual_key)
        return reporter
    
    def mouse_down(self):
        """鼠标按下? - 返回报告器积木"""
        return self._create_reporter_block("sensing_mousedown")
    
    def mouse_x(self):
        """鼠标的 x 坐标 - 返回报告器积木"""
        return self._create_reporter_block("sensing_mousex")
    
    def mouse_y(self):
        """鼠标的 y 坐标 - 返回报告器积木"""
        return self._create_reporter_block("sensing_mousey")
    
    def distance_to_mouse(self):
        """到鼠标指针的距离 - 返回报告器积木"""
        reporter = self._create_reporter_block("sensing_distanceto")
        self._set_menu_input(
            reporter.current_block, "DISTANCETOMENU", "sensing_distancetomenu",
            "DISTANCETOMENU", "_mouse_")
        return reporter
    
    def distance_to_sprite(self, sprite_name):
        """到指定角色的距离 - 返回报告器积木"""
        reporter = self._create_reporter_block("sensing_distanceto")
        self._set_menu_input(
            reporter.current_block, "DISTANCETOMENU", "sensing_distancetomenu",
            "DISTANCETOMENU", sprite_name)
        return reporter
    
    def ask_and_wait(self, question):
        """询问...并等待"""
        return self._add_block("sensing_askandwait",
            inputs={"QUESTION": self._literal(question, 10)})
    
    def answer(self):
        """获取回答 - 返回报告器积木"""
        return self._create_reporter_block("sensing_answer")
    
    def get_username(self):
        """获取用户名 - 返回报告器积木"""
        return self._create_reporter_block("sensing_username")
    
    def current_date(self, date_type):
        """获取当前日期时间: year, month, day, hour, minute, second, dayofweek - 返回报告器积木"""
        return self._create_reporter_block("sensing_current",
            fields={"CURRENTMENU": [date_type, None]})
    
    def days_since_2000(self):
        """2000年至今的天数 - 返回报告器积木"""
        return self._create_reporter_block("sensing_dayssince2000")

    # ===== 外观类积木 =====
    def say(self, message):
        return self._add_block("looks_say",
            inputs={"MESSAGE": self._literal(message, 10)})

    def say_for_seconds(self, message, seconds=2):
        return self._add_block("looks_sayforsecs",
            inputs={
                "MESSAGE": self._literal(message, 10),
                "SECS": self._literal(seconds)
            })

    def think(self, message):
        return self._add_block("looks_think",
            inputs={"MESSAGE": self._literal(message, 10)})

    def think_for_seconds(self, message, seconds=2):
        return self._add_block("looks_thinkforsecs",
            inputs={
                "MESSAGE": self._literal(message, 10),
                "SECS": self._literal(seconds)
            })

    def switch_costume(self, costume):
        self._add_block("looks_switchcostumeto")
        self._set_menu_input(
            self.current_block, "COSTUME", "looks_costume", "COSTUME", costume)
        return self

    def next_costume(self):
        return self._add_block("looks_nextcostume")

    def switch_backdrop(self, backdrop):
        self._add_block("looks_switchbackdropto")
        self._set_menu_input(
            self.current_block, "BACKDROP", "looks_backdrops", "BACKDROP", backdrop)
        return self

    def switch_backdrop_and_wait(self, backdrop):
        self._add_block("looks_switchbackdroptoandwait")
        self._set_menu_input(
            self.current_block, "BACKDROP", "looks_backdrops", "BACKDROP", backdrop)
        return self

    def next_backdrop(self):
        return self._add_block("looks_nextbackdrop")

    def change_size_by(self, amount):
        return self._add_block("looks_changesizeby",
            inputs={"CHANGE": self._literal(amount)})

    def set_size_to(self, percent):
        return self._add_block("looks_setsizeto",
            inputs={"SIZE": self._literal(percent)})

    def change_effect_by(self, effect, amount):
        return self._add_block("looks_changeeffectby",
            inputs={"CHANGE": self._literal(amount)},
            fields={"EFFECT": [effect, None]})

    def set_effect_to(self, effect, value):
        return self._add_block("looks_seteffectto",
            inputs={"VALUE": self._literal(value)},
            fields={"EFFECT": [effect, None]})

    def clear_graphic_effects(self):
        return self._add_block("looks_cleargraphiceffects")

    def show(self):
        return self._add_block("looks_show")

    def hide(self):
        return self._add_block("looks_hide")

    def go_to_front_back(self, direction="front"):
        return self._add_block("looks_gotofrontback",
            fields={"FRONT_BACK": [direction, None]})

    def go_forward_layers(self, direction, layers=1):
        return self._add_block("looks_goforwardbackwardlayers",
            inputs={"NUM": self._literal(layers)},
            fields={"FORWARD_BACKWARD": [direction, None]})

    def costume_number_or_name(self, number_name="number"):
        return self._create_reporter_block("looks_costumenumbername",
            fields={"NUMBER_NAME": [number_name, None]})

    def backdrop_number_or_name(self, number_name="number"):
        return self._create_reporter_block("looks_backdropnumbername",
            fields={"NUMBER_NAME": [number_name, None]})

    def size(self):
        return self._create_reporter_block("looks_size")

    # ===== 声音类积木 =====
    def play_sound(self, sound):
        self._add_block("sound_play")
        self._set_menu_input(
            self.current_block, "SOUND_MENU", "sound_sounds_menu", "SOUND_MENU", sound)
        return self

    def play_sound_until_done(self, sound):
        self._add_block("sound_playuntildone")
        self._set_menu_input(
            self.current_block, "SOUND_MENU", "sound_sounds_menu", "SOUND_MENU", sound)
        return self

    def stop_all_sounds(self):
        return self._add_block("sound_stopallsounds")

    def change_sound_effect_by(self, effect, amount):
        return self._add_block("sound_changeeffectby",
            inputs={"VALUE": self._literal(amount)},
            fields={"EFFECT": [effect, None]})

    def set_sound_effect_to(self, effect, value):
        return self._add_block("sound_seteffectto",
            inputs={"VALUE": self._literal(value)},
            fields={"EFFECT": [effect, None]})

    def clear_sound_effects(self):
        return self._add_block("sound_cleareffects")

    def change_volume_by(self, amount):
        return self._add_block("sound_changevolumeby",
            inputs={"VOLUME": self._literal(amount)})

    def set_volume_to(self, volume):
        return self._add_block("sound_setvolumeto",
            inputs={"VOLUME": self._literal(volume)})

    def volume(self):
        return self._create_reporter_block("sound_volume")

    # ===== 事件广播积木 =====
    def broadcast(self, message):
        message_id = self.sprite._broadcast_id(message) if hasattr(self.sprite, "_broadcast_id") else str(message)
        return self._add_block("event_broadcast",
            inputs={"BROADCAST_INPUT": [1, [11, str(message), message_id]]})

    def broadcast_and_wait(self, message):
        message_id = self.sprite._broadcast_id(message) if hasattr(self.sprite, "_broadcast_id") else str(message)
        return self._add_block("event_broadcastandwait",
            inputs={"BROADCAST_INPUT": [1, [11, str(message), message_id]]})

    # ===== 控制类积木 =====
    def wait(self, seconds):
        return self._add_block("control_wait",
            inputs={"DURATION": self._literal(seconds)})

    def repeat(self, times, callback):
        self._validate_callbacks(callback)
        block = Block("control_repeat",
            inputs={"TIMES": self._literal(times)})
        block.inputs = self._prepare_inputs(block, block.inputs)
        self.current_block.set_next(block)
        self.sprite._register_block(block)
        self.current_block = block
        self._build_substack(block, "SUBSTACK", callback)
        return self

    def forever(self, callback):
        self._validate_callbacks(callback)
        block = Block("control_forever")
        self.current_block.set_next(block)
        self.sprite._register_block(block)
        self.current_block = block
        self._build_substack(block, "SUBSTACK", callback)
        return self

    def if_then(self, condition, callback):
        self._validate_callbacks(callback)
        block = Block("control_if",
            inputs={"CONDITION": [2, condition]})
        block.inputs = self._prepare_inputs(block, block.inputs)
        self.current_block.set_next(block)
        self.sprite._register_block(block)
        self.current_block = block
        self._build_substack(block, "SUBSTACK", callback)
        return self

    def if_else(self, condition, then_callback, else_callback):
        self._validate_callbacks(then_callback, else_callback)
        block = Block("control_if_else",
            inputs={"CONDITION": [2, condition]})
        block.inputs = self._prepare_inputs(block, block.inputs)
        self.current_block.set_next(block)
        self.sprite._register_block(block)
        self.current_block = block
        self._build_substack(block, "SUBSTACK", then_callback)
        self._build_substack(block, "SUBSTACK2", else_callback)
        return self

    def wait_until(self, condition):
        return self._add_block("control_wait_until",
            inputs={"CONDITION": [2, condition]})

    def repeat_until(self, condition, callback):
        self._validate_callbacks(callback)
        block = Block("control_repeat_until",
            inputs={"CONDITION": [2, condition]})
        block.inputs = self._prepare_inputs(block, block.inputs)
        self.current_block.set_next(block)
        self.sprite._register_block(block)
        self.current_block = block
        self._build_substack(block, "SUBSTACK", callback)
        return self

    def stop(self, option="all"):
        return self._add_block("control_stop",
            fields={"STOP_OPTION": [option, None]})

    def create_clone(self, target="_myself_"):
        self._add_block("control_create_clone_of")
        self._set_menu_input(
            self.current_block, "CLONE_OPTION", "control_create_clone_of_menu",
            "CLONE_OPTION", target)
        return self

    def delete_clone(self):
        return self._add_block("control_delete_this_clone")

    # ===== 变量与列表积木 =====
    def _variable_field(self, name):
        if name not in self.sprite.variables:
            raise KeyError("Variable {!r} has not been created".format(name))
        return {"VARIABLE": [name, name]}

    def set_variable(self, name, value):
        return self._add_block("data_setvariableto",
            inputs={"VALUE": self._literal(value, 10)},
            fields=self._variable_field(name))

    def change_variable_by(self, name, amount):
        return self._add_block("data_changevariableby",
            inputs={"VALUE": self._literal(amount)},
            fields=self._variable_field(name))

    def variable(self, name):
        return self._create_reporter_block("data_variable",
            fields=self._variable_field(name))

    def _list_field(self, name):
        if name not in self.sprite.lists:
            raise KeyError("List {!r} has not been created".format(name))
        return {"LIST": [name, name]}

    def add_item_to_list(self, name, item):
        return self._add_block("data_addtolist",
            inputs={"ITEM": self._literal(item, 10)},
            fields=self._list_field(name))

    def delete_of_list(self, name, index):
        return self._add_block("data_deleteoflist",
            inputs={"INDEX": self._literal(index, 10)},
            fields=self._list_field(name))

    def delete_all_of_list(self, name):
        return self._add_block("data_deletealloflist",
            fields=self._list_field(name))

    def insert_at_list(self, name, item, index):
        return self._add_block("data_insertatlist",
            inputs={
                "ITEM": self._literal(item, 10),
                "INDEX": self._literal(index, 10)
            },
            fields=self._list_field(name))

    def replace_item_of_list(self, name, index, item):
        return self._add_block("data_replaceitemoflist",
            inputs={
                "INDEX": self._literal(index, 10),
                "ITEM": self._literal(item, 10)
            },
            fields=self._list_field(name))

    def item_of_list(self, name, index):
        return self._create_reporter_block("data_itemoflist",
            inputs={"INDEX": self._literal(index, 10)},
            fields=self._list_field(name))

    def item_number_of_list(self, name, item):
        return self._create_reporter_block("data_itemnumoflist",
            inputs={"ITEM": self._literal(item, 10)},
            fields=self._list_field(name))

    def list_contains(self, name, item):
        return self._create_reporter_block("data_listcontainsitem",
            inputs={"ITEM": self._literal(item, 10)},
            fields=self._list_field(name))

    def list_length(self, name):
        return self._create_reporter_block("data_lengthoflist",
            fields=self._list_field(name))

    def show_list(self, name):
        return self._add_block("data_showlist", fields=self._list_field(name))

    def hide_list(self, name):
        return self._add_block("data_hidelist", fields=self._list_field(name))

    # ===== 其余侦测积木 =====
    def touching_color(self, color):
        return self._create_reporter_block("sensing_touchingcolor",
            inputs={"COLOR": [1, [9, str(color)]]})

    def color_touching_color(self, color1, color2):
        return self._create_reporter_block("sensing_coloristouchingcolor",
            inputs={
                "COLOR": [1, [9, str(color1)]],
                "COLOR2": [1, [9, str(color2)]]
            })

    def loudness(self):
        return self._create_reporter_block("sensing_loudness")

    def timer(self):
        return self._create_reporter_block("sensing_timer")

    def reset_timer(self):
        return self._add_block("sensing_resettimer")

    def attribute_of(self, property_name, object_name):
        reporter = self._create_reporter_block("sensing_of",
            fields={"PROPERTY": [property_name, None]})
        self._set_menu_input(
            reporter.current_block, "OBJECT", "sensing_of_object_menu", "OBJECT", object_name)
        return reporter

    def set_drag_mode(self, mode="draggable"):
        return self._add_block("sensing_setdragmode",
            fields={"DRAG_MODE": [mode, None]})