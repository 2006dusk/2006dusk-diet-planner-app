# -*- coding: utf-8 -*-
"""
体重规划模块
负责体重记录和目标管理
"""

import json
from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App
from kivy.utils import get_color_from_hex as rgba

# 导入统一数据管理器
from utils.data_manager import DataManager

# 在这里定义WeightScreen的KV语言
weight_screen_kv = '''
#:import FlatButton components.custom_widgets.FlatButton
#:import Card components.custom_widgets.Card

<WeightScreen>:
    name: 'weight'
    BoxLayout:
        orientation: 'vertical'

        # Header
        BoxLayout:
            size_hint_y: None
            height: '120dp'
            padding: '24dp', '60dp', '24dp', '12dp'
            Label:
                text: "体重规划"
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

        # 内容区域
        ScrollView:
            bar_width: 0
            scroll_type: ['bars', 'content']
            effect_cls: 'ScrollEffect'

            BoxLayout:
                orientation: 'vertical'
                padding: '24dp', '12dp'
                spacing: '24dp'
                size_hint_y: None
                height: self.minimum_height

                # 用户信息卡片
                Card:
                    size_hint_y: None
                    height: self.minimum_height
                    BoxLayout:
                        orientation: 'vertical'
                        spacing: '15dp'
                        size_hint_y: None
                        height: self.minimum_height

                        Label:
                            id: user_info_label
                            text: "用户信息加载中..."
                            font_name: 'ChineseFont' if app.font_available else 'Roboto'
                            font_size: '16sp'
                            color: rgba('#000000')
                            size_hint_y: None
                            height: '80dp'
                            text_size: self.size
                            halign: 'left'
                            valign: 'middle'

                        # 体重输入区域
                        BoxLayout:
                            orientation: 'horizontal'
                            spacing: '10dp'
                            size_hint_y: None
                            height: '48dp'

                            TextInput:
                                id: weight_input
                                hint_text: '输入当前体重(kg)'
                                font_name: 'ChineseFont' if app.font_available else 'Roboto'
                                font_size: '14sp'
                                multiline: False
                                input_filter: 'float'
                                size_hint_x: 0.7

                            FlatButton:
                                text: "保存"
                                size_hint_x: 0.3
                                on_press: root.save_weight()

                # 体重历史记录
                Card:
                    size_hint_y: None
                    height: self.minimum_height
                    BoxLayout:
                        orientation: 'vertical'
                        spacing: '15dp'
                        size_hint_y: None
                        height: self.minimum_height

                        Label:
                            text: "体重历史记录"
                            font_name: 'ChineseFont' if app.font_available else 'Roboto'
                            font_size: '16sp'
                            color: rgba('#000000')
                            size_hint_y: None
                            height: '30dp'

                        Label:
                            id: weight_history_label
                            text: "暂无体重记录"
                            font_name: 'ChineseFont' if app.font_available else 'Roboto'
                            font_size: '14sp'
                            color: rgba('#8E8E93')
                            text_size: self.size
                            halign: 'left'
                            valign: 'top'

                # 饮食建议卡片
                Card:
                    size_hint_y: None
                    height: self.minimum_height
                    BoxLayout:
                        orientation: 'vertical'
                        spacing: '15dp'
                        size_hint_y: None
                        height: self.minimum_height

                        Label:
                            text: "个性化饮食建议"
                            font_name: 'ChineseFont' if app.font_available else 'Roboto'
                            font_size: '16sp'
                            color: rgba('#000000')
                            size_hint_y: None
                            height: '30dp'

                        Label:
                            id: diet_suggestion_label
                            text: "请输入体重以获取建议"
                            font_name: 'ChineseFont' if app.font_available else 'Roboto'
                            font_size: '14sp'
                            color: rgba('#8E8E93')
                            text_size: self.size
                            halign: 'left'
                            valign: 'top'

                # 体重规划计算器
                Card:
                    size_hint_y: None
                    height: self.minimum_height
                    BoxLayout:
                        orientation: 'vertical'
                        spacing: '15dp'
                        size_hint_y: None
                        height: self.minimum_height

                        Label:
                            text: "体重规划计算器"
                            font_name: 'ChineseFont' if app.font_available else 'Roboto'
                            font_size: '16sp'
                            color: rgba('#000000')
                            size_hint_y: None
                            height: '30dp'

                        # 输入区域
                        BoxLayout:
                            orientation: 'vertical'
                            spacing: '10dp'
                            size_hint_y: None
                            height: self.minimum_height

                            BoxLayout:
                                orientation: 'horizontal'
                                spacing: '10dp'
                                size_hint_y: None
                                height: '48dp'

                                TextInput:
                                    id: current_weight
                                    hint_text: '当前体重(kg)'
                                    font_name: 'ChineseFont' if app.font_available else 'Roboto'
                                    font_size: '14sp'
                                    multiline: False
                                    input_filter: 'float'
                                    size_hint_x: 0.5

                                TextInput:
                                    id: target_weight
                                    hint_text: '目标体重(kg)'
                                    font_name: 'ChineseFont' if app.font_available else 'Roboto'
                                    font_size: '14sp'
                                    multiline: False
                                    input_filter: 'float'
                                    size_hint_x: 0.5

                            BoxLayout:
                                orientation: 'horizontal'
                                spacing: '10dp'
                                size_hint_y: None
                                height: '48dp'

                                TextInput:
                                    id: weeks
                                    hint_text: '计划周期(周)'
                                    font_name: 'ChineseFont' if app.font_available else 'Roboto'
                                    font_size: '14sp'
                                    multiline: False
                                    input_filter: 'int'
                                    size_hint_x: 0.5

                                FlatButton:
                                    text: "计算"
                                    size_hint_x: 0.5
                                    on_press: root.calculate_plan()

                        # 结果显示区域
                        BoxLayout:
                            id: result_container
                            orientation: 'vertical'
                            spacing: '10dp'
                            size_hint_y: None
                            height: self.minimum_height
'''

