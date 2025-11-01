# -*- coding: utf-8 -*-
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from components.custom_widgets import FlatButton, Card, StyledTextInput
from kivy.utils import get_color_from_hex as rgba
from kivy.clock import Clock
import json
from pathlib import Path
from kivy.app import App
# 导入颜色常量
from main import IOS_MINT, IOS_CORAL, IOS_ORANGE, IOS_BG, IOS_CARD, IOS_DIVIDER, IOS_TEXT_MAIN, IOS_TEXT_SEC
import time

# 数据文件路径
DATA_DIR = Path(__file__).parent.parent.parent / "data"
USER_DATA_DIR = DATA_DIR / "user_data"
RECIPE_FILE = USER_DATA_DIR / "user_recipes.json"

# 在这里定义RecipeScreen的KV语言
recipe_screen_kv = '''
#:import FlatButton components.custom_widgets.FlatButton
#:import Card components.custom_widgets.Card
#:import StyledTextInput components.custom_widgets.StyledTextInput

<RecipeScreen>:
    name: 'recipes'
    BoxLayout:
        orientation: 'vertical'

        # Header
        BoxLayout:
            size_hint_y: None
            height: '108dp'
            padding: '24dp', '48dp', '24dp', '12dp'
            Label:
                text: "食谱管理"
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

                # 食物名称输入
                Card:
                    size_hint_y: None
                    height: self.minimum_height
                    BoxLayout:
                        orientation: 'vertical'
                        spacing: '16dp'
                        size_hint_y: None
                        height: self.minimum_height

                        Label:
                            text: "食物名称"
                            font_name: 'ChineseFont' if app.font_available else 'Roboto'
                            font_size: '16sp'
                            color: rgba('#000000')
                            size_hint_y: None
                            height: '30dp'
                        StyledTextInput:
                            id: food_name_input
                            hint_text: "请输入食物名称"
                            multiline: False
                            size_hint_y: None
                            height: '48dp'

                # 营养成分输入
                Card:
                    size_hint_y: None
                    height: self.minimum_height
                    BoxLayout:
                        orientation: 'vertical'
                        spacing: '16dp'
                        size_hint_y: None
                        height: self.minimum_height

                        Label:
                            text: "营养成分 (每100g)"
                            font_name: 'ChineseFont' if app.font_available else 'Roboto'
                            font_size: '16sp'
                            color: rgba('#000000')
                            size_hint_y: None
                            height: '30dp'

                        BoxLayout:
                            orientation: 'vertical'
                            spacing: '8dp'
                            size_hint_y: None
                            height: self.minimum_height
                            Label:
                                text: "热量 (千卡)"
                                font_name: 'ChineseFont' if app.font_available else 'Roboto'
                                font_size: '14sp'
                                color: rgba('#000000')
                                size_hint_y: None
                                height: '25dp'
                            StyledTextInput:
                                id: calories_input
                                hint_text: "例如: 120"
                                input_filter: 'float'
                                multiline: False
                                size_hint_y: None
                                height: '48dp'

                        BoxLayout:
                            orientation: 'vertical'
                            spacing: '8dp'
                            size_hint_y: None
                            height: self.minimum_height
                            Label:
                                text: "蛋白质 (g)"
                                font_name: 'ChineseFont' if app.font_available else 'Roboto'
                                font_size: '14sp'
                                color: rgba('#000000')
                                size_hint_y: None
                                height: '25dp'
                            StyledTextInput:
                                id: protein_input
                                hint_text: "例如: 5.2"
                                input_filter: 'float'
                                multiline: False
                                size_hint_y: None
                                height: '48dp'

                        BoxLayout:
                            orientation: 'vertical'
                            spacing: '8dp'
                            size_hint_y: None
                            height: self.minimum_height
                            Label:
                                text: "脂肪 (g)"
                                font_name: 'ChineseFont' if app.font_available else 'Roboto'
                                font_size: '14sp'
                                color: rgba('#000000')
                                size_hint_y: None
                                height: '25dp'
                            StyledTextInput:
                                id: fat_input
                                hint_text: "例如: 3.1"
                                input_filter: 'float'
                                multiline: False
                                size_hint_y: None
                                height: '48dp'

                        BoxLayout:
                            orientation: 'vertical'
                            spacing: '8dp'
                            size_hint_y: None
                            height: self.minimum_height
                            Label:
                                text: "碳水化合物 (g)"
                                font_name: 'ChineseFont' if app.font_available else 'Roboto'
                                font_size: '14sp'
                                color: rgba('#000000')
                                size_hint_y: None
                                height: '25dp'
                            StyledTextInput:
                                id: carbs_input
                                hint_text: "例如: 20.5"
                                input_filter: 'float'
                                multiline: False
                                size_hint_y: None
                                height: '48dp'

                # 操作按钮
                BoxLayout:
                    orientation: 'horizontal'
                    spacing: '10dp'
                    size_hint_y: None
                    height: '48dp'
                    FlatButton:
                        id: add_button
                        text: "添加"
                        on_press: root.save_food()
                    FlatButton:
                        text: "取消"
                        on_press: root.clear_inputs()

                # 食谱列表区域
                Card:
                    size_hint_y: None
                    height: self.minimum_height
                    BoxLayout:
                        orientation: 'vertical'
                        spacing: '15dp'
                        size_hint_y: None
                        height: self.minimum_height
                        Label:
                            text: "已有食谱"
                            font_name: 'ChineseFont' if app.font_available else 'Roboto'
                            font_size: '18sp'
                            color: rgba('#000000')
                            size_hint_y: None
                            height: '30dp'
                            bold: True
                        BoxLayout:
                            id: recipe_list_container
                            orientation: 'vertical'
                            spacing: '15dp'
                            size_hint_y: None
                            height: self.minimum_height
'''

