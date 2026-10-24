"""
Scratch Builder - 主程序
https://github.com/MCPwme/Scratch_Builder
"""
from .assets import AssetManager
from .blocks import Block, BlockBuilder
from .sprite import Sprite
from .project import ScratchProject
from .output import initialize_output_system, log_message
import zipfile
import json
import sys
import os
from pathlib import Path

VERSION = "1.0.0.dev20261024"
PROGRAM_NAME = "Scratch Builder"

ANSI_COLORS = {
    'purple': '\033[35m',
    'green': '\033[32m',
    'red': '\033[31m',
    'yellow': '\033[33m',
    'reset': '\033[0m'
}

initialize_output_system()


def validate_sb3(file_path):
    """
    验证 SB3 文件结构是否完整、合法

    参数:
        file_path: SB3 文件路径
    
    返回:
        dict: 包含验证结果和详细信息的字典
            - valid: bool, 是否通过验证
            - errors: list, 错误信息列表
            - warnings: list, 警告信息列表
            - info: dict, 项目基本信息
    """
    result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "info": {}
    }
    
    if not os.path.exists(file_path):
        result["valid"] = False
        result["errors"].append(f"文件不存在: {file_path}")
        return result
    
    try:
        with zipfile.ZipFile(file_path, 'r') as zf:
            file_list = set(zf.namelist())
            
            if 'project.json' not in file_list:
                result["valid"] = False
                result["errors"].append("缺少 project.json 文件")
                return result
            
            try:
                project_data = json.loads(zf.read('project.json').decode('utf-8'))
            except json.JSONDecodeError as e:
                result["valid"] = False
                result["errors"].append(f"project.json 格式错误: {str(e)}")
                return result
            except UnicodeDecodeError:
                result["valid"] = False
                result["errors"].append("project.json 编码错误,不是有效的 UTF-8 格式")
                return result
            
            required_fields = ['targets', 'monitors', 'extensions', 'meta']
            for field in required_fields:
                if field not in project_data:
                    result["valid"] = False
                    result["errors"].append(f"project.json 缺少必要字段: {field}")
            
            if not result["valid"]:
                return result
            
            meta = project_data.get('meta', {})
            if 'semver' not in meta:
                result["warnings"].append("meta 中缺少 semver 版本信息")
            if 'vm' not in meta:
                result["warnings"].append("meta 中缺少 vm 版本信息")
            
            targets = project_data['targets']
            if not targets:
                result["valid"] = False
                result["errors"].append("targets 为空,至少需要一个舞台")
                return result
            
            stage = None
            sprites = []
            for target in targets:
                if target.get('isStage', False):
                    stage = target
                else:
                    sprites.append(target)
            
            if stage is None:
                result["valid"] = False
                result["errors"].append("缺少舞台 (isStage=true 的 target)")
            else:
                stage_required = ['name', 'costumes', 'sounds', 'volume', 'tempo']
                for field in stage_required:
                    if field not in stage:
                        result["warnings"].append(f"舞台缺少字段: {field}")
            
            for i, sprite in enumerate(sprites):
                sprite_name = sprite.get('name', f'角色{i+1}')
                sprite_required = ['name', 'costumes', 'sounds', 'volume', 'x', 'y', 
                                   'size', 'direction', 'visible', 'rotationStyle']
                for field in sprite_required:
                    if field not in sprite:
                        result["warnings"].append(f"角色 '{sprite_name}' 缺少字段: {field}")
            
            all_md5exts = set()
            for target in targets:
                for costume in target.get('costumes', []):
                    if 'md5ext' in costume:
                        all_md5exts.add(costume['md5ext'])
                    else:
                        result["warnings"].append(
                            f"目标 '{target.get('name', '未知')}' 的造型缺少 md5ext"
                        )
                
                for sound in target.get('sounds', []):
                    if 'md5ext' in sound:
                        all_md5exts.add(sound['md5ext'])
                    else:
                        result["warnings"].append(
                            f"目标 '{target.get('name', '未知')}' 的声音缺少 md5ext"
                        )
            
            for md5ext in all_md5exts:
                if md5ext not in file_list:
                    result["valid"] = False
                    result["errors"].append(f"引用的素材文件不存在: {md5ext}")
            
            result["info"] = {
                "文件名": os.path.basename(file_path),
                "文件大小": f"{os.path.getsize(file_path) / 1024:.1f} KB",
                "项目名称": stage.get('name', '未命名') if stage else '未知',
                "角色数量": len(sprites),
                "造型总数": sum(len(t.get('costumes', [])) for t in targets),
                "声音总数": sum(len(t.get('sounds', [])) for t in targets),
                "素材文件数": len(all_md5exts),
                "ZIP 内文件数": len(file_list),
                "Scratch 版本": meta.get('semver', '未知'),
                "VM 版本": meta.get('vm', '未知')
            }
            
    except zipfile.BadZipFile:
        result["valid"] = False
        result["errors"].append("不是有效的 ZIP 文件,文件可能已损坏")
    except PermissionError:
        result["valid"] = False
        result["errors"].append("没有权限读取文件")
    except Exception as e:
        result["valid"] = False
        result["errors"].append(f"验证过程发生异常: {str(e)}")
    
    return result


