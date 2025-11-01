# -*- coding: utf-8 -*-
"""
身体数据模块
负责用户身体数据的录入和管理
"""

import json
from pathlib import Path
from datetime import datetime

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App
from kivy.utils import get_color_from_hex as rgba
from kivy.clock import Clock
from kivy.animation import Animation

# 导入统一数据管理器
from utils.data_manager import DataManager

# 导入自定义组件
from components.custom_widgets import FlatButton, Card, GenderButton, GoalButton, StyledTextInput
# 导入颜色常量
from main import IOS_ORANGE

# 数据文件路径
DATA_DIR = Path(__file__).parent.parent.parent / "data"
USER_DATA_DIR = DATA_DIR / "user_data"
USER_PROFILE_FILE = USER_DATA_DIR / "user_profile.json"

# KV语言定义
body_data_screen_kv = '''
<BodyDataScreen>:
    name: 'profile'
    BoxLayout:
        orientation: 'vertical'
        
        # Header
        BoxLayout:
            size_hint_y: None
            height: '108dp'
            padding: '24dp', '48dp', '24dp', '12dp'
            Label:
                text: "个人中心"
                font_name: 'ChineseFont' if app.font_available else 'Roboto'
                font_size: '32sp'
                color: rgba('#000000')
                bold: False
        
        # 返回按钮区域
        BoxLayout:
            size_hint_y: None
            height: '60dp'
            padding: '12dp'
            FlatButton:
                text: "← 返回"
                size_hint_x: None
                width: '100dp'
                on_press: root.navigate_back()
        
        # Scroll 内容
        ScrollView:
            bar_width: 0
            scroll_type: ['bars', 'content']
            bar_color: rgba('#7EDAB8')
            bar_inactive_color: rgba('#C0C0C0')
            effect_cls: 'ScrollEffect'
            BoxLayout:
                orientation: 'vertical'
                padding: '24dp', '12dp', '24dp', '24dp'
                spacing: '24dp'
                size_hint_y: None
                height: self.minimum_height
                
                # 性别选择区域
                Card:
                    size_hint_y: None
                    height: self.minimum_height
                    BoxLayout:
                        orientation: 'vertical'
                        spacing: '16dp'
                        size_hint_y: None
                        height: self.minimum_height
                        
                        Label:
                            text: "性别"
                            font_name: 'ChineseFont' if app.font_available else 'Roboto'
                            font_size: '16sp'
                            color: rgba('#000000')
                            size_hint_y: None
                            height: '30dp'
                        
                        BoxLayout:
                            orientation: 'horizontal'
                            spacing: '16dp'
                            size_hint_y: None
                            height: '48dp'
                            
                            GenderButton:
                                id: male_button
                                text: "男"
                                gender: 'male'
                                on_press: root.select_gender('male')
                            
                            GenderButton:
                                id: female_button
                                text: "女"
                                gender: 'female'
                                on_press: root.select_gender('female')
                
                # 目标选择区域
                Card:
                    size_hint_y: None
                    height: self.minimum_height
                    BoxLayout:
                        orientation: 'vertical'
                        spacing: '16dp'
                        size_hint_y: None
                        height: self.minimum_height
                        
                        Label:
                            text: "目标"
                            font_name: 'ChineseFont' if app.font_available else 'Roboto'
                            font_size: '16sp'
                            color: rgba('#000000')
                            size_hint_y: None
                            height: '30dp'
                        
                        BoxLayout:
                            orientation: 'horizontal'
                            spacing: '10dp'
                            size_hint_y: None
                            height: '48dp'
                            
                            GoalButton:
                                id: lose_weight_button
                                text: "减重"
                                on_press: root.select_goal('减重')
                            
                            GoalButton:
                                id: maintain_weight_button
                                text: "维持"
                                on_press: root.select_goal('维持')
                            
                            GoalButton:
                                id: gain_weight_button
                                text: "增重"
                                on_press: root.select_goal('增重')
                
                # 用户信息输入区域
                Card:
                    size_hint_y: None
                    height: self.minimum_height
                    BoxLayout:
                        orientation: 'vertical'
                        spacing: '16dp'
                        size_hint_y: None
                        height: self.minimum_height
                        
                        Label:
                            text: "身体数据"
                            font_name: 'ChineseFont' if app.font_available else 'Roboto'
                            font_size: '16sp'
                            color: rgba('#000000')
                            size_hint_y: None
                            height: '30dp'
                        
                        BoxLayout:
                            orientation: 'vertical'
                            spacing: '12dp'
                            size_hint_y: None
                            height: self.minimum_height
                            
                            BoxLayout:
                                orientation: 'horizontal'
                                spacing: '10dp'
                                size_hint_y: None
                                height: '48dp'
                                
                                StyledTextInput:
                                    id: age_input
                                    hint_text: '年龄'
                                    font_name: 'ChineseFont' if app.font_available else 'Roboto'
                                    font_size: '14sp'
                                    multiline: False
                                    input_filter: 'int'
                                    size_hint_x: 0.5
                                    keyboard_suggestions: True
                                    input_type: 'number'
                                
                                StyledTextInput:
                                    id: height_input
                                    hint_text: '身高(cm)'
                                    font_name: 'ChineseFont' if app.font_available else 'Roboto'
                                    font_size: '14sp'
                                    multiline: False
                                    input_filter: 'float'
                                    size_hint_x: 0.5
                                    keyboard_suggestions: True
                                    input_type: 'number'
                            
                            BoxLayout:
                                orientation: 'horizontal'
                                spacing: '10dp'
                                size_hint_y: None
                                height: '48dp'
                                
                                StyledTextInput:
                                    id: current_weight_input
                                    hint_text: '当前体重(kg)'
                                    font_name: 'ChineseFont' if app.font_available else 'Roboto'
                                    font_size: '14sp'
                                    multiline: False
                                    input_filter: 'float'
                                    size_hint_x: 0.5
                                    keyboard_suggestions: True
                                    input_type: 'number'
                                
                                StyledTextInput:
                                    id: target_weight_input
                                    hint_text: '目标体重(kg)'
                                    font_name: 'ChineseFont' if app.font_available else 'Roboto'
                                    font_size: '14sp'
                                    multiline: False
                                    input_filter: 'float'
                                    size_hint_x: 0.5
                                    keyboard_suggestions: True
                                    input_type: 'number'
                
                # 保存按钮
                Card:
                    size_hint_y: None
                    height: self.minimum_height
                    BoxLayout:
                        orientation: 'vertical'
                        spacing: '16dp'
                        size_hint_y: None
                        height: self.minimum_height
                        
                        FlatButton:
                            id: save_button
                            text: "保存数据"
                            on_press: root.save_data()
'''

