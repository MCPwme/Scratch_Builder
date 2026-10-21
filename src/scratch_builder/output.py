"""
Scratch Builder - Output System
https://github.com/MCPwme/Scratch_Builder
"""
import logging
import os
import colorlog
from datetime import datetime

def initialize_output_system(output_init=True):
    """
    Initializes the output system for logging messages to both console and file.
    """
    root_logger = logging.getLogger()
    
    # 如果已经配置过，直接返回，避免重复添加 Handler
    if root_logger.handlers:
        return
    
    root_logger.setLevel(logging.DEBUG)
    
    # --- 1. 确定日志目录和文件路径 ---
    
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    
    # 如果日志目录不存在，则创建它
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    # --- 2. 生成合法的文件名 (关键修改点) ---
    
    now = datetime.now()
    
    # 【重要】Windows 文件名不能包含 : / \ * ? " < > |
    timestamp_str = now.strftime("%Y-%m-%d %H-%M-%S")
    
    # 最终文件名例如: [2026-10-15 19-07-54]log.log
    log_filename = f"[{timestamp_str}].log"
    
    # 完整的日志文件路径
    log_file_path = os.path.join(log_dir, log_filename)
    
    # --- 3. 配置 File Handler ---
    
    try:
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        file_formatter = logging.Formatter(
            '[%(asctime)s][%(levelname)s] %(message)s',
            datefmt='%Y/%m/%d-%H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        # 如果文件创建失败（例如权限问题），打印错误但不崩溃
        print(f"Failed to create log file at {log_file_path}: {e}")
        return

    # --- 4. 配置控制台 Handler ---
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    color_formatter = colorlog.ColoredFormatter(
        '%(log_color)s[%(asctime)s][%(levelname)s] %(message)s',
        datefmt='%H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'white',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white'
        }
    )
    console_handler.setFormatter(color_formatter)
    root_logger.addHandler(console_handler)
    
    if output_init:
        logging.info('The Output System is running now.')

def log_message(level, message):
    if level == 'info':
        logging.info(message)
    elif level == 'error':
        logging.error(message)
    elif level == 'warning':
        logging.warning(message)
    elif level == 'debug':
        logging.debug(message)
    elif level == 'critical':
        logging.critical(message)
    else:
        logging.error(f'Unknown log level: {level}. Message: {message}')

def test_logging():
    log_message('info', '----------------------- Test Sample -----------------------')
    log_message('info', 'This is an info message for testing purposes.')
    log_message('error', 'This is an error message for testing purposes.')
    log_message('warning', 'This is a warning message for testing purposes.')
    log_message('debug', 'This is a debug message for testing purposes.')
    log_message('critical', 'This is a critical message for testing purposes.')
    log_message('info', '-----------------------------------------------------------')
initialize_output_system(False)