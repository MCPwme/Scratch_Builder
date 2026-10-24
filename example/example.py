"""
Scratch Builder 综合示例
运行后会在当前目录生成 example.sb3需要先安装 scratch_builder
https://github.com/MCPwme/Scratch_Builder
"""
from pathlib import Path

from scratch_builder import ScratchProject


def add_cat(project, image_path, name, x, y, size, direction):
    """添加猫咪角色并设置初始属性。"""
    sprite = project.add_sprite(name, str(image_path))
    sprite.x = x
    sprite.y = y
    sprite.size = size
    sprite.direction = direction
    sprite.visible = True
    sprite.draggable = False
    sprite.rotationStyle = "left-right"
    return sprite


def build_project():
    example_dir = Path(__file__).resolve().parent
    cat_image = example_dir / "cat.svg"
    output_file = example_dir / "example.sb3"

    project = ScratchProject("Scratch Builder 综合示例")
    project.set_backdrop(str(cat_image), name="猫咪背景")

    # 绿旗脚本：移动、转向、滑行和边缘反弹。
    cat = add_cat(project, cat_image, "主角猫", -120, -40, 80, 90)
    (
        cat.when_flag_clicked()
        .go_to_xy(-120, -40)
        .point_in_direction(90)
        .move_steps(80)
        .turn_right(90)
        .move_steps(50)
        .if_on_edge_bounce()
        .glide_to_xy(0, 0, 1)
        .set_rotation_style("left-right")
    )

    # 第二个角色展示 X/Y 坐标操作、随机位置和指向目标。
    target = add_cat(project, cat_image, "目标猫", 120, 60, 60, -90)
    (
        target.when_flag_clicked()
        .set_x(120)
        .set_y(60)
        .change_x_by(-20)
        .change_y_by(-10)
        .point_towards("_mouse_")
        .go_to("_random_")
        .if_on_edge_bounce()
    )

    # 将项目导出为 Scratch 3.0 的 .sb3 文件。
    project.save(str(output_file))
    return output_file


if __name__ == "__main__":
    saved_file = build_project()
    print("示例项目已生成：{}".format(saved_file))
