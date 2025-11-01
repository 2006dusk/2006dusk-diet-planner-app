# -*- coding: utf-8 -*-
"""
统一数据管理器
负责管理所有用户数据的加载、保存和访问
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 获取数据文件路径
DATA_DIR = Path(__file__).parent.parent / "data"
PREDEFINED_FOODS_DIR = DATA_DIR / "predefined_foods"
USER_DATA_DIR = DATA_DIR / "user_data"

UNIFIED_DATA_FILE = USER_DATA_DIR / "user_data.json"

# 保留原有的独立数据文件路径，用于向后兼容
# 注意：这些独立文件已被弃用，仅保留用于迁移
USER_PROFILE_FILE = USER_DATA_DIR / "user_profile.json"  # 已弃用
USER_PLAN_FILE = USER_DATA_DIR / "user_plan.json"  # 已弃用
HISTORY_PLANS_FILE = USER_DATA_DIR / "history_plans.json"  # 已弃用
USER_RECIPES_FILE = USER_DATA_DIR / "user_recipes.json"  # 已弃用
DAILY_INTAKE_FILE = USER_DATA_DIR / "daily_intake.json"  # 已弃用
WEEKLY_DATA_FILE = USER_DATA_DIR / "weekly_data.json"  # 已弃用


class DataManager:
    """统一数据管理器"""
    
    def __init__(self):
        """初始化数据管理器"""
        self.user_data = self._load_user_data()
        self.last_load_time = datetime.now()
    
    def _load_user_data(self) -> Dict[str, Any]:
        """加载用户数据"""
        # 首先尝试加载统一的数据文件
        if UNIFIED_DATA_FILE.exists():
            try:
                with open(UNIFIED_DATA_FILE, 'r', encoding='utf-8') as f:
                    self.last_load_time = datetime.now()
                    return json.load(f)
            except Exception as e:
                print(f"加载统一数据文件时出错: {e}")
        
        # 如果统一文件不存在，则从分散的文件中加载数据
        data = self._migrate_from_separate_files()
        self.last_load_time = datetime.now()
        return data
    
    def _migrate_from_separate_files(self) -> Dict[str, Any]:
        """从分散的文件中迁移数据"""
        user_data = {
            "profile": {},
            "current_plan": None,
            "history_plans": [],
            "user_recipes": [],
            "daily_intake": [],
            "weekly_data": []
        }
        
        # 加载用户档案
        if USER_PROFILE_FILE.exists():
            try:
                with open(USER_PROFILE_FILE, 'r', encoding='utf-8') as f:
                    user_data["profile"] = json.load(f)
            except Exception as e:
                print(f"加载用户档案时出错: {e}")
        
        # 加载当前计划
        if USER_PLAN_FILE.exists():
            try:
                with open(USER_PLAN_FILE, 'r', encoding='utf-8') as f:
                    user_data["current_plan"] = json.load(f)
            except Exception as e:
                print(f"加载当前计划时出错: {e}")
        
        # 加载历史计划
        if HISTORY_PLANS_FILE.exists():
            try:
                with open(HISTORY_PLANS_FILE, 'r', encoding='utf-8') as f:
                    user_data["history_plans"] = json.load(f)
            except Exception as e:
                print(f"加载历史计划时出错: {e}")
        
        # 加载用户食谱
        if USER_RECIPES_FILE.exists():
            try:
                with open(USER_RECIPES_FILE, 'r', encoding='utf-8') as f:
                    user_data["user_recipes"] = json.load(f)
            except Exception as e:
                print(f"加载用户食谱时出错: {e}")
        
        # 加载每日摄入记录
        if DAILY_INTAKE_FILE.exists():
            try:
                with open(DAILY_INTAKE_FILE, 'r', encoding='utf-8') as f:
                    user_data["daily_intake"] = json.load(f)
            except Exception as e:
                print(f"加载每日摄入记录时出错: {e}")
        
        # 加载每周数据
        if WEEKLY_DATA_FILE.exists():
            try:
                with open(WEEKLY_DATA_FILE, 'r', encoding='utf-8') as f:
                    user_data["weekly_data"] = json.load(f)
            except Exception as e:
                print(f"加载每周数据时出错: {e}")
        
        # 保存到统一文件
        self._save_user_data(user_data)
        
        return user_data
    
    def _check_file_updated(self) -> bool:
        """检查文件是否在上次加载后被更新"""
        if UNIFIED_DATA_FILE.exists():
            try:
                file_modified_time = datetime.fromtimestamp(UNIFIED_DATA_FILE.stat().st_mtime)
                return file_modified_time > self.last_load_time
            except Exception:
                return False
        return False
    
    def _reload_if_needed(self):
        """如果文件已更新，则重新加载数据"""
        if self._check_file_updated():
            self.user_data = self._load_user_data()
    
    def _save_user_data(self, user_data: Dict[str, Any] = None):
        """保存用户数据到统一文件"""
        data_to_save = user_data if user_data is not None else self.user_data
        try:
            # 确保数据目录存在
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            
            with open(UNIFIED_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            # 更新最后加载时间
            self.last_load_time = datetime.now()
        except Exception as e:
            print(f"保存用户数据时出错: {e}")
    
    # 用户档案相关方法
    def get_profile(self) -> Dict[str, Any]:
        """获取用户档案"""
        self._reload_if_needed()
        return self.user_data.get("profile", {})
    
    def update_profile(self, profile_data: Dict[str, Any]):
        """更新用户档案 - 完全覆盖，不保留旧数据"""
        self._reload_if_needed()
        self.user_data["profile"] = profile_data  # 完全覆盖而不是合并
        self._save_user_data()
    
    # 饮食计划相关方法
    def get_current_plan(self) -> Optional[Dict[str, Any]]:
        """获取当前饮食计划"""
        self._reload_if_needed()
        # 从统一数据文件中获取当前计划
        current_plan = self.user_data.get("current_plan")
        if current_plan:
            # 检查计划日期是否为今天
            plan_date = current_plan.get("date")
            today = datetime.now().strftime("%Y-%m-%d")
            
            if plan_date == today:
                return current_plan
            else:
                # 如果不是今天的计划，从历史计划中查找今天的计划
                history_plans = self.user_data.get("history_plans", [])
                for plan in history_plans:
                    if plan.get("date") == today:
                        # 将今天的计划设置为当前计划
                        self.user_data["current_plan"] = plan
                        self._save_user_data()
                        return plan
                return None  # 没有找到今天的计划
        else:
            # 如果没有当前计划，从历史计划中查找今天的计划
            history_plans = self.user_data.get("history_plans", [])
            today = datetime.now().strftime("%Y-%m-%d")
            for plan in history_plans:
                if plan.get("date") == today:
                    # 将今天的计划设置为当前计划
                    self.user_data["current_plan"] = plan
                    self._save_user_data()
                    return plan
        return None

    def save_current_plan(self, plan_data: Dict[str, Any]):
        """保存当前饮食计划"""
        self._reload_if_needed()
        # 添加当前日期
        plan_data["date"] = datetime.now().strftime("%Y-%m-%d")
        
        # 保存到user_data.json
        self.user_data["current_plan"] = plan_data
        # 同时更新历史计划中的当天记录
        self.add_history_plan(plan_data)
        
        # 返回添加了日期的计划数据，以便调用者使用
        return plan_data

    def get_history_plans(self) -> List[Dict[str, Any]]:
        """获取历史饮食计划"""
        self._reload_if_needed()
        # 从统一数据文件中获取历史计划
        return self.user_data.get("history_plans", [])

    def add_history_plan(self, plan_data: Dict[str, Any]):
        """添加历史饮食计划，确保每天只有一组计划"""
        self._reload_if_needed()
        # 确保计划有日期
        if "date" not in plan_data:
            plan_data["date"] = datetime.now().strftime("%Y-%m-%d")
        
        # 从统一数据中读取现有历史计划
        history_plans = self.user_data.get("history_plans", [])
        
        # 检查是否已存在同日期的计划，如果存在则更新而不是添加
        existing_plan_index = None
        for i, plan in enumerate(history_plans):
            if plan.get("date") == plan_data["date"]:
                existing_plan_index = i
                break
                
        if existing_plan_index is not None:
            # 更新现有计划（覆盖）
            history_plans[existing_plan_index] = plan_data
        else:
            # 添加新计划
            history_plans.append(plan_data)
        
        # 保存到user_data.json
        self.user_data["history_plans"] = history_plans
        self._save_user_data()
        
        # 为了确保不重复，我们进行一次去重操作
        self._deduplicate_history_plans()

    def _deduplicate_history_plans(self):
        """对历史计划进行去重，确保每天只有一条记录"""
        history_plans = self.user_data.get("history_plans", [])
        
        # 使用字典按键日期去重，保留最新的记录
        unique_plans = {}
        for plan in history_plans:
            plan_date = plan.get("date")
            if plan_date:
                # 如果日期已存在，会被新记录覆盖（即保留后者）
                unique_plans[plan_date] = plan
        
        # 转换回列表
        deduplicated_plans = list(unique_plans.values())
        
        # 只有在确实有重复时才更新
        if len(deduplicated_plans) != len(history_plans):
            self.user_data["history_plans"] = deduplicated_plans
            self._save_user_data()
    
    # 用户食谱相关方法
    def get_user_recipes(self) -> List[Dict[str, Any]]:
        """获取用户自定义食谱"""
        return self.user_data.get("user_recipes", [])
    
    def add_user_recipe(self, recipe_data: Dict[str, Any]):
        """添加用户自定义食谱"""
        if "user_recipes" not in self.user_data:
            self.user_data["user_recipes"] = []
        self.user_data["user_recipes"].append(recipe_data)
        self._save_user_data()
    
    # 摄入记录相关方法
    def get_daily_intake(self) -> List[Dict[str, Any]]:
        """获取每日摄入记录"""
        return self.user_data.get("daily_intake", [])
    
    def add_daily_intake(self, intake_data: Dict[str, Any]):
        """添加每日摄入记录"""
        if "daily_intake" not in self.user_data:
            self.user_data["daily_intake"] = []
        self.user_data["daily_intake"].append(intake_data)
        self._save_user_data()
    
    # 每周数据相关方法
    def get_weekly_data(self) -> List[Dict[str, Any]]:
        """获取每周数据"""
        return self.user_data.get("weekly_data", [])
    
    def add_weekly_data(self, weekly_data: Dict[str, Any]):
        """添加每周数据"""
        if "weekly_data" not in self.user_data:
            self.user_data["weekly_data"] = []
        self.user_data["weekly_data"].append(weekly_data)
        self._save_user_data()
    
    # 数据清理方法
    def cleanup_separate_files(self):
        """清理分散的数据文件"""
        separate_files = [
            USER_PROFILE_FILE,
            USER_PLAN_FILE,
            HISTORY_PLANS_FILE,
            USER_RECIPES_FILE,
            DAILY_INTAKE_FILE,
            WEEKLY_DATA_FILE
        ]
        
        for file_path in separate_files:
            if file_path.exists():
                try:
                    # 备份文件
                    backup_path = file_path.with_suffix(file_path.suffix + '.bak')
                    file_path.rename(backup_path)
                    print(f"已备份并移除文件: {file_path.name}")
                except Exception as e:
                    print(f"处理文件 {file_path.name} 时出错: {e}")