Builder.load_string(recipe_screen_kv)


class RecipeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._is_first_popup = True  # 标记是否是第一个弹窗
        # 在屏幕初始化时绑定事件，确保界面加载完成后刷新食谱列表
        self.bind(on_enter=self.refresh_recipe_list)
    
    def on_kv_post(self, base_widget):
        """在KV文件加载完成后执行"""
        super().on_kv_post(base_widget)
        # 初始刷新食谱列表
        self.refresh_recipe_list()
    
    def refresh_recipe_list(self, *args):
        """刷新食谱列表"""
        # 确保界面元素已经加载
        if not hasattr(self, 'ids') or 'recipe_list_container' not in self.ids:
            return
            
        container = self.ids.recipe_list_container
        container.clear_widgets()
        
        # 检查食谱文件是否存在
        if not RECIPE_FILE.exists():
            # 如果食谱文件不存在，显示提示信息
            no_recipe_label = Builder.load_string('''
Label:
    text: "暂无食谱，请添加食物"
    font_size: '16sp'
    color: rgba('#8E8E93')
    font_name: 'ChineseFont' if app.font_available else 'DroidSans'
    size_hint_y: None
    height: '30dp'
''')
            container.add_widget(no_recipe_label)
            return
        
        # 读取食谱数据
        try:
            with open(RECIPE_FILE, 'r', encoding='utf-8') as f:
                recipes = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            recipes = []
        
        # 如果没有食谱，显示提示信息
        if not recipes:
            no_recipe_label = Builder.load_string('''
Label:
    text: "暂无食谱，请添加食物"
    font_size: '16sp'
    color: rgba('#8E8E93')
    font_name: 'ChineseFont' if app.font_available else 'DroidSans'
    size_hint_y: None
    height: '30dp'
''')
            container.add_widget(no_recipe_label)
            return
        
        # 显示食谱列表
        total_calories = 0
        for recipe in recipes:
            total_calories += recipe.get('calories', 0)
            # 创建食谱项的KV代码
            recipe_item_kv = f'''
BoxLayout:
    orientation: 'horizontal'
    size_hint_y: None
    height: '60dp'
    padding: '10dp', '5dp'
    canvas.before:
        Color:
            rgba: rgba('#FFFFFF') + [0.85]
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12]
    BoxLayout:
        orientation: 'vertical'
        size_hint_x: 0.7
        Label:
            text: "{recipe['name']}"
            font_size: '16sp'
            color: rgba('#000000')
            font_name: 'ChineseFont' if app.font_available else 'DroidSans'
            size_hint_y: 0.6
            halign: 'left'
            valign: 'bottom'
        Label:
            text: "热量: {recipe.get('calories', 0)} 千卡"
            font_size: '14sp'
            color: rgba('#8E8E93')
            font_name: 'ChineseFont' if app.font_available else 'DroidSans'
            size_hint_y: 0.4
            halign: 'left'
            valign: 'top'
    Label:
        text: ">"
        font_size: '24sp'
        color: rgba('#C0C0C0')
        size_hint_x: 0.3
        halign: 'right'
        valign: 'middle'
'''
            recipe_item = Builder.load_string(recipe_item_kv)
            container.add_widget(recipe_item)
        
        # 显示总热量
        total_calories_label = Builder.load_string(f'''
Label:
    text: "总热量: {round(total_calories, 1)} 千卡"
    font_size: '16sp'
    color: rgba('#7EDAB8')
    font_name: 'ChineseFont' if app.font_available else 'DroidSans'
    size_hint_y: None
    height: '30dp'
    halign: 'right'
    valign: 'middle'
    bold: True
''')
        container.add_widget(total_calories_label)
    
    def save_food(self):
        """保存食物到食谱"""
        # 获取输入值
        try:
            name = self.ids.food_name_input.text.strip()
            if not name:
                # 使用按钮反馈替代弹窗提示
                self.show_save_feedback("名称不能为空", success=False)
                return

            calories = float(self.ids.calories_input.text) if self.ids.calories_input.text else 0
            protein = float(self.ids.protein_input.text) if self.ids.protein_input.text else 0
            fat = float(self.ids.fat_input.text) if self.ids.fat_input.text else 0
            carbs = float(self.ids.carbs_input.text) if self.ids.carbs_input.text else 0

            # 验证数据
            if calories < 0 or protein < 0 or fat < 0 or carbs < 0:
                # 使用按钮反馈替代弹窗提示
                self.show_save_feedback("数值不能为负", success=False)
                return

            # 创建食物数据
            food_data = {
                "id": int(time.time() * 1000),  # 使用时间戳作为唯一ID
                "name": name,
                "calories": calories,
                "protein": protein,
                "fat": fat,
                "carbs": carbs,
                "unit": "100g"
            }

            # 读取现有食谱数据
            if RECIPE_FILE.exists():
                with open(RECIPE_FILE, 'r', encoding='utf-8') as f:
                    recipes = json.load(f)
            else:
                recipes = []

            # 添加新食物
            recipes.append(food_data)

            # 保存到文件
            with open(RECIPE_FILE, 'w', encoding='utf-8') as f:
                json.dump(recipes, f, ensure_ascii=False, indent=2)

            # 清空输入框
            self.clear_inputs()

            # 显示保存成功反馈（通过按钮颜色变化）
            self.show_save_feedback("已保存", success=True)

            # 刷新食谱列表
            self.refresh_recipe_list()
            
        except ValueError:
            # 使用按钮反馈替代弹窗提示
            self.show_save_feedback("输入格式错误", success=False)
        except Exception as e:
            print(f"保存用户食谱时出错: {e}")
            # 使用按钮反馈替代弹窗提示
            self.show_save_feedback("保存失败", success=False)
    
    def show_save_feedback(self, message, success=True):
        """显示保存反馈，通过按钮颜色变化和文字修改"""
        if hasattr(self.ids, 'add_button'):
            add_button = self.ids.add_button
            # 保存原始状态
            original_text = add_button.text
            # 修改按钮文字
            add_button.text = message
            # 根据success参数设置按钮状态
            add_button.save_success = success
            
            # 3秒后恢复原始状态
            def restore_button_state(dt):
                add_button.text = original_text
                add_button.save_success = False  # 恢复原始样式
                
            Clock.schedule_once(restore_button_state, 3)
    
    def clear_inputs(self):
        """清空输入框"""
        self.ids.food_name_input.text = ""
        self.ids.calories_input.text = ""
        self.ids.protein_input.text = ""
        self.ids.fat_input.text = ""
        self.ids.carbs_input.text = ""
    
    def show_popup(self, title, content):
        """显示弹窗消息 - 使用按钮反馈替代"""
        # 使用保存按钮显示反馈
        self.show_save_feedback(content, success=True)
    
    def show_auto_save_notification(self, message):
        """显示自动保存通知 - 使用按钮反馈替代"""
        self.show_save_feedback(message, success=True)

    def navigate_back(self):
        """返回上一个屏幕"""
        app = App.get_running_app()
        if hasattr(app, 'navigate_to_screen'):
            app.navigate_to_screen('home', direction='right')
        else:
            # 备用方案：如果navigate_to_screen方法不存在，则使用root.current
            app.root.current = 'home'