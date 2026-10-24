# Scratch Builder

Scratch Builder 是一个 Python 库，可通过代码生成 Scratch 3.0 项目文件（`.sb3`）。

- 当前版本：`1.0.0.dev20261024`
- Python：`3.7` 或更高版本
- GitHub：https://github.com/MCPwme/Scratch_Builder
- PyPI：https://pypi.org/project/scratch-builder/

## 安装

从 PyPI 安装：

```bash
pip install scratch_builder
```

或者在项目根目录安装本地源码：

```bash
pip install .
```

## 快速开始

下面的示例使用项目内的 `example/cat.svg` 作为角色造型，生成 `example/hello.sb3`：

```python
from pathlib import Path

from scratch_builder import ScratchProject

example_dir = Path(__file__).resolve().parent / "example"
cat_image = example_dir / "cat.svg"

project = ScratchProject("我的第一个项目")
project.set_backdrop(str(cat_image), name="背景")

cat = project.add_sprite("主角", str(cat_image))
cat.x = 0
cat.y = 0
cat.size = 100
cat.direction = 90
cat.visible = True

(
    cat.when_flag_clicked()
    .go_to_xy(0, 0)
    .move_steps(100)
    .turn_right(90)
    .glide_to_xy(100, 50, 1)
)

project.save(str(example_dir / "hello.sb3"))
```

也可以直接运行完整示例：

```bash
python example/example.py
```

该脚本会在 `example` 目录中生成 `example.sb3`。生成的项目可以用 Scratch 3.0 网页版或离线编辑器打开。

## 项目与角色 API

### 创建项目、角色和舞台背景

```python
project = ScratchProject("项目名称")
sprite = project.add_sprite("角色名称", "造型文件.svg")
project.set_backdrop("背景文件.svg", name="背景名称")
project.save("输出文件.sb3")
```

- `ScratchProject(name="My Project")`：创建项目。
- `add_sprite(name="Sprite", costume_path=None)`：添加角色。提供造型文件路径后会加载该造型。
- `set_backdrop(file_path, name="backdrop1")`：设置舞台背景。
- `save(output_path)`：导出 `.sb3` 文件。

素材路径相对于运行脚本时的工作目录解析。示例脚本使用 `pathlib.Path(__file__)` 定位素材，便于从其他目录运行。

### 角色属性

添加角色后，可设置以下属性：

```python
sprite.x = 100
sprite.y = -50
sprite.size = 80
sprite.direction = 45
sprite.visible = True
sprite.draggable = False
sprite.rotationStyle = "all around"
```

### 事件

事件入口返回积木构建器，可继续链式调用后续积木：

```python
sprite.when_flag_clicked().move_steps(10)
sprite.when_key_pressed("space").say("开始")
sprite.when_this_sprite_clicked().change_size_by(10)
sprite.when_i_receive("完成").say("收到了")
```

另提供 `when_backdrop_switches_to(backdrop)`、`when_greater_than(menu, value)` 和
`when_i_start_as_a_clone()` 事件入口；广播可用 `broadcast(message)` 或
`broadcast_and_wait(message)` 发送。

## 当前支持的积木

### 运动

| 方法 | 用途 | 参数 |
| --- | --- | --- |
| `move_steps(steps=10)` | 移动指定步数 | `steps`：步数 |
| `turn_right(degrees=15)` | 向右转 | `degrees`：角度 |
| `turn_left(degrees=15)` | 向左转 | `degrees`：角度 |
| `go_to_xy(x=0, y=0)` | 移到坐标 | `x`, `y`：坐标 |
| `go_to(target="_random_")` | 移到角色、鼠标或随机位置 | `target`：目标 |
| `glide_to(target="_random_", seconds=1)` | 滑行到目标 | `target`：目标；`seconds`：秒数 |
| `glide_to_xy(x, y, seconds=1)` | 滑行到坐标 | `x`, `y`：坐标；`seconds`：秒数 |
| `set_x(x)` | 设置 X 坐标 | `x`：坐标 |
| `set_y(y)` | 设置 Y 坐标 | `y`：坐标 |
| `change_x_by(dx)` | 改变 X 坐标 | `dx`：变化量 |
| `change_y_by(dy)` | 改变 Y 坐标 | `dy`：变化量 |
| `point_in_direction(direction=90)` | 指向指定方向 | `direction`：角度 |
| `point_towards(target="mouse-pointer")` | 指向鼠标或指定角色 | `target`：目标名称 |
| `goto_random_position()` | 移到随机位置 | 无 |
| `if_on_edge_bounce()` | 碰到边缘时反弹 | 无 |
| `set_rotation_style(style="left-right")` | 设置旋转方式 | `style`：Scratch 旋转样式 |