def log_message_validation_result(result):
    """格式化输出验证结果"""
    log_message('info', "=" * 50)
    log_message('info', "SB3 文件验证报告")
    log_message('info', "=" * 50)
    
    if result["valid"]:
        log_message('info', f"{ANSI_COLORS['green']}验证通过:文件结构正常{ANSI_COLORS['reset']}")
    else:
        log_message('error', "验证失败:文件存在问题")
    
    if result["errors"]:
        log_message('error', f"错误({len(result['errors'])}个):")
        for error in result["errors"]:
            log_message('error', f"  • {error}")
    
    if result["warnings"]:
        log_message('warning', f"警告({len(result['warnings'])}个):")
        for warning in result["warnings"]:
            log_message('warning', f"  • {warning}")
    
    if result["info"]:
        log_message('info', "项目信息:")
        for key, value in result["info"].items():
            log_message('info', f"  {key}: {value}")
    
    log_message('info', "=" * 50)


def show_help():
    """显示帮助信息"""
    log_message('info', f"\n{PROGRAM_NAME} [V {VERSION}]")
    log_message('info', "\n使用说明:")
    log_message('info', "  scratch_builder.py [选项] [参数]")
    log_message('info', "\n命令行选项:")
    log_message('info', "  /help              - 显示此帮助信息")
    log_message('info', "  /version           - 显示版本信息")
    log_message('info', "  /build <file>      - 构建 Scratch 项目")
    log_message('info', "  /validate <file>   - 验证 SB3 文件")
    log_message('info', "  /cmd               - 进入交互模式")
    log_message('info', "\n交互模式命令:")
    log_message('info', "  /help              - 显示帮助信息")
    log_message('info', "  /exit              - 退出程序")
    log_message('info', "  /version           - 显示版本信息")
    log_message('info', "  /build <file>      - 构建 Scratch 项目")
    log_message('info', "  /validate <file>   - 验证 SB3 文件")
    log_message('info', "")


def show_version():
    """显示版本信息"""
    log_message('info', f"{PROGRAM_NAME} version: {VERSION}")


def handle_build(file_path=None):
    """处理构建项目命令"""
    if not file_path:
        file_path = input("请输入 Scratch 项目文件路径: ").strip()
    
    if not file_path:
        log_message('error', "文件路径不能为空")
        return
    
    file_path = Path(file_path)
    
    if not file_path.suffix:
        file_path = file_path.with_suffix('.sb3')
    
    log_message('info', f"正在构建 Scratch 项目: {file_path}")
    
    try:
        project = ScratchProject()
        project.save(str(file_path))
        log_message('info', f"{ANSI_COLORS['green']}✓ 项目构建成功: {file_path}{ANSI_COLORS['reset']}")
    except PermissionError:
        log_message('error', f"没有权限写入文件: {file_path}")
    except OSError as e:
        log_message('error', f"文件系统错误: {e}")
    except Exception as e:
        log_message('error', f"构建项目失败: {e}")


def handle_validate(file_path=None):
    """处理验证 SB3 文件命令"""
    if not file_path:
        file_path = input("请输入 SB3 文件路径: ").strip()
    
    if not file_path:
        log_message('error', "文件路径不能为空")
        return
    
    log_message('info', f"正在验证 SB3 文件: {file_path}")
    
    try:
        validation_result = validate_sb3(file_path)
        log_message_validation_result(validation_result)
    except Exception as e:
        log_message('error', f"验证过程发生错误: {e}")


def interactive_mode():
    """交互式命令处理"""
    log_message('info', f"{ANSI_COLORS['purple']}进入交互模式 (输入 /help 查看可用命令){ANSI_COLORS['reset']}")
    
    command_handlers = {
        '/help': lambda _: show_help(),
        '/exit': lambda _: sys.exit(0),
        '/version': lambda _: show_version(),
        '/build': lambda args: handle_build(args[0] if args else None),
        '/validate': lambda args: handle_validate(args[0] if args else None),
    }
    
    while True:
        try:
            user_input = input(f"{ANSI_COLORS['purple']}>>> {ANSI_COLORS['reset']}").strip()
            
            if not user_input:
                continue
            
            parts = user_input.split()
            command = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            handler = command_handlers.get(command)
            
            if handler:
                handler(args)
            else:
                log_message('error', f"未知命令: '{command}'. 输入 /help 查看可用命令")
        
        except KeyboardInterrupt:
            log_message('info', "\n使用 /exit 退出程序")
        except EOFError:
            log_message('info', "\n再见!")
            break


def parse_command_line_args():
    """解析命令行参数"""
    if len(sys.argv) <= 1:
        return None, None
    
    command = sys.argv[1].lower()
    
    if command in ['/help', '--help', '-h']:
        return 'help', None
    elif command in ['/version', '--version', '-v']:
        return 'version', None
    elif command == '/build':
        if len(sys.argv) > 2:
            return 'build', sys.argv[2]
        else:
            log_message('error', "请提供文件路径: scratch_builder.py /build <file>")
            sys.exit(1)
    elif command == '/validate':
        if len(sys.argv) > 2:
            return 'validate', sys.argv[2]
        else:
            log_message('error', "请提供文件路径: scratch_builder.py /validate <file>")
            sys.exit(1)
    elif command == '/cmd':
        return 'interactive', None
    else:
        log_message('error', f"未知命令行参数: {command}")
        show_help()
        sys.exit(1)


def main():
    """主程序入口"""
    command, arg = parse_command_line_args()
    
    if command == 'help':
        show_help()
    elif command == 'version':
        show_version()
    elif command == 'build':
        handle_build(arg)
    elif command == 'validate':
        handle_validate(arg)
    elif command == 'interactive' or command is None:
        interactive_mode()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log_message('info', "\n程序被中断,再见!")
        sys.exit(0)
    except Exception as e:
        log_message('error', f"程序发生严重错误: {e}")
        sys.exit(1)