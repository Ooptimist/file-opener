"""
group_manager.py
文件组管理模块

负责文件组的加载、保存、添加、删除等操作
文件组数据以 JSON 格式存储
"""

import os
import json
from ..defines import get_groups_file_path


class GroupManager:
    """
    文件组管理器
    
    管理文件组的持久化存储和内存操作
    """
    
    def __init__(self):
        """
        初始化文件组管理器
        """
        self.groups_file = get_groups_file_path()
        self.groups = {}
        self.load()
    
    def load(self):
        """
        从文件加载文件组数据
        
        如果文件不存在或解析失败，则初始化为空字典
        """
        if os.path.exists(self.groups_file):
            try:
                with open(self.groups_file, 'r', encoding='utf-8') as f:
                    self.groups = json.load(f)
            except Exception as e:
                print(f"加载文件组失败: {e}")
                self.groups = {}
        else:
            self.groups = {}
    
    def save(self):
        """
        保存文件组数据到文件
        
        Returns:
            bool: 是否保存成功
        """
        try:
            with open(self.groups_file, 'w', encoding='utf-8') as f:
                json.dump(self.groups, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存文件组失败: {e}")
            return False
    
    def add_group(self, name, files):
        """
        添加新的文件组
        
        Args:
            name (str): 文件组名称
            files (list): 文件路径列表
        
        Returns:
            bool: 是否添加成功
        """
        if not name or not files:
            return False
        
        self.groups[name] = list(files)  # 创建副本
        return self.save()
    
    def delete_group(self, name):
        """
        删除文件组
        
        Args:
            name (str): 文件组名称
        
        Returns:
            bool: 是否删除成功
        """
        if name in self.groups:
            del self.groups[name]
            return self.save()
        return False
    
    def get_group(self, name):
        """
        获取指定文件组的文件列表
        
        Args:
            name (str): 文件组名称
        
        Returns:
            list: 文件路径列表，如果组不存在则返回空列表
        """
        return self.groups.get(name, [])
    
    def get_all_groups(self):
        """
        获取所有文件组
        
        Returns:
            dict: 文件组字典 {名称: [文件列表]}
        """
        return self.groups.copy()
    
    def has_group(self, name):
        """
        检查文件组是否存在
        
        Args:
            name (str): 文件组名称
        
        Returns:
            bool: 是否存在
        """
        return name in self.groups
    
    def rename_group(self, old_name, new_name):
        """
        重命名文件组
        
        Args:
            old_name (str): 原名称
            new_name (str): 新名称
        
        Returns:
            bool: 是否重命名成功
        """
        if old_name in self.groups and new_name not in self.groups:
            self.groups[new_name] = self.groups.pop(old_name)
            return self.save()
        return False
    
    def get_group_stats(self, name):
        """
        获取文件组的统计信息
        
        Args:
            name (str): 文件组名称
        
        Returns:
            tuple: (存在的文件数, 总文件数)，组不存在返回 (0, 0)
        """
        files = self.get_group(name)
        if not files:
            return 0, 0
        
        existing = sum(1 for f in files if os.path.exists(f))
        return existing, len(files)
    
    def add_file_to_group(self, group_name, file_path):
        """
        添加单个文件到文件组
        
        Args:
            group_name (str): 文件组名称
            file_path (str): 文件路径
        
        Returns:
            bool: 是否添加成功
        """
        if group_name not in self.groups:
            return False
        
        if file_path in self.groups[group_name]:
            return True  # 文件已存在，视为成功
        
        self.groups[group_name].append(file_path)
        return self.save()
    
    def remove_file_from_group(self, group_name, file_index):
        """
        从文件组删除指定索引的文件
        
        Args:
            group_name (str): 文件组名称
            file_index (int): 文件索引
        
        Returns:
            bool: 是否删除成功
        """
        if group_name not in self.groups:
            return False
        
        files = self.groups[group_name]
        if 0 <= file_index < len(files):
            files.pop(file_index)
            return self.save()
        return False
    
    def update_group_files(self, group_name, files):
        """
        批量更新文件组的文件列表
        
        Args:
            group_name (str): 文件组名称
            files (list): 新的文件路径列表
        
        Returns:
            bool: 是否更新成功
        """
        if group_name not in self.groups:
            return False
        
        self.groups[group_name] = list(files)
        return self.save()