Builder.load_string(body_data_screen_kv)

# 为GenderButton和GoalButton添加引用，避免属性访问错误
from kivy.factory import Factory
Factory.register('GenderButton', cls=GenderButton)
Factory.register('GoalButton', cls=GoalButton)

class BodyDataScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_data = {}
        self.original_data = {}
        self.data_manager = DataManager()  # 初始化数据管理器
        self._is_first_popup = True  # 标记是否是第一个弹窗
    
    def on_pre_enter(self, *args):
        """在进入屏幕前加载已有数据"""
        self.load_existing_data()
    
    def load_existing_data(self):
        """加载已存在的用户数据"""
        # 使用数据管理器加载用户档案
        profile_data = self.data_manager.get_profile()
        if profile_data:
            try:
                self.user_data = profile_data
                # 保存原始数据用于比较
                self.original_data = self.user_data.copy()
                
                # 更新界面显示
                self.update_ui_with_data()
            except Exception as e:
                print(f"加载用户数据时出错: {e}")
    
    def update_ui_with_data(self):
        """用已有的数据更新界面"""
        # 设置性别
        gender = self.user_data.get("gender", "")
        if gender == "男":
            self.select_gender('male')
        elif gender == "女":
            self.select_gender('female')
        else:
            # 如果没有设置性别，重置所有按钮状态
            self.select_gender(None)
        
        # 设置目标
        goal = self.user_data.get("goal", "维持")
        if goal == "减重":
            self.select_goal('减重')
        elif goal == "维持":
            self.select_goal('维持')
        elif goal == "增重":
            self.select_goal('增重')
        else:
            # 如果没有设置目标，重置所有按钮状态
            self.select_goal(None)
        
        # 设置输入框的值
        if hasattr(self.ids, 'age_input'):
            self.ids.age_input.text = str(self.user_data.get("age", ""))
        if hasattr(self.ids, 'height_input'):
            self.ids.height_input.text = str(self.user_data.get("height", ""))
        if hasattr(self.ids, 'current_weight_input'):
            self.ids.current_weight_input.text = str(self.user_data.get("current_weight", ""))
        if hasattr(self.ids, 'target_weight_input'):
            self.ids.target_weight_input.text = str(self.user_data.get("target_weight", ""))
    
    def select_gender(self, gender):
        """选择性别"""
        # 重置所有性别按钮状态
        if hasattr(self.ids, 'male_button'):
            self.ids.male_button.selected = (gender == 'male')
        if hasattr(self.ids, 'female_button'):
            self.ids.female_button.selected = (gender == 'female')
        
        # 保存选择
        if gender is not None:
            self.user_data["gender"] = "男" if gender == 'male' else "女"
    
    def select_goal(self, goal):
        """选择目标"""
        # 重置所有目标按钮状态
        if hasattr(self.ids, 'lose_weight_button'):
            self.ids.lose_weight_button.selected = (goal == '减重')
        if hasattr(self.ids, 'maintain_weight_button'):
            self.ids.maintain_weight_button.selected = (goal == '维持')
        if hasattr(self.ids, 'gain_weight_button'):
            self.ids.gain_weight_button.selected = (goal == '增重')
        
        # 保存选择
        if goal is not None:
            self.user_data["goal"] = goal
    
    def save_data(self):
        """保存数据"""
        # 获取输入值
        try:
            age = int(self.ids.age_input.text) if hasattr(self.ids, 'age_input') and self.ids.age_input.text else 0
            height = float(self.ids.height_input.text) if hasattr(self.ids, 'height_input') and self.ids.height_input.text else 0
            current_weight = float(self.ids.current_weight_input.text) if hasattr(self.ids, 'current_weight_input') and self.ids.current_weight_input.text else 0
            target_weight = float(self.ids.target_weight_input.text) if hasattr(self.ids, 'target_weight_input') and self.ids.target_weight_input.text else 0
            
            # 验证数据
            if age <= 0 or height <= 0 or current_weight <= 0:
                # 使用按钮反馈替代弹窗提示
                self.show_save_feedback("数据无效", success=False)
                return
            
            if target_weight <= 0:
                # 使用按钮反馈替代弹窗提示
                self.show_save_feedback("目标体重无效", success=False)
                return
            
            # 保存数据
            self.user_data.update({
                "age": age,
                "height": height,
                "current_weight": current_weight,
                "target_weight": target_weight
            })
            
            # 使用数据管理器保存用户档案
            self.data_manager.update_profile(self.user_data)
            
            # 显示保存成功反馈（通过按钮颜色变化）
            self.show_save_feedback("已保存", success=True)
            
        except ValueError:
            # 使用按钮反馈替代弹窗提示
            self.show_save_feedback("输入格式错误", success=False)
        except Exception as e:
            # 使用按钮反馈替代弹窗提示
            self.show_save_feedback("保存失败", success=False)
    
    def show_save_feedback(self, message, success=True):
        """显示保存反馈，通过按钮颜色变化和文字修改"""
        if hasattr(self.ids, 'save_button'):
            save_button = self.ids.save_button
            # 保存原始状态
            original_text = save_button.text
            # 修改按钮文字和颜色
            save_button.text = message
            save_button.save_success = success  # 使用自定义属性控制颜色
            
            # 3秒后恢复原始状态
            def restore_button_state(dt):
                save_button.text = original_text
                save_button.save_success = False  # 恢复原始样式
                
            Clock.schedule_once(restore_button_state, 3)
    
    def show_message(self, message, msg_type):
        """显示消息 - 使用按钮反馈替代"""
        # 根据消息类型确定反馈颜色
        if msg_type == "error":
            self.show_save_feedback(message, success=False)
        else:
            self.show_save_feedback(message, success=True)
    
    def show_auto_save_notification(self, message):
        """显示自动保存通知 - 使用按钮反馈替代"""
        self.show_save_feedback(message, success=True)
    
    def navigate_back(self):
        """返回主页，使用右滑动效"""
        app = App.get_running_app()
        if hasattr(app, 'navigate_to_screen'):
            app.navigate_to_screen('home', direction='right')
        else:
            app.root.current = 'home'