Builder.load_string(weight_screen_kv)


class WeightScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = DataManager()  # 初始化数据管理器

    def on_pre_enter(self, *args):
        """在进入屏幕前加载用户信息"""
        self.load_user_info()
        self.load_weight_history()

    def load_user_info(self):
        """加载并显示用户信息"""
        try:
            # 使用数据管理器获取用户档案
            user_info = self.data_manager.get_profile()

            if user_info:
                # 构建用户信息文本，使用统一的格式和单位
                info_text = "年龄: {} 岁\n".format(user_info.get('age', '未知'))
                info_text += "身高: {} cm\n".format(user_info.get('height', '未知'))
                info_text += "当前体重: {} kg\n".format(user_info.get('current_weight', '未知'))
                info_text += "目标体重: {} kg".format(user_info.get('target_weight', '未知'))

                # 更新标签文本
                self.ids.user_info_label.text = info_text

                # 同步输入框数据
                self.ids.current_weight.text = str(user_info.get('current_weight', ''))
                self.ids.target_weight.text = str(user_info.get('target_weight', ''))
            else:
                self.ids.user_info_label.text = "暂无用户信息，请先完善个人资料"

        except Exception as e:
            self.ids.user_info_label.text = f"加载用户信息失败: {str(e)}"

    def load_weight_history(self):
        """加载并显示体重历史记录"""
        try:
            # 获取体重历史记录
            profile_data = self.data_manager.get_profile()
            weight_history = profile_data.get("weight_history", [])

            if weight_history:
                # 按日期排序，显示最近的5条记录
                sorted_history = sorted(weight_history, key=lambda x: x['date'], reverse=True)[:5]

                # 构建历史记录文本，统一格式和单位显示
                history_text = ""
                for record in sorted_history:
                    history_text += "{}: {} kg\n".format(record['date'], record['weight'])

                self.ids.weight_history_label.text = history_text.strip()
            else:
                self.ids.weight_history_label.text = "暂无体重记录"

        except Exception as e:
            self.ids.weight_history_label.text = f"加载体重记录失败: {str(e)}"

    def save_weight(self):
        """保存体重并生成个性化建议"""
        # 获取输入值
        weight_input = self.ids.weight_input.text

        try:
            # 解析输入值
            current_weight = float(weight_input)

            # 更新用户档案中的当前体重
            user_info = self.data_manager.get_profile()
            user_info["current_weight"] = current_weight
            
            # 更新体重历史记录
            weight_history = user_info.get("weight_history", [])
            today = datetime.now().strftime("%Y-%m-%d")
            
            # 检查今天是否已有记录，如果有则更新，否则添加新记录
            existing_record_index = None
            for i, record in enumerate(weight_history):
                if record.get("date") == today:
                    existing_record_index = i
                    break
            
            weight_record = {
                "date": today,
                "weight": current_weight
            }
            
            if existing_record_index is not None:
                weight_history[existing_record_index] = weight_record
            else:
                weight_history.append(weight_record)
            
            user_info["weight_history"] = weight_history

            # 使用数据管理器更新用户档案
            self.data_manager.update_profile(user_info)

            # 更新显示的用户信息和体重历史
            self.load_user_info()
            self.load_weight_history()

            # 生成个性化饮食建议
            self.generate_diet_suggestion(current_weight, user_info)

        except ValueError:
            self.ids.diet_suggestion_label.text = "请输入有效的体重数值"
        except Exception as e:
            self.ids.diet_suggestion_label.text = f"保存失败: {str(e)}"

    def generate_diet_suggestion(self, current_weight, user_info):
        """根据用户信息生成个性化饮食建议"""
        try:
            # 获取用户基本信息
            height = user_info.get("height")
            age = user_info.get("age")
            gender = user_info.get("gender", "男")
            target_weight = user_info.get("target_weight")
            activity_level = user_info.get("activity_level", "medium")

            if not all([height, age, target_weight]):
                self.ids.diet_suggestion_label.text = "请完善个人信息以获取建议"
                return

            # 计算BMI
            height_m = height / 100  # 转换为米
            bmi = current_weight / (height_m ** 2)

            # 根据BMI和目标体重生成建议，优化换行和单位显示
            if current_weight < target_weight:
                # 需要增重
                suggestion = "您的 BMI 为 {:.1f}，建议适当增加热量摄入\n\n".format(bmi)
                suggestion += "• 增加蛋白质摄入（鸡蛋、瘦肉、豆类）\n"
                suggestion += "• 适量摄入健康脂肪（坚果、牛油果）\n"
                suggestion += "• 规律进餐，可适当加餐"
            elif current_weight > target_weight:
                # 需要减重
                suggestion = "您的 BMI 为 {:.1f}，建议适当控制热量摄入\n\n".format(bmi)
                suggestion += "• 增加蔬菜和水果摄入\n"
                suggestion += "• 选择低脂蛋白质来源\n"
                suggestion += "• 控制碳水化合物摄入，适量运动"
            else:
                # 维持体重
                suggestion = "您的 BMI 为 {:.1f}，建议保持均衡饮食\n\n".format(bmi)
                suggestion += "• 保持营养均衡\n"
                suggestion += "• 适量运动\n"
                suggestion += "• 规律作息"

            self.ids.diet_suggestion_label.text = suggestion

        except Exception as e:
            self.ids.diet_suggestion_label.text = f"生成建议失败: {str(e)}"

    def calculate_plan(self):
        """计算体重规划"""
        # 获取输入值
        current_weight_input = self.ids.current_weight.text
        target_weight_input = self.ids.target_weight.text
        weeks_input = self.ids.weeks.text

        # 获取结果显示容器
        result_container = self.ids.result_container
        result_container.clear_widgets()

        try:
            # 解析输入值
            current_weight = float(current_weight_input)
            target_weight = float(target_weight_input)
            weeks = int(weeks_input)

            # 计算每周需要减重/增重的公斤数
            weight_diff = target_weight - current_weight
            weekly_change = weight_diff / weeks

            # 根据计算结果确定显示文本
            goal_text = '增重' if weight_diff > 0 else '减重'
            suggestion_text = '适当增加热量摄入' if weight_diff > 0 else '适当控制热量摄入'
            color_code = '#FF3B30' if weight_diff * weekly_change < 0 else '#34C759'

            # 显示结果，优化格式和单位显示
            result_card = Builder.load_string(f'''
BoxLayout:
    orientation: 'vertical'
    spacing: '10dp'
    size_hint_y: None
    height: '200dp'
    padding: '20dp', '15dp'
    canvas.before:
        Color:
            rgba: rgba('#FFFFFF') + [0.85]
        RoundedRectangle:
            pos: self.pos
            size: self.size
    Label:
        text: "体重变化计划"
        font_name: 'ChineseFont' if app.font_available else 'Roboto'
        font_size: '16sp'
        color: rgba('#000000')
        size_hint_y: None
        height: '30dp'
        halign: 'center'
        valign: 'middle'
    Label:
        text: "目标: {goal_text} {abs(weight_diff):.1f} kg"
        font_name: 'ChineseFont' if app.font_available else 'Roboto'
        font_size: '14sp'
        color: rgba('#8E8E93')
        size_hint_y: None
        height: '25dp'
        halign: 'left'
        valign: 'middle'
    Label:
        text: "周期: {weeks} 周"
        font_name: 'ChineseFont' if app.font_available else 'Roboto'
        font_size: '14sp'
        color: rgba('#8E8E93')
        size_hint_y: None
        height: '25dp'
        halign: 'left'
        valign: 'middle'
    Label:
        text: "每周{goal_text} {abs(weekly_change):.2f} kg"
        font_name: 'ChineseFont' if app.font_available else 'Roboto'
        font_size: '14sp'
        color: rgba('{color_code}')
        size_hint_y: None
        height: '25dp'
        halign: 'left'
        valign: 'middle'
    Label:
        text: "建议: {suggestion_text}"
        font_name: 'ChineseFont' if app.font_available else 'Roboto'
        font_size: '14sp'
        color: rgba('#8E8E93')
        text_size: self.size
        halign: 'left'
        valign: 'top'
        size_hint_y: None
        height: '50dp'
''')

            result_container.add_widget(result_card)

        except ValueError:
            # 显示错误信息
            error_card = Builder.load_string('''
BoxLayout:
    orientation: 'vertical'
    spacing: '10dp'
    size_hint_y: None
    height: '100dp'
    padding: '20dp', '15dp'
    canvas.before:
        Color:
            rgba: rgba('#FFFFFF') + [0.85]
        RoundedRectangle:
            pos: self.pos
            size: self.size
    Label:
        text: "输入错误"
        font_name: 'ChineseFont' if app.font_available else 'Roboto'
        font_size: '16sp'
        color: rgba('#FF3B30')
        size_hint_y: None
        height: '30dp'
        halign: 'center'
        valign: 'middle'
    Label:
        text: "请输入有效的数字"
        font_name: 'ChineseFont' if app.font_available else 'Roboto'
        font_size: '14sp'
        color: rgba('#8E8E93')
        size_hint_y: None
        height: '25dp'
        halign: 'center'
        valign: 'middle'
''')
            result_container.add_widget(error_card)
        except Exception as e:
            # 显示错误信息
            error_card = Builder.load_string('''
BoxLayout:
    orientation: 'vertical'
    spacing: '10dp'
    size_hint_y: None
    height: '100dp'
    padding: '20dp', '15dp'
    canvas.before:
        Color:
            rgba: rgba('#FFFFFF') + [0.85]
        RoundedRectangle:
            pos: self.pos
            size: self.size
    Label:
        text: "计算错误"
        font_name: 'ChineseFont' if app.font_available else 'Roboto'
        font_size: '16sp'
        color: rgba('#FF3B30')
        size_hint_y: None
        height: '30dp'
        halign: 'center'
        valign: 'middle'
    Label:
        text: "计算时发生错误"
        font_name: 'ChineseFont' if app.font_available else 'Roboto'
        font_size: '14sp'
        color: rgba('#8E8E93')
        size_hint_y: None
        height: '25dp'
        halign: 'center'
        valign: 'middle'
''')
            result_container.add_widget(error_card)

    def navigate_back(self):
        """返回主页，使用右滑动效"""
        app = App.get_running_app()
        if hasattr(app, 'navigate_to_screen'):
            app.navigate_to_screen('home', direction='right')
        else:
            app.root.current = 'home'