### 运算报告器

当前提供以下报告器构建方法：`x_position()`、`y_position()`、`direction()`、`add(a, b)`、`subtract(a, b)`、`multiply(a, b)`、`divide(a, b)`、`pick_random(min_val, max_val)`、`greater_than(a, b)`、`less_than(a, b)`、`equals(a, b)`、`and_op(a, b)`、`or_op(a, b)`、`not_op(a)`、`join(str1, str2)`、`letter_of(index, string)`、`length_of(string)`、`contains(string, substring)`、`mod(a, b)`、`round_num(n)` 和 `math_function(operator, n)`。

`math_function` 的 `operator` 可使用 Scratch 数学运算名称，例如 `"sqrt"`、`"sin"` 或 `"abs"`。

### 侦测报告器与积木

当前提供：`touching_mouse_pointer()`、`touching_edge()`、`touching_sprite(sprite_name)`、`touching_color(color)`、`color_touching_color(color1, color2)`、`key_pressed(key)`、`mouse_down()`、`mouse_x()`、`mouse_y()`、`distance_to_mouse()`、`distance_to_sprite(sprite_name)`、`ask_and_wait(question)`、`answer()`、`get_username()`、`current_date(date_type)`、`days_since_2000()`、`loudness()`、`timer()`、`reset_timer()`、`attribute_of(property_name, object_name)` 和 `set_drag_mode(mode)`。

`key_pressed` 支持 `"space"`、方向键名称和 `"any"` 等按键值。`current_date` 的 `date_type` 可使用 `"year"`、`"month"`、`"day"`、`"hour"`、`"minute"`、`"second"` 或 `"dayofweek"`。

运算和侦测报告器可以嵌入其他积木的输入，也可作为条件或循环条件。

## 支持的 Scratch 积木

角色脚本构建器支持 Scratch 3.0 的常用内置分类：

- **运动**：移动、转向、坐标/目标移动、滑行、方向、边缘反弹、旋转样式和坐标/方向报告器。
- **外观**：说话/思考、切换造型/背景、大小、图形效果、显示/隐藏、图层以及造型/背景/大小报告器。
- **声音**：播放/等待播放、停止声音、音效、音量和音量报告器。
- **事件**：绿旗、按键、角色点击、接收广播、背景切换和数值阈值事件，以及广播积木。
- **控制**：等待、重复、一直重复、条件/双分支、等待直到、重复直到、停止、克隆/删除克隆和克隆启动事件。
- **侦测**：碰撞、按键/鼠标、距离、询问与回答、日期时间、计时器、响度、角色属性和拖动模式。
- **运算**：算术、比较、逻辑、字符串、随机数、取模、舍入和数学函数。
- **变量与列表**：创建/读取/设置/改变变量；添加、删除、插入、替换、查找、计数以及显示/隐藏列表。

条件和循环通过回调构建子脚本，条件可直接传入运算或侦测报告器。变量和列表需先在角色上创建：

```python
sprite.create_variable("分数", 0).create_list("记录")

script = sprite.when_flag_clicked()
condition = script.greater_than(script.variable("分数"), 0)
(
    script
    .move_steps(script.pick_random(2, 1))
    .repeat(3, lambda loop: loop.change_variable_by("分数", 1).move_steps(10))
    .if_then(condition, lambda branch: branch.say("分数大于零"))
    .broadcast("完成")
)
```

数值、文本及颜色值输入都可以嵌入报告器，例如
`script.move_steps(script.pick_random(2, 1))` 或
`script.touching_color(script.variable("颜色"))`；布尔报告器可以嵌套在逻辑运算或条件中，
例如 `script.if_then(script.and_op(script.key_pressed("space"), condition), lambda branch: branch.say("成立"))`。

`repeat(times, callback)`、`forever(callback)`、`if_then(condition, callback)`、
`if_else(condition, then_callback, else_callback)` 和
`repeat_until(condition, callback)` 的回调参数是该子脚本的构建器。`if_then`、
`if_else`、`wait_until` 和 `repeat_until` 的条件接受报告器，例如
`script.key_pressed("space")`、`script.greater_than(a, b)`，也接受 Python 的
`True` 和 `False`。

角色变量与列表操作方法包括 `set_variable`、`change_variable_by`、`variable`、
`add_item_to_list`、`delete_of_list`、`delete_all_of_list`、`insert_at_list`、
`replace_item_of_list`、`item_of_list`、`item_number_of_list`、`list_contains`、
`list_length`、`show_list` 和 `hide_list`。

## 许可证

MIT License
