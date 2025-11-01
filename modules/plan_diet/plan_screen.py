# -*- coding: utf-8 -*-
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.app import App
from pathlib import Path
import json
import os
import random
import re
from datetime import datetime
from functools import partial

# 从主应用导入颜色常量
from main import IOS_MINT, IOS_CORAL, IOS_ORANGE, IOS_BG, IOS_CARD, IOS_DIVIDER, IOS_TEXT_MAIN, IOS_TEXT_SEC, IOS_SUCCESS, \
    IOS_WARNING, IOS_ERROR

# 导入饮食计划相关模块
from modules.plan_diet.plan_generator import PlanGenerator

# 导入高级食物选择器
from modules.plan_diet.advanced_food_selector import AdvancedFoodSelector

# 导入统一数据管理器
from utils.data_manager import DataManager

# 导入rgba函数供KV文件使用
from kivy.utils import get_color_from_hex as rgba

# 在这里定义DietPlanScreen的KV语言，避免中文字符编码问题
plan_screen_kv = '''
<DietPlanScreen>:
    name: 'plan'  # 明确指定屏幕名称
    BoxLayout:
        orientation: 'vertical'

        #  Header 
        BoxLayout:
            size_hint_y: None
            height: '108dp'
            padding: '24dp', '48dp', '24dp', '12dp'
            Label:
                text: "饮食计划"
                font_name: 'ChineseFont' if app.font_available else 'Roboto' if app and hasattr(app, 'font_available') else 'Roboto'
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

        #  Scroll 内容 
        ScrollView:
            id: scroll_view
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

                # 用户输入区域
                InputCard:
                    size_hint_y: None
                    height: self.minimum_height
                    BoxLayout:
                        orientation: 'vertical'
                        spacing: '10dp'
                        size_hint_y: None
                        height: '60dp'

                        Label:
                            text: "生成饮食计划"
                            font_name: 'ChineseFont' if app.font_available else 'Roboto' if app and hasattr(app, 'font_available') else 'Roboto'
                            font_size: '16sp'
                            color: rgba('#000000')
                            size_hint_y: None
                            height: '30dp'

                        BoxLayout:
                            orientation: 'horizontal'
                            spacing: '10dp'
                            size_hint_y: None
                            height: '48dp'
                            FlatButton:
                                id: goal_button
                                text: "维持"
                                on_press: root.switch_goal()
                            FlatButton:
                                text: "刷新计划"
                                on_press: root.refresh_plan()
                            FlatButton:
                                text: "随机生成"
                                on_press: root.randomize_plan()
                            FlatButton:
                                id: save_button
                                text: "保存计划"
                                on_press: root.save_plan()

                # 结果显示区域
                BoxLayout:
                    id: meals_container  # 用于显示饮食计划的容器
                    orientation: 'vertical'
                    spacing: '15dp'
                    size_hint_y: None
                    height: self.minimum_height
'''

Builder.load_string(plan_screen_kv)


class DietPlanScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.plan_generator = PlanGenerator()
        self.user_data = None
        self.current_meal_index = None
        self.current_position = None
        # 添加长按检测相关属性
        self.long_press_duration = 2.0  # 长按持续时间（秒）从3秒改为2秒
        self.long_press_trigger = None
        self.progress_bars = {}  # 存储进度条引用
        self.current_plan_data = None  # 保存当前显示的计划数据
        self.data_manager = DataManager()  # 初始化数据管理器
        self._is_first_popup = True  # 标记是否是第一个弹窗

    def on_pre_enter(self, *args):
        """在进入屏幕前加载数据"""
        print(f"DEBUG: on_pre_enter called, current_plan_data exists: {self.current_plan_data is not None}")
        # 每次进入页面都重新加载数据以确保显示最新内容
        Clock.schedule_once(lambda dt: self.load_body_data_and_plan(), 0.1)
        # 同时加载摄入数据
        Clock.schedule_once(lambda dt: self.load_intake_data(), 0.15)

    def load_intake_data(self):
        """加载摄入数据"""
        # 这里可以添加任何需要的摄入数据加载逻辑
        pass

    def load_body_data_and_plan(self):
        """从JSON文件加载身体数据和今日计划"""
        try:
            # 使用数据管理器获取用户档案
            self.user_data = self.data_manager.get_profile()

            if self.user_data:
                # 初始化目标切换按钮文字
                goal = self.user_data.get("goal", "maintain")
                # 将中文目标转换为英文
                goal_mapping = {"减重": "lose", "维持": "maintain", "增重": "gain"}
                if goal in goal_mapping:
                    goal = goal_mapping[goal]
                goal_names = {"lose": "减重", "maintain": "维持", "gain": "增重"}
                self.update_goal_button_text(goal_names[goal])
            else:
                # 文件不存在时，显示提示信息而不是直接返回
                self.show_message("未找到身体数据，请先在'身体数据'模块中填写", "error")
                # 清空计划显示区域
                self.clear_plan_display()
                return

            # 直接从user_plan.json文件获取当前计划
            plan_data = self.data_manager.get_current_plan()

            if plan_data:
                # 显示今日计划
                print("DEBUG: Displaying today's plan")
                self._display_plan(plan_data)
            else:
                # 没有计划文件，尝试生成新的计划
                print("DEBUG: No plan file exists, refreshing plan")
                self.refresh_plan()

        except Exception as e:
            self.show_message(f"加载数据时出错: {str(e)}", "error")
            # 出错时也尝试生成计划
            print(f"DEBUG: Exception occurred: {str(e)}, refreshing plan")
            self.refresh_plan()

    def show_food_selection(self, meal_index, meal_calories, position):
        """显示食物选择器"""
        print(
            f"DEBUG: show_food_selection called with meal_index={meal_index}, meal_calories={meal_calories}, position={position}")
        # 保存当前操作的信息
        self.current_meal_index = meal_index
        self.current_position = position
        print(f"DEBUG: Saved current_meal_index={self.current_meal_index}, current_position={self.current_position}")

        # 创建并显示高级食物选择器
        selector = AdvancedFoodSelector()
        selector.show_food_selector(
            self.on_food_selected,
            meal_calories
        )

    def on_food_selected(self, food_data):
        """当食物被选中时的回调"""
        print(f"DEBUG: on_food_selected called with food_data={food_data}")
        print(f"DEBUG: current_meal_index={self.current_meal_index}, current_position={self.current_position}")
        print(f"DEBUG: current_plan_data={self.current_plan_data}")
        print(f"DEBUG: plan_generator.current_plan={self.plan_generator.current_plan}")
        # 更新当前计划中的食物
        if self.current_position == -1:
            # 添加新食物
            print("DEBUG: Calling add_food_to_meal")
            updated_meal = self.plan_generator.add_food_to_meal(
                self.current_meal_index,
                food_data
            )
        else:
            # 替换现有食物
            print("DEBUG: Calling replace_food_in_me_meal")
            updated_meal = self.plan_generator.replace_food_in_meal(
                self.current_meal_index,
                self.current_position,
                food_data
            )
        print(f"DEBUG: updated_meal returned: {updated_meal is not None}")
        if updated_meal:
            # 更新当前计划数据中的特定餐次
            if isinstance(self.current_plan_data, dict) and 'plan' in self.current_plan_data:
                self.current_plan_data['plan'][self.current_meal_index] = updated_meal
            print("DEBUG: current_plan_data updated")
            # 局部更新显示，而不是刷新整个界面
            self._update_meal_display(self.current_meal_index)
            print("DEBUG: _update_meal_display called")
        else:
            print("DEBUG: updated_meal is None, not updating display")

    def switch_goal(self):
        """切换目标"""
        if not self.user_data:
            self.show_message("请先加载身体数据", "error")
            return

        # 切换目标
        new_goal = self.plan_generator.switch_goal(self.user_data)

        # 重新计算计划的各项数值
        weight = self.user_data.get("current_weight")
        height = self.user_data.get("height")
        age = self.user_data.get("age")
        gender = self.user_data.get("gender", "男")

        # 将中文目标转换为英文
        goal_mapping = {"减重": "lose", "维持": "maintain", "增重": "gain"}
        if new_goal in goal_mapping:
            new_goal = goal_mapping[new_goal]

        # 重新生成计划数据
        plan_data = self.plan_generator.generate_plan(weight, height, age, gender, new_goal)

        # 更新显示
        self._display_plan(plan_data)

        # 使用数据管理器保存更新后的用户数据
        self.data_manager.update_profile(self.user_data)

        # 更新按钮文字
        goal_names = {"lose": "减重", "maintain": "维持", "gain": "增重"}
        self.update_goal_button_text(goal_names[new_goal])

    def update_goal_button_text(self, text):
        """更新目标切换按钮的文字"""
        # 直接通过ID更新按钮文字
        goal_button = self.ids.goal_button
        goal_button.text = text

    def randomize_plan(self):
        """随机生成饮食计划"""
        if not self.user_data:
            self.show_message("请先加载身体数据", "error")
            return

        try:
            # 从用户数据中获取信息
            weight = self.user_data.get("current_weight")  # 修正字段名
            height = self.user_data.get("height")
            age = self.user_data.get("age")
            gender = self.user_data.get("gender", "男")
            goal = self.user_data.get("goal", "maintain")
            # 将中文目标转换为英文
            goal_mapping = {"减重": "lose", "维持": "maintain", "增重": "gain"}
            if goal in goal_mapping:
                goal = goal_mapping[goal]

            # 调用随机生成计划方法
            plan_data = self.plan_generator.generate_random_plan(weight, height, age, gender, goal)
            self._display_plan(plan_data)

            # 保存生成的计划
            self.save_plan()
        except Exception as e:
            self.show_message(f"随机生成计划时出错: {str(e)}", "error")

    def refresh_plan(self):
        """刷新饮食计划"""
        if not self.user_data:
            self.show_message("请先加载身体数据", "error")
            return

        try:
            # 从用户数据中获取信息
            weight = self.user_data.get("current_weight")  # 修正字段名
            height = self.user_data.get("height")
            age = self.user_data.get("age")
            gender = self.user_data.get("gender", "男")
            goal = self.user_data.get("goal", "maintain")
            # 将中文目标转换为英文
            goal_mapping = {"减重": "lose", "维持": "maintain", "增重": "gain"}
            if goal in goal_mapping:
                goal = goal_mapping[goal]

            # 调用原来的生成计划方法
            plan_data = self.plan_generator.generate_plan(weight, height, age, gender, goal)
            self._display_plan(plan_data)

            # 保存生成的计划
            self.save_plan()
        except Exception as e:
            self.show_message(f"刷新计划时出错: {str(e)}", "error")
            # 显示错误信息卡片
            self._display_error_message(f"刷新计划时出错: {str(e)}")

    def _display_error_message(self, error_text):
        """显示错误信息"""
        # 获取结果显示容器
        meals_container = self.ids.meals_container
        # 清除之前的结果
        meals_container.clear_widgets()

        # 添加错误信息卡片
        error_card = self._create_error_card(error_text)
        meals_container.add_widget(error_card)

    def show_message(self, message, msg_type):
        """显示消息 - 使用按钮反馈替代"""
        # 根据消息类型确定反馈颜色
        if msg_type == "error":
            self.show_save_feedback(message, success=False)
        else:
            self.show_save_feedback(message, success=True)
    
    def show_auto_save_notification(self, message):
        """显示自动保存通知 - 使用按钮反馈替代"""
        # 在保存按钮上显示通知
        self.show_save_feedback(message, success=True)
    
    def show_save_feedback(self, message, success=True):
        """显示保存反馈，通过按钮颜色变化和文字修改"""
        if hasattr(self.ids, 'save_button'):
            save_button = self.ids.save_button
            # 保存原始状态
            original_text = save_button.text
            # 修改按钮文字
            save_button.text = message
            # 根据success参数设置按钮状态
            save_button.save_success = success
            
            # 3秒后恢复原始状态
            def restore_button_state(dt):
                save_button.text = original_text
                save_button.save_success = False  # 恢复原始样式
                
            Clock.schedule_once(restore_button_state, 3)

    def save_plan(self):
        """保存当前饮食计划到JSON文件"""
        if not self.current_plan_data:
            self.show_message("没有可保存的计划", "error")
            return

        try:
            # 使用数据管理器保存当前计划到user_plan.json
            # 确保当前计划有正确的日期
            plan_with_date = self.data_manager.save_current_plan(self.current_plan_data)

            # 同时将今天的计划添加到历史记录中
            self.data_manager.add_history_plan(plan_with_date)

            # 显示保存成功反馈（通过按钮颜色变化）
            self.show_save_feedback("已保存", success=True)
            
            # 显示自动保存通知
            self.show_auto_save_notification("已自动保存")
        except Exception as e:
            self.show_save_feedback("保存失败", success=False)

    def clear_plan_display(self):
        """清空计划显示区域"""
        meals_container = self.ids.meals_container
        meals_container.clear_widgets()

        # 显示提示信息
        app = App.get_running_app()
        font_name = 'ChineseFont' if app and app.font_available else 'Roboto' if app and hasattr(app,
                                                                                                 'font_available') else 'Roboto'

        info_label = Label(
            text="暂无今日计划，请点击刷新计划或随机生成创建计划",
            font_name=font_name,
            font_size='16sp',
            color=get_color_from_hex('#8E8E93'),
            size_hint_y=None,
            height=50
        )
        meals_container.add_widget(info_label)

    def _display_plan(self, plan_data):
        """显示饮食计划"""
        print(f"DEBUG: _display_plan called with plan_data={plan_data}")
        print(f"DEBUG: plan_data type: {type(plan_data)}")
        # 保存当前计划数据以便后续保存
        if isinstance(plan_data, dict) and 'plan' in plan_data:
            self.current_plan_data = plan_data
            # 同步计划数据到plan_generator
            self.plan_generator.current_plan = plan_data['plan']
        else:
            # 如果plan_data直接是plan列表
            self.current_plan_data = {
                "plan": plan_data,
                "bmi": 0,
                "bmr": 0,
                "recommended_calories": 0,
                "total_nutrition": {
                    "calories": 0,
                    "protein": 0,
                    "fat": 0,
                    "carbs": 0,
                    "fiber": 0
                },
                "goal": "maintain"
            }
            self.plan_generator.current_plan = plan_data
        print(f"DEBUG: plan_generator.current_plan updated")
        print(f"DEBUG: plan_generator.current_plan type: {type(self.plan_generator.current_plan)}")
        print(f"DEBUG: current_plan_data = {self.current_plan_data}")

        # 获取结果显示容器
        meals_container = self.ids.meals_container
        print(f"DEBUG: meals_container before clear: {len(meals_container.children)} children")
        # 清除之前的结果
        meals_container.clear_widgets()

        # 获取app实例以访问font_available属性
        app = App.get_running_app()

        try:
            # 显示BMI和推荐热量以及总营养成分
            info_card = self._create_info_card(plan_data)
            meals_container.add_widget(info_card)
            print(f"DEBUG: Added info_card to meals_container, now has {len(meals_container.children)} children")

            # 显示饮食计划
            meal_times = ["早餐  07:30", "午餐  12:00", "下午茶  15:30", "晚餐  18:30"]
            # 修复：正确访问plan数据
            plan_list = plan_data['plan'] if isinstance(plan_data, dict) and 'plan' in plan_data else plan_data
            print(f"DEBUG: plan_list has {len(plan_list)} meals")
            for i, meal in enumerate(plan_list):
                print(f"DEBUG: Processing meal {i}: {meal.get('name', 'Unknown')}")
                # 为每个餐次创建一个容器，并设置ID以便后续更新
                meal_container = BoxLayout(
                    orientation='vertical',
                    spacing='12dp',
                    size_hint_y=None,
                    height=300,  # 临时高度，稍后会更新
                    padding=['24dp', '20dp']
                )

                # 绑定最小高度更新
                meal_container.bind(minimum_height=meal_container.setter('height'))
                meal_container.name = f'meal_container_{i}'  # 设置名称用于查找

                # 先添加容器到父容器
                meals_container.add_widget(meal_container)
                print(
                    f"DEBUG: Added meal_container_{i} to meals_container, now has {len(meals_container.children)} children")

                # 应用背景图形（在内容构建之前）
                self._apply_meal_container_graphics(meal_container)

                # 构建餐次内容
                self._build_meal_content(meal_container, i, meal, meal_times)

            print(f"DEBUG: meals_container after adding all meals: {len(meals_container.children)} children")

            # 确保 meals_container 高度正确更新
            def update_meals_container_height(dt):
                # 重新计算所有子组件的高度
                total_height = 0
                spacing = meals_container.spacing
                print(f"DEBUG: meals_container spacing: {spacing}")
                for i, child in enumerate(meals_container.children):
                    child_height = max(child.minimum_height, child.height) if hasattr(child,
                                                                                      'minimum_height') else child.height
                    print(f"DEBUG: Child {i} ({getattr(child, 'name', 'unnamed')}) height: {child_height}")
                    total_height += child_height
                    # 添加间距（除了最后一个元素）
                    if child != meals_container.children[-1]:
                        total_height += spacing
                        print(f"DEBUG: Added spacing {spacing}, total so far: {total_height}")

                meals_container.height = max(total_height, 300)
                print(f"DEBUG: Updated meals_container height to {meals_container.height}")
                print(f"DEBUG: meals_container.minimum_height = {meals_container.minimum_height}")
                print(f"DEBUG: meals_container children count = {len(meals_container.children)}")

            Clock.schedule_once(update_meals_container_height, 0.3)

        except ValueError as e:
            # 输入无效时显示错误信息
            error_card = self._create_error_card("身体数据无效，请检查数据")
            meals_container.add_widget(error_card)
        except Exception as e:
            # 其他错误
            error_card = self._create_error_card(f"生成计划时出错: {str(e)}")
            meals_container.add_widget(error_card)

    def _update_meals_container_height(self):
        """更新 meals_container 的高度"""
        meals_container = self.ids.meals_container
        if meals_container:
            # 重新计算并设置高度
            meals_container.height = meals_container.minimum_height or 300

    def _apply_meal_container_graphics(self, container):
        """为餐次容器应用背景图形"""
        # 直接绘制背景，不使用延迟
        self._draw_meal_container_background(container)

        # 确保位置和大小更新时重新绘制背景
        container.fbind('pos', self._update_meal_container_graphics)
        container.fbind('size', self._update_meal_container_graphics)

    def _draw_meal_container_background(self, container):
        """实际绘制餐次容器背景"""
        # 直接绘制背景
        container.canvas.before.clear()
        from kivy.graphics import Color, RoundedRectangle
        with container.canvas.before:
            Color(rgba=IOS_CARD + [0.85])  # IOS_CARD 已经是 RGBA 列表，直接使用
            RoundedRectangle(
                pos=container.pos,
                size=container.size,
                radius=[24]
            )

    def _update_meal_container_graphics(self, instance, value):
        """更新餐次容器的图形"""
        self._redraw_meal_container_background(instance)

    def _redraw_meal_container_background(self, instance):
        """重新绘制餐次容器背景"""
        instance.canvas.before.clear()
        from kivy.graphics import Color, RoundedRectangle
        with instance.canvas.before:
            Color(rgba=IOS_CARD + [0.85])  # IOS_CARD 已经是 RGBA 列表，直接使用
            RoundedRectangle(
                pos=instance.pos,
                size=instance.size,
                radius=[24]
            )

    def _create_info_card(self, plan_data):

        """创建信息卡片"""

        app = App.get_running_app()

        container = BoxLayout(

            orientation='vertical',

            spacing='12dp',

            size_hint_y=None,

            height=350,  # 增加高度以容纳额外信息（因为营养信息区域变高了）

            padding=['24dp', '20dp']

        )

        container.canvas.before.clear()

        from kivy.graphics import Color, RoundedRectangle

        with container.canvas.before:

            Color(rgba=IOS_CARD + [0.85])  # IOS_CARD 已经是 RGBA 列表，直接使用

            RoundedRectangle(

                pos=container.pos,

                size=container.size,

                radius=[24]

            )

        container.bind(pos=self._update_info_card_graphics, size=self._update_info_card_graphics)

        container.bind(minimum_height=container.setter('height'))

        # BMI信息
        bmi_text = f"BMI: {plan_data.get('bmi', 0):.1f} - "

        if plan_data.get('bmi', 0) < 18.5:

            bmi_text += "偏瘦"

        elif plan_data.get('bmi', 0) < 24:

            bmi_text += "正常"

        elif plan_data.get('bmi', 0) < 28:

            bmi_text += "偏重"

        else:

            bmi_text += "肥胖"

        bmi_label = Label(
            text=bmi_text,
            font_name='ChineseFont' if app.font_available else 'Roboto' if app and hasattr(app,
                                                                                           'font_available') else 'Roboto',
            font_size='16sp',
            color=get_color_from_hex('#000000'),
            size_hint_y=None,
            height=30,
            halign='center'
        )
        bmi_label.bind(size=bmi_label.setter('text_size'))
        container.add_widget(bmi_label)

        # 基础代谢率
        bmr_label = Label(
            text=f"基础代谢率: {plan_data.get('bmr', 0):.0f} 千卡",
            font_name='ChineseFont' if app.font_available else 'Roboto' if app and hasattr(app,
                                                                                           'font_available') else 'Roboto',
            font_size='14sp',
            color=get_color_from_hex('#8E8E93'),
            size_hint_y=None,
            height=25,
            halign='center'
        )
        bmr_label.bind(size=bmr_label.setter('text_size'))
        container.add_widget(bmr_label)

        # 推荐热量摄入
        calories_label = Label(
            text=f"推荐热量摄入: {plan_data.get('recommended_calories', 0):.0f} 千卡",
            font_name='ChineseFont' if app.font_available else 'Roboto' if app and hasattr(app,
                                                                                           'font_available') else 'Roboto',
            font_size='14sp',
            color=get_color_from_hex('#7EDAB8'),
            size_hint_y=None,
            height=25,
            halign='center'
        )
        calories_label.bind(size=calories_label.setter('text_size'))
        container.add_widget(calories_label)

        # 目标
        goal_text = "目标: "
        goal = plan_data.get('goal', 'maintain')
        if goal == 'lose':
            goal_text += "减重"
        elif goal == 'maintain':
            goal_text += "维持"
        else:
            goal_text += "增重"

        goal_label = Label(
            text=goal_text,
            font_name='ChineseFont' if app.font_available else 'Roboto' if app and hasattr(app,
                                                                                           'font_available') else 'Roboto',
            font_size='14sp',
            color=get_color_from_hex('#FF6B6B'),
            size_hint_y=None,
            height=25,
            halign='center'
        )
        goal_label.bind(size=goal_label.setter('text_size'))
        container.add_widget(goal_label)

        # 添加营养信息显示区域（带背景）
        nutrition_container = self._create_nutrition_display(plan_data)
        nutrition_container.name = 'nutrition_display'
        container.add_widget(nutrition_container)

        return container

    def _create_nutrition_display(self, plan_data):
        """创建营养信息显示区域（带背景）"""
        app = App.get_running_app()

        # 创建容器
        container = BoxLayout(
            orientation='vertical',
            spacing='4dp',  # 减小间距
            size_hint_y=None,
            height=100,  # 增加高度以容纳四行信息
            padding=['15dp', '10dp']
        )

        # 设置背景
        container.canvas.before.clear()
        from kivy.graphics import Color, RoundedRectangle
        with container.canvas.before:
            Color(rgba=IOS_CARD + [0.85])
            RoundedRectangle(
                pos=container.pos,
                size=container.size,
                radius=[18]
            )

        # 绑定位置和大小更新
        container.bind(pos=self._update_nutrition_display_graphics, size=self._update_nutrition_display_graphics)
        container.bind(minimum_height=container.setter('height'))

        # 总营养成分（基于当前计划计算）
        total_nutrition = self._calculate_total_nutrition(plan_data)

        # 热量信息（第一行）
        calories_text = f"计划总热量: {total_nutrition['calories']:.0f} 千卡"
        calories_label = Label(
            text=calories_text,
            font_name='ChineseFont' if app.font_available else 'Roboto' if app and hasattr(app,
                                                                                           'font_available') else 'Roboto',
            font_size='12sp',
            color=get_color_from_hex('#8E8E93'),
            size_hint_y=None,
            height=20,
            halign='center'
        )
        calories_label.bind(size=calories_label.setter('text_size'))
        container.add_widget(calories_label)

        # 详细营养成分（第二行）
        nutrition_text = f"蛋白质: {total_nutrition['protein']:.1f}g | 脂肪: {total_nutrition['fat']:.1f}g | 碳水: {total_nutrition['carbs']:.1f}g"
        nutrition_label = Label(
            text=nutrition_text,
            font_name='ChineseFont' if app.font_available else 'Roboto' if app and hasattr(app,
                                                                                           'font_available') else 'Roboto',
            font_size='12sp',
            color=get_color_from_hex('#8E8E93'),
            size_hint_y=None,
            height=20,
            halign='center'
        )
        nutrition_label.bind(size=nutrition_label.setter('text_size'))
        container.add_widget(nutrition_label)

        # 实际摄入量（基于当前页面显示的食物数据实时计算）
        actual_intake = self._calculate_actual_intake()

        # 实际摄入热量（第三行）
        actual_calories_text = f"实际摄入量: {actual_intake['calories']:.0f} 千卡"
        actual_calories_label = Label(
            text=actual_calories_text,
            font_name='ChineseFont' if app.font_available else 'Roboto' if app and hasattr(app,
                                                                                           'font_available') else 'Roboto',
            font_size='12sp',
            color=get_color_from_hex('#8E8E93'),
            size_hint_y=None,
            height=20,
            halign='center'
        )
        actual_calories_label.bind(size=actual_calories_label.setter('text_size'))
        container.add_widget(actual_calories_label)

        # 实际摄入详细营养成分（第四行）
        actual_nutrition_text = f"蛋白质: {actual_intake['protein']:.1f}g | 脂肪: {actual_intake['fat']:.1f}g | 碳水: {actual_intake['carbs']:.1f}g"
        actual_nutrition_label = Label(
            text=actual_nutrition_text,
            font_name='ChineseFont' if app.font_available else 'Roboto' if app and hasattr(app,
                                                                                           'font_available') else 'Roboto',
            font_size='12sp',
            color=get_color_from_hex('#8E8E93'),
            size_hint_y=None,
            height=20,
            halign='center'
        )
        actual_nutrition_label.bind(size=actual_nutrition_label.setter('text_size'))
        container.add_widget(actual_nutrition_label)

        return container

    def _update_nutrition_display_graphics(self, instance, value):
        """更新营养信息显示区域的图形"""
        instance.canvas.before.clear()
        from kivy.graphics import Color, RoundedRectangle
        with instance.canvas.before:
            Color(rgba=IOS_CARD + [0.85])
            RoundedRectangle(
                pos=instance.pos,
                size=instance.size,
                radius=[18]
            )

    def _calculate_total_nutrition(self, plan_data):
        """计算当前计划的总营养成分"""
        # 直接使用plan_data中的total_nutrition
        total_nutrition = plan_data.get('total_nutrition', {
            "calories": 0,
            "protein": 0,
            "fat": 0,
            "carbs": 0,
            "fiber": 0
        })

        # 确保计划总热量与推荐热量一致
        recommended_calories = plan_data.get('recommended_calories', 0)
        if recommended_calories > 0:
            total_nutrition["calories"] = recommended_calories

        return total_nutrition

    def _calculate_actual_intake(self):
        """根据当前页面显示的食物数据实时计算实际摄入量"""
        # 从当前计划数据中计算实际摄入量
        total_nutrition = {
            "calories": 0,
            "protein": 0,
            "fat": 0,
            "carbs": 0
        }

        # 遍历所有餐次，累加营养成分
        if self.current_plan_data and 'plan' in self.current_plan_data:
            plan_list = self.current_plan_data['plan']
            for meal in plan_list:
                total_nutrition["calories"] += meal.get("calories", 0)
                total_nutrition["protein"] += meal.get("protein", 0)
                total_nutrition["fat"] += meal.get("fat", 0)
                total_nutrition["carbs"] += meal.get("carbs", 0)

        return total_nutrition

    def _get_actual_intake(self):
        """获取实际摄入量数据"""
        # 此方法已废弃，保留以确保向后兼容性
        return {
            "calories": 0,
            "protein": 0,
            "fat": 0,
            "carbs": 0
        }

    def _update_info_card_graphics(self, instance, value):

        """更新信息卡片的图形"""

        instance.canvas.before.clear()

        from kivy.graphics import Color, RoundedRectangle

        with instance.canvas.before:
            Color(rgba=IOS_CARD + [0.85])  # IOS_CARD 已经是 RGBA 列表，直接使用

            RoundedRectangle(

                pos=instance.pos,

                size=instance.size,

                radius=[24]

            )

    def _create_error_card(self, error_text):

        """创建错误信息卡片"""

        app = App.get_running_app()
        font_name = 'ChineseFont' if app and app.font_available else 'Roboto' if app and hasattr(app,
                                                                                                 'font_available') else 'Roboto'

        container = BoxLayout(
            orientation='vertical',
            spacing='12dp',
            size_hint_y=None,
            height=150,
            padding=['24dp', '20dp']
        )
        container.canvas.before.clear()
        from kivy.graphics import Color, RoundedRectangle
        with container.canvas.before:
            Color(rgba=IOS_CARD + [0.85])  # IOS_CARD 已经是 RGBA 列表，直接使用
            RoundedRectangle(
                pos=container.pos,
                size=container.size,
                radius=[24]
            )
        container.bind(pos=self._update_error_card_graphics, size=self._update_error_card_graphics)
        container.bind(minimum_height=container.setter('height'))

        error_label = Label(
            text=error_text,
            font_name=font_name,
            font_size='18sp',
            color=get_color_from_hex('#FF3B30'),
            size_hint_y=None,
            height=50
        )
        container.add_widget(error_label)
        return container

    def _update_error_card_graphics(self, instance, value):

        """更新错误卡片的图形"""

        instance.canvas.before.clear()

        from kivy.graphics import Color, RoundedRectangle

        with instance.canvas.before:
            Color(rgba=IOS_CARD + [0.85])  # IOS_CARD 已经是 RGBA 列表，直接使用

            RoundedRectangle(

                pos=instance.pos,

                size=instance.size,

                radius=[24]

            )

    def _build_meal_content(self, container, i, meal, meal_times):

        """构建单个餐次的内容"""
        print(f"DEBUG: _build_meal_content called with container={container}, i={i}, meal={meal}")
        app = App.get_running_app()

        # 清除原有内容但保留背景
        container.clear_widgets()

        # 重新应用背景图形（在清除内容后）
        self._apply_meal_container_graphics(container)

        # 确定餐次类型
        meal_type = meal.get("meal_type", "未知")
        time_label = meal_times[i] if i < len(meal_times) else f"{meal_type}  未知时间"

        # 获取单位和重量信息
        unit = meal.get("unit", "份")
        weight_info = f" | 重量: {meal.get('weight', '未知')}g" if "weight" in meal else ""

        # 添加时间标签
        time_label_widget = Label(
            text=time_label,
            font_name='ChineseFont' if app.font_available else 'Roboto' if app and hasattr(app,
                                                                                           'font_available') else 'Roboto',
            font_size='13sp',
            color=get_color_from_hex('#8E8E93'),
            size_hint_x=1,
            size_hint_y=None,
            height=25
        )
        time_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=30

        )
        time_layout.add_widget(time_label_widget)

        container.add_widget(time_layout)

        # 解析食物组合
        meal_components = meal.get("components", [])
        print(f"DEBUG: meal_components={meal_components}")
        print(f"DEBUG: meal has {len(meal_components)} components")

        # 构建食物显示项
        food_items_height = 0
        for j, component in enumerate(meal_components):
            print(f"DEBUG: Adding component {j}: {component['food']['name']}")
            food_name = component['food']['name']
            food_calories = component['food']['calories']
            food_calories_text = f" ({food_calories}千卡)" if food_calories > 0 else ""

            # 创建食物标签
            food_label = Label(
                text=f"{food_name} ({food_calories}千卡)",
                font_name='ChineseFont' if app.font_available else 'Roboto' if app and hasattr(app,
                                                                                               'font_available') else 'Roboto',
                font_size='16sp',
                color=get_color_from_hex('#000000'),
                size_hint_y=None,
                height=30,
                halign='center',
                valign='middle'
            )

            # 添加提示文本，告知用户可以长按删除
            food_label.tooltip = "点击修改，长按删除"

            # 使用functools.partial来避免lambda闭包问题
            from functools import partial
            # 绑定按下事件
            food_label.bind(on_touch_down=partial(self._on_food_label_touch_down, meal_index=i, position=j,
                                                  meal_calories=meal['calories']))
            # 绑定释放事件
            food_label.bind(on_touch_up=partial(self._on_food_label_touch_up, meal_index=i, position=j))

            food_item = BoxLayout(
                orientation='horizontal',
                spacing='10dp',
                size_hint_y=None,
                height=40
            )
            food_items_height += 40

            # 添加空白控件以实现边距效果
            food_item.add_widget(Widget(size_hint_x=0.1))

            # 添加食物标签容器
            food_label_container = BoxLayout(
                orientation='vertical',
                size_hint_x=0.8,
                size_hint_y=None,
                height=35
            )
            food_label_container.canvas.before.clear()
            from kivy.graphics import Color, RoundedRectangle
            with food_label_container.canvas.before:
                Color(rgba=IOS_BG + [0.9])  # IOS_BG 已经是 RGBA 列表，直接使用
                RoundedRectangle(
                    pos=food_label_container.pos,
                    size=food_label_container.size,
                    radius=[15]
                )
            food_label_container.bind(pos=self._update_food_label_container_graphics,
                                      size=self._update_food_label_container_graphics)

            food_label_container.add_widget(food_label)
            food_item.add_widget(food_label_container)
            food_item.add_widget(Widget(size_hint_x=0.1))
            container.add_widget(food_item)
            print(f"DEBUG: Added food item {j} to container")

            # 添加进度条（默认隐藏）
            from kivy.uix.progressbar import ProgressBar
            progress_bar = ProgressBar(
                max=100,
                value=0,
                size_hint_y=None,
                height=5,
                opacity=0  # 默认隐藏
            )
            food_items_height += 5
            progress_container = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=5
            )
            progress_container.add_widget(Widget(size_hint_x=0.1))
            progress_container.add_widget(progress_bar)
            progress_container.add_widget(Widget(size_hint_x=0.1))
            container.add_widget(progress_container)
            print(f"DEBUG: Added progress bar {j} to container")

            # 保存进度条引用
            progress_bar_key = f"{i}_{j}"
            self.progress_bars[progress_bar_key] = progress_bar

            # 如果不是最后一个食物，添加分隔线
            if j < len(meal_components) - 1:
                separator = Label(
                    text="----",
                    font_name='ChineseFont' if app.font_available else 'Roboto' if app and hasattr(app,
                                                                                                   'font_available') else 'Roboto',
                    font_size='18sp',
                    color=get_color_from_hex('#8E8E93'),
                    size_hint_y=None,
                    height=25,
                    size_hint_x=0.8,
                    halign='center',
                    valign='middle'
                )
                food_items_height += 25

                sep_layout = BoxLayout(
                    orientation='horizontal',
                    spacing='10dp',
                    size_hint_y=None,
                    height=30
                )
                food_items_height += 30

                sep_layout.add_widget(Widget(size_hint_x=0.1))
                sep_layout.add_widget(separator)
                sep_layout.add_widget(Widget(size_hint_x=0.1))
                container.add_widget(sep_layout)
                print(f"DEBUG: Added separator {j} to container")

        # 添加添加食物按钮
        add_label = Label(
            text="+",
            font_name='ChineseFont' if app.font_available else 'Roboto' if app and hasattr(app,
                                                                                           'font_available') else 'Roboto',
            font_size='24sp',
            bold=True,
            color=get_color_from_hex('#000000'),
            size_hint_y=None,
            height=30
        )

        # 绑定触摸事件
        # 使用partial来正确传递参数
        from functools import partial
        add_label.bind(on_touch_down=partial(self._on_add_label_touch, meal_index=i))

        add_button = BoxLayout(
            orientation='horizontal',
            spacing='10dp',
            size_hint_y=None,
            height=40
        )
        food_items_height += 40
        add_button.add_widget(Widget(size_hint_x=0.4))

        add_label_container = BoxLayout(
            orientation='vertical',
            size_hint_x=0.2,
            size_hint_y=None,
            height=35
        )
        add_label_container.canvas.before.clear()
        from kivy.graphics import Color, RoundedRectangle
        with add_label_container.canvas.before:
            Color(rgba=IOS_DIVIDER + [0.9])  # IOS_DIVIDER 已经是 RGBA 列表，直接使用
            RoundedRectangle(
                pos=add_label_container.pos,
                size=add_label_container.size,
                radius=[15]
            )
        add_label_container.bind(pos=self._update_add_label_container_graphics,
                                 size=self._update_add_label_container_graphics)

        add_label_container.add_widget(add_label)
        add_button.add_widget(add_label_container)
        add_button.add_widget(Widget(size_hint_x=0.4))
        container.add_widget(add_button)
        print(f"DEBUG: Added add button to container")

        # 添加营养信息
        calories_text = f"热量: {meal['calories']} 千卡 | {unit}{weight_info}"
        protein_text = f"蛋白质: {meal.get('protein', 0)}g  脂肪: {meal.get('fat', 0)}g  碳水: {meal.get('carbs', 0)}g"

        calories_label = Label(
            text=calories_text,
            font_name='ChineseFont' if app.font_available else 'Roboto' if app and hasattr(app,
                                                                                           'font_available') else 'Roboto',
            font_size='14sp',
            color=get_color_from_hex('#FF6B6B'),
            size_hint_y=None,
            height=25
        )

        nutrition_label = Label(
            text=protein_text,
            font_name='ChineseFont' if app.font_available else 'Roboto' if app and hasattr(app,
                                                                                           'font_available') else 'Roboto',
            font_size='12sp',
            color=get_color_from_hex('#8E8E93'),
            size_hint_y=None,
            height=20
        )
        nutrition_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=50,
            spacing='4dp'

        )
        food_items_height += 50

        nutrition_layout.add_widget(calories_label)
        nutrition_layout.add_widget(nutrition_label)

        container.add_widget(nutrition_layout)
        print(f"DEBUG: Added nutrition info to container")

        # 确保容器高度正确更新
        # 使用 Clock.schedule_once 延迟更新高度，确保所有子组件都已添加完毕
        def update_container_height(dt):
            # 强制重新计算minimum_height
            container.do_layout()
            calculated_height = max(container.minimum_height, 300, food_items_height + 150)  # 150是其他组件的高度估算
            container.height = calculated_height
            print(f"DEBUG: Updated container height to {container.height}")
            print(f"DEBUG: container.minimum_height = {container.minimum_height}")
            print(f"DEBUG: calculated_height = {calculated_height}")
            print(f"DEBUG: container children count = {len(container.children)}")

        Clock.schedule_once(update_container_height, 0.1)
        print("DEBUG: _build_meal_content finished")

    def _update_container_height(self, container):
        """更新容器高度"""
        container.height = container.minimum_height or 300

    def _update_food_label_container_graphics(self, instance, value):

        """更新食物标签容器的图形"""

        instance.canvas.before.clear()

        from kivy.graphics import Color, RoundedRectangle

        with instance.canvas.before:
            Color(rgba=IOS_BG + [0.9])  # 浅灰色背景

            RoundedRectangle(

                pos=instance.pos,

                size=instance.size,

                radius=[15]

            )

    def _update_add_label_container_graphics(self, instance, value):

        """更新添加按钮容器的图形"""

        instance.canvas.before.clear()

        from kivy.graphics import Color, RoundedRectangle

        with instance.canvas.before:
            Color(rgba=IOS_DIVIDER + [0.9])  # 灰色背景

            RoundedRectangle(

                pos=instance.pos,

                size=instance.size,

                radius=[15]

            )

    def _on_food_label_touch_down(self, instance, touch, meal_index, position, meal_calories):
        """食物标签按下事件处理"""
        # 检查触摸是否在实例上
        if not instance.collide_point(*touch.pos):
            return False

        # 检查触摸事件类型
        if touch.is_mouse_scrolling or touch.grab_current is not None:
            return False

        # 显示进度条
        progress_key = f"{meal_index}_{position}"
        if progress_key in self.progress_bars:
            progress_bar = self.progress_bars[progress_key]
            progress_bar.opacity = 1  # 显示进度条
            progress_bar.value = 0  # 重置进度

        # 设置长按检测定时器
        trigger = partial(self._handle_long_press, meal_index, position)
        self.long_press_trigger = Clock.schedule_once(
            lambda dt: trigger(),
            self.long_press_duration
        )

        # 启动进度条动画
        self._animate_progress_bar(meal_index, position)

        touch.ud['long_press_trigger'] = self.long_press_trigger
        return True

    def _animate_progress_bar(self, meal_index, position):
        """动画进度条"""
        progress_key = f"{meal_index}_{position}"
        if progress_key in self.progress_bars:
            progress_bar = self.progress_bars[progress_key]
            # 创建动画，从0到100，持续时间等于长按时间
            from kivy.animation import Animation
            anim = Animation(value=100, duration=self.long_press_duration)
            anim.start(progress_bar)

    def _on_food_label_touch_up(self, instance, touch, meal_index, position):
        """食物标签释放事件处理"""
        # 隐藏进度条
        progress_key = f"{meal_index}_{position}"
        if progress_key in self.progress_bars:
            progress_bar = self.progress_bars[progress_key]
            progress_bar.opacity = 0  # 隐藏进度条
            progress_bar.value = 0  # 重置进度

        # 如果长按触发器存在，取消它并执行点击操作
        if 'long_press_trigger' in touch.ud:
            trigger = touch.ud['long_press_trigger']
            trigger.cancel()  # 取消长按
            touch.ud.pop('long_press_trigger', None)

            # 只有在不是长按的情况下才执行点击操作
            # 检查是否触发了长按事件
            if not hasattr(self, '_long_press_executed') or not self._long_press_executed:
                # 执行点击操作
                # 这里需要获取meal_calories，暂时使用一个默认值
                meal_calories = 0
                if (self.current_plan_data and
                        'plan' in self.current_plan_data and
                        0 <= meal_index < len(self.current_plan_data['plan'])):
                    meal_calories = self.current_plan_data['plan'][meal_index].get('calories', 0)

                self.show_food_selection(meal_index, meal_calories, position)

            # 重置长按执行标志
            if hasattr(self, '_long_press_executed'):
                delattr(self, '_long_press_executed')

        return True

    def _handle_long_press(self, meal_index, position, dt=None):
        """处理长按事件，删除食物"""
        # 设置长按执行标志
        self._long_press_executed = True

        # 清除长按触发器引用
        self.long_press_trigger = None

        # 隐藏进度条
        progress_key = f"{meal_index}_{position}"
        if progress_key in self.progress_bars:
            progress_bar = self.progress_bars[progress_key]
            progress_bar.opacity = 0  # 隐藏进度条
            progress_bar.value = 0  # 重置进度

        self.remove_food_from_meal(meal_index, position)

    def remove_food_from_meal(self, meal_index, position):
        """从餐次中删除食物"""
        try:
            # 从计划数据中删除食物
            updated_meal = self.plan_generator.remove_food_from_meal(meal_index, position)
            if updated_meal:
                # 更新当前计划数据中的特定餐次
                if isinstance(self.current_plan_data, dict) and 'plan' in self.current_plan_data:
                    self.current_plan_data['plan'][meal_index] = updated_meal

                # 保存更新后的计划到文件
                self.save_plan()

                # 更新显示
                self._update_meal_display(meal_index)
                self.show_message("食物已删除", "info")
                return True
            else:
                self.show_message("删除食物失败", "error")
        except Exception as e:
            self.show_message(f"删除食物时出错: {str(e)}", "error")
        return False

    def delete_food(self, meal_index, position):
        """删除指定位置的食物"""
        if self.current_plan_data and 'plan' in self.current_plan_data:
            if 0 <= meal_index < len(self.current_plan_data['plan']):
                meal = self.current_plan_data['plan'][meal_index]
                if 0 <= position < len(meal['foods']):
                    # 删除食物
                    deleted_food = meal['foods'].pop(position)
                    
                    # 更新餐次热量
                    meal['calories'] -= deleted_food.get('calories', 0) * deleted_food.get('quantity', 1)
                    
                    # 更新总营养成分
                    self._update_total_nutrition()
                    
                    # 重新显示计划
                    self._display_plan(self.current_plan_data)
                    
                    # 显示删除成功消息（移除弹窗提示）
                    # self.show_message("食物已删除", "info")
                    return True
                else:
                    # 移除弹窗提示
                    # self.show_message("删除食物失败", "error")
                    return False
            else:
                # 移除弹窗提示
                # self.show_message("删除食物失败", "error")
                return False
        else:
            # 移除弹窗提示
            # self.show_message("删除食物失败", "error")
            return False

    def _update_total_nutrition(self):
        """更新总营养成分"""
        self.total_nutrition = {
            'calories': 0,
            'protein': 0,
            'carbohydrates': 0,
            'fat': 0,
            'fiber': 0,
            'sugar': 0,
            'sodium': 0,
            'vitamin_a': 0,
            'vitamin_c': 0,
            'calcium': 0,
            'iron': 0,
        }
        if self.current_plan_data and 'plan' in self.current_plan_data:
            for meal in self.current_plan_data['plan']:
                self.total_nutrition['calories'] += meal.get('calories', 0)
                self.total_nutrition['protein'] += meal.get('protein', 0)
                self.total_nutrition['carbohydrates'] += meal.get('carbohydrates', 0)
                self.total_nutrition['fat'] += meal.get('fat', 0)
                self.total_nutrition['fiber'] += meal.get('fiber', 0)
                self.total_nutrition['sugar'] += meal.get('sugar', 0)
                self.total_nutrition['sodium'] += meal.get('sodium', 0)
                self.total_nutrition['vitamin_a'] += meal.get('vitamin_a', 0)
                self.total_nutrition['vitamin_c'] += meal.get('vitamin_c', 0)
                self.total_nutrition['calcium'] += meal.get('calcium', 0)
                self.total_nutrition['iron'] += meal.get('iron', 0)

    def _on_add_label_touch(self, instance, touch, meal_index):
        """添加食物标签触摸事件处理"""
        # 检查触摸事件类型
        if touch.is_mouse_scrolling or touch.grab_current is not None:
            return False

        # 单击事件 - 显示食物选择器以添加新食物
        if touch.is_touch and touch.button == 'left':
            if instance.collide_point(*touch.pos):
                if self.current_plan_data and 'plan' in self.current_plan_data:
                    if 0 <= meal_index < len(self.current_plan_data['plan']):
                        meal_calories = self.current_plan_data['plan'][meal_index]['calories']
                        # 显示食物选择器
                        self.show_food_selection(meal_index, meal_calories, -1)  # -1 表示添加新食物
                        return True
        return False

    def _update_meal_display(self, meal_index):
        """更新特定餐次的显示"""
        print(f"DEBUG: _update_meal_display called with meal_index={meal_index}")
        # 同步数据
        if self.current_plan_data and 'plan' in self.current_plan_data:
            self.plan_generator.current_plan = self.current_plan_data['plan']
            print(f"DEBUG: Synchronized plan_generator.current_plan")

        # 查找对应的餐次容器
        meals_container = self.ids.meals_container
        meal_container = None

        # 根据名称查找餐次容器
        for child in meals_container.children:
            if hasattr(child, 'name') and child.name == f'meal_container_{meal_index}':
                meal_container = child
                print(f"DEBUG: Found meal_container for meal_index={meal_index}")
                break

        if meal_container and self.current_plan_data:
            print(f"DEBUG: meal_container and current_plan_data exist")
            print(f"DEBUG: current_plan_data type: {type(self.current_plan_data)}")
            # 重新构建餐次内容
            meal_times = ["早餐  07:30", "午餐  12:00", "下午茶  15:30", "晚餐  18:30"]
            # 修复：正确访问meal数据
            if isinstance(self.current_plan_data, dict) and 'plan' in self.current_plan_data:
                meal = self.current_plan_data['plan'][meal_index]
            else:
                # 如果current_plan_data直接是plan列表
                meal = self.current_plan_data[meal_index]
            print(f"DEBUG: meal data={meal}")
            self._build_meal_content(meal_container, meal_index, meal, meal_times)
            print("DEBUG: _build_meal_content called")

            # 更新信息卡片中的营养信息显示
            self._update_info_card_nutrition()

            # 确保 meals_container 高度正确更新
            def update_parent_height(dt):
                # 重新计算所有子组件的高度
                total_height = 0
                spacing = meals_container.spacing
                print(f"DEBUG: meals_container spacing: {spacing}")
                for i, child in enumerate(meals_container.children):
                    child_height = max(child.minimum_height, child.height) if hasattr(child,
                                                                                      'minimum_height') else child.height
                    print(f"DEBUG: Child {i} ({getattr(child, 'name', 'unnamed')}) height: {child_height}")
                    total_height += child_height
                    # 添加间距（除了最后一个元素）
                    if child != meals_container.children[-1]:
                        total_height += spacing
                        print(f"DEBUG: Added spacing {spacing}, total so far: {total_height}")

                meals_container.height = max(total_height, 300)
                print(f"DEBUG: Updated meals_container height to {meals_container.height}")
                print(f"DEBUG: meals_container.minimum_height = {meals_container.minimum_height}")
                print(f"DEBUG: meals_container children count = {len(meals_container.children)}")

            Clock.schedule_once(update_parent_height, 0.3)
        else:
            print(f"DEBUG: meal_container={meal_container}, current_plan_data={self.current_plan_data}")

    def _update_info_card_nutrition(self):
        """更新信息卡片中的营养信息显示"""
        # 查找信息卡片中的营养信息容器并更新其内容
        meals_container = self.ids.meals_container
        if meals_container.children and len(meals_container.children) > 0:
            # 信息卡片应该是第一个添加的子组件（最后一个在列表中）
            info_card = meals_container.children[-1]
            if info_card and hasattr(info_card, 'children') and len(info_card.children) > 0:
                # 营养信息容器应该是信息卡片的最后一个子组件（第一个在列表中）
                nutrition_container = info_card.children[0]
                if nutrition_container and hasattr(nutrition_container,
                                                   'name') and nutrition_container.name == 'nutrition_display':
                    # 清除原有内容
                    nutrition_container.clear_widgets()

                    # 重新添加营养信息
                    app = App.get_running_app()

                    # 总营养成分（基于当前计划计算）
                    total_nutrition = self._calculate_total_nutrition(self.current_plan_data)

                    # 热量信息（第一行）
                    calories_text = f"计划总热量: {total_nutrition['calories']:.0f} 千卡"
                    calories_label = Label(
                        text=calories_text,
                        font_name='ChineseFont' if app.font_available else 'Roboto' if app and hasattr(app,
                                                                                                       'font_available') else 'Roboto',
                        font_size='12sp',
                        color=get_color_from_hex('#8E8E93'),
                        size_hint_y=None,
                        height=20,
                        halign='center'
                    )
                    calories_label.bind(size=calories_label.setter('text_size'))
                    nutrition_container.add_widget(calories_label)

                    # 详细营养成分（第二行）
                    nutrition_text = f"蛋白质: {total_nutrition['protein']:.1f}g | 脂肪: {total_nutrition['fat']:.1f}g | 碳水: {total_nutrition['carbs']:.1f}g"
                    nutrition_label = Label(
                        text=nutrition_text,
                        font_name='ChineseFont' if app.font_available else 'Roboto' if app and hasattr(app,
                                                                                                       'font_available') else 'Roboto',
                        font_size='12sp',
                        color=get_color_from_hex('#8E8E93'),
                        size_hint_y=None,
                        height=20,
                        halign='center'
                    )
                    nutrition_label.bind(size=nutrition_label.setter('text_size'))
                    nutrition_container.add_widget(nutrition_label)

                    # 实际摄入量（基于当前页面显示的食物数据实时计算）
                    actual_intake = self._calculate_actual_intake()

                    # 实际摄入热量（第三行）
                    actual_calories_text = f"实际摄入量: {actual_intake['calories']:.0f} 千卡"
                    actual_calories_label = Label(
                        text=actual_calories_text,
                        font_name='ChineseFont' if app.font_available else 'Roboto' if app and hasattr(app,
                                                                                                       'font_available') else 'Roboto',
                        font_size='12sp',
                        color=get_color_from_hex('#8E8E93'),
                        size_hint_y=None,
                        height=20,
                        halign='center'
                    )
                    actual_calories_label.bind(size=actual_calories_label.setter('text_size'))
                    nutrition_container.add_widget(actual_calories_label)

                    # 实际摄入详细营养成分（第四行）
                    actual_nutrition_text = f"蛋白质: {actual_intake['protein']:.1f}g | 脂肪: {actual_intake['fat']:.1f}g | 碳水: {actual_intake['carbs']:.1f}g"
                    actual_nutrition_label = Label(
                        text=actual_nutrition_text,
                        font_name='ChineseFont' if app.font_available else 'Roboto' if app and hasattr(app,
                                                                                                       'font_available') else 'Roboto',
                        font_size='12sp',
                        color=get_color_from_hex('#8E8E93'),
                        size_hint_y=None,
                        height=20,
                        halign='center'
                    )
                    actual_nutrition_label.bind(size=actual_nutrition_label.setter('text_size'))
                    nutrition_container.add_widget(actual_nutrition_label)

    def navigate_back(self):
        """返回上一屏幕，使用右滑动效"""
        app = App.get_running_app()
        if hasattr(app, 'navigate_to_screen'):
            app.navigate_to_screen('home', direction='right')
        else:
            app.root.current = 'home'