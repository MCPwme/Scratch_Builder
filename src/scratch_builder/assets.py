"""
Scratch Builder - Assets Module
https://github.com/MCPwme/Scratch_Builder
"""
import hashlib
import os

class AssetManager:
    """管理角色造型和声音素材"""
    
    def __init__(self):
        self._assets = {}
    
    def add_costume(self, file_path, name=None):
        """添加造型文件,返回 asset 信息"""
        with open(file_path, 'rb') as f:
            content = f.read()
        
        md5 = hashlib.md5(content).hexdigest()
        ext = os.path.splitext(file_path)
        md5ext = f"{md5}{ext}"
        
        self._assets[md5ext] = content
        
        return {
            "assetId": md5,
            "name": name or os.path.basename(file_path),
            "md5ext": md5ext,
            "dataFormat": ext.lstrip('.'),
            "rotationCenterX": 240,
            "rotationCenterY": 180
        }
    
    def add_sound(self, file_path, name=None):
        """添加声音文件"""
        with open(file_path, 'rb') as f:
            content = f.read()
        
        md5 = hashlib.md5(content).hexdigest()
        ext = os.path.splitext(file_path)
        md5ext = f"{md5}{ext}"
        
        self._assets[md5ext] = content
        
        return {
            "assetId": md5,
            "name": name or os.path.basename(file_path),
            "md5ext": md5ext,
            "dataFormat": ext.lstrip('.'),
            "rate": 44100,
            "sampleCount": len(content)
        }
    
    def get_all_assets(self):
        return self._assets.copy()
