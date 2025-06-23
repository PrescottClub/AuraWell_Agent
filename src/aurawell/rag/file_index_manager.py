#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件索引管理器
负责维护OSS中文件的索引信息，包括文件名、上传日期、向量化状态等
"""

import json
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
try:
    from .oss_utils import OSSManager, get_beijing_time, get_utc_time
except ImportError:
    from oss_utils import OSSManager, get_beijing_time, get_utc_time

class FileIndexManager:
    """文件索引管理器"""
    
    def __init__(self):
        """初始化文件索引管理器"""
        self.oss_manager = OSSManager()
        self.index_file_key = "file_status/file_index.json"
        self.nutrition_prefix = "nutrition/"
        
        # 初始化索引文件
        self._initialize_index_file()
    
    def _initialize_index_file(self):
        """初始化索引文件，如果不存在则创建"""
        try:
            if not self.oss_manager.file_exists(self.index_file_key):
                print(f"📝 索引文件不存在，创建新的索引文件: {self.index_file_key}")
                empty_index = {}
                self.oss_manager.upload_string_as_file(
                    json.dumps(empty_index, ensure_ascii=False, indent=2),
                    self.index_file_key
                )
                print("✅ 索引文件创建成功")
            else:
                print(f"✅ 索引文件已存在: {self.index_file_key}")
        except Exception as e:
            print(f"❌ 初始化索引文件失败: {e}")
    
    def _load_index(self) -> Dict:
        """
        从OSS加载索引文件
        
        Returns:
            Dict: 索引数据
        """
        try:
            content = self.oss_manager.download_file_content(self.index_file_key)
            if content:
                return json.loads(content)
            else:
                print("⚠️  索引文件内容为空，返回空字典")
                return {}
        except Exception as e:
            print(f"❌ 加载索引文件失败: {e}")
            return {}
    
    def _save_index(self, index_data: Dict) -> bool:
        """
        保存索引数据到OSS
        
        Args:
            index_data (Dict): 索引数据
            
        Returns:
            bool: 保存是否成功
        """
        try:
            content = json.dumps(index_data, ensure_ascii=False, indent=2)
            return self.oss_manager.upload_string_as_file(content, self.index_file_key)
        except Exception as e:
            print(f"❌ 保存索引文件失败: {e}")
            return False
    
    def add_file_record(self, filename: str, oss_key: str, vectorized: bool = False) -> bool:
        """
        添加文件记录到索引
        
        Args:
            filename (str): 文件名
            oss_key (str): OSS中的文件键名
            vectorized (bool): 是否已向量化
            
        Returns:
            bool: 添加是否成功
        """
        try:
            index_data = self._load_index()
            
            # 使用文件名作为键
            file_record = {
                "filename": filename,
                "oss_key": oss_key,
                "upload_date_utc": get_utc_time(),
                "upload_date_beijing": get_beijing_time(),
                "vectorized": vectorized,
                "last_updated": get_beijing_time()
            }
            
            index_data[filename] = file_record
            
            success = self._save_index(index_data)
            if success:
                print(f"✅ 文件记录添加成功: {filename}")
            else:
                print(f"❌ 文件记录添加失败: {filename}")
            
            return success
            
        except Exception as e:
            print(f"❌ 添加文件记录失败: {e}")
            return False
    
    def update_vectorization_status(self, filename: str, vectorized: bool = True) -> bool:
        """
        更新文件的向量化状态
        
        Args:
            filename (str): 文件名
            vectorized (bool): 向量化状态
            
        Returns:
            bool: 更新是否成功
        """
        try:
            index_data = self._load_index()
            
            if filename in index_data:
                index_data[filename]["vectorized"] = vectorized
                index_data[filename]["last_updated"] = get_beijing_time()
                
                success = self._save_index(index_data)
                if success:
                    print(f"✅ 向量化状态更新成功: {filename} -> {vectorized}")
                else:
                    print(f"❌ 向量化状态更新失败: {filename}")
                
                return success
            else:
                print(f"⚠️  文件记录不存在: {filename}")
                return False
                
        except Exception as e:
            print(f"❌ 更新向量化状态失败: {e}")
            return False
    
    def file_exists_in_index(self, filename: str) -> bool:
        """
        检查文件是否已在索引中
        
        Args:
            filename (str): 文件名
            
        Returns:
            bool: 文件是否存在于索引中
        """
        try:
            index_data = self._load_index()
            return filename in index_data
        except Exception as e:
            print(f"❌ 检查文件索引失败: {e}")
            return False
    
    def get_file_record(self, filename: str) -> Optional[Dict]:
        """
        获取文件记录
        
        Args:
            filename (str): 文件名
            
        Returns:
            Optional[Dict]: 文件记录，不存在返回None
        """
        try:
            index_data = self._load_index()
            return index_data.get(filename)
        except Exception as e:
            print(f"❌ 获取文件记录失败: {e}")
            return None
    
    def get_files_uploaded_in_days(self, days: int = 30) -> List[Dict]:
        """
        获取指定天数内上传的文件
        
        Args:
            days (int): 天数，默认30天
            
        Returns:
            List[Dict]: 文件记录列表
        """
        try:
            index_data = self._load_index()
            
            # 计算截止时间（北京时间）
            beijing_tz = timezone(timedelta(hours=8))
            cutoff_time = datetime.now(beijing_tz) - timedelta(days=days)
            
            recent_files = []
            for filename, record in index_data.items():
                try:
                    # 解析上传时间（北京时间）
                    upload_time = datetime.fromisoformat(record["upload_date_beijing"])
                    
                    # 如果上传时间没有时区信息，假设为北京时间
                    if upload_time.tzinfo is None:
                        upload_time = upload_time.replace(tzinfo=beijing_tz)
                    
                    if upload_time >= cutoff_time:
                        recent_files.append(record)
                        
                except Exception as e:
                    print(f"⚠️  解析文件时间失败: {filename}, {e}")
                    continue
            
            print(f"✅ 找到 {len(recent_files)} 个在 {days} 天内上传的文件")
            return recent_files
            
        except Exception as e:
            print(f"❌ 获取最近上传文件失败: {e}")
            return []
    
    def get_unvectorized_files(self) -> List[Dict]:
        """
        获取未向量化的文件
        
        Returns:
            List[Dict]: 未向量化的文件记录列表
        """
        try:
            index_data = self._load_index()
            
            unvectorized_files = []
            for filename, record in index_data.items():
                if not record.get("vectorized", False):
                    unvectorized_files.append(record)
            
            print(f"✅ 找到 {len(unvectorized_files)} 个未向量化的文件")
            return unvectorized_files
            
        except Exception as e:
            print(f"❌ 获取未向量化文件失败: {e}")
            return []
    
    def get_all_files(self) -> Dict:
        """
        获取所有文件记录
        
        Returns:
            Dict: 所有文件记录
        """
        try:
            return self._load_index()
        except Exception as e:
            print(f"❌ 获取所有文件记录失败: {e}")
            return {}
    
    def remove_file_record(self, filename: str) -> bool:
        """
        从索引中移除文件记录
        
        Args:
            filename (str): 文件名
            
        Returns:
            bool: 移除是否成功
        """
        try:
            index_data = self._load_index()
            
            if filename in index_data:
                del index_data[filename]
                success = self._save_index(index_data)
                if success:
                    print(f"✅ 文件记录移除成功: {filename}")
                else:
                    print(f"❌ 文件记录移除失败: {filename}")
                return success
            else:
                print(f"⚠️  文件记录不存在: {filename}")
                return True  # 文件不存在也算成功
                
        except Exception as e:
            print(f"❌ 移除文件记录失败: {e}")
            return False
