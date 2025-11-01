# -*- coding: utf-8 -*-
"""
高级食物选择器模块
提供自主搜索、分类查找和热量区间查找功能
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.app import App
from kivy.utils import get_color_from_hex
from kivy.uix.label import Label
from kivy.factory import Factory
from kivy.graphics import Color, RoundedRectangle, Line
import json
from pathlib import Path

# 导入食物数据
from recipe_core import load_food_data, get_grouped_foods

# 数据文件路径
DATA_DIR = Path(__file__).parent.parent.parent / "data"
USER_DATA_DIR = DATA_DIR / "user_data"
RECIPE_FILE = USER_DATA_DIR / "user_recipes.json"

# 定义配色方案 (使用与主应用一致的配色)
from main import IOS_MINT, IOS_CORAL, IOS_BG, IOS_CARD, IOS_DIVIDER, IOS_TEXT_MAIN, IOS_TEXT_SEC, IOS_SUCCESS, IOS_WARNING, IOS_ERROR

# 定义FoodItem类
class FoodItem(BoxLayout):
    def __init__(self, food_data, select_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (1, None)
        self.height = '50dp'  # 进一步缩小高度
        self.padding = '8dp'  # 进一步缩小内边距
        self.spacing = '8dp'  # 进一步缩小间距
        
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[8])  # 进一步缩小圆角
            Color(0.9, 0.9, 0.9, 1)
            self.line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 8), width=1)
        
        self.bind(pos=self.update_graphics_pos, size=self.update_graphics_size)
        
        self.food_data = food_data
        self.select_callback = select_callback
        
        # 创建内部布局
        layout = BoxLayout(orientation='vertical')
        layout.bind(on_touch_down=self.on_item_touch_down)
        
        # 食物名称
        name_label = Label(
            text=food_data.get('name', ''),
            font_name='ChineseFont' if App.get_running_app().font_available else 'Microsoft YaHei',
            color=[0, 0, 0, 1],
            halign='left',
            text_size=(None, None),  # 修复：设置合适的text_size
            valign='middle',
            font_size='14sp',  # 进一步缩小字体
            bold=True,
            size_hint_y=None,  # 修复：明确设置size_hint_y
            height=25  # 修复：明确设置高度
        )
        name_label.bind(texture_size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))  # 修复：绑定texture_size更新text_size
        layout.add_widget(name_label)
        
        # 底部信息行
        info_layout = BoxLayout(orientation='horizontal', spacing='6dp')
        
        # 热量标签
        self.calorie_label = Label(
            text=str(food_data.get('calories', 0)) + ' 千卡',
            font_name='ChineseFont' if App.get_running_app().font_available else 'Microsoft YaHei',
            color=[0, 0, 0, 1],
            halign='left',
            text_size=(None, None),  # 修复：设置合适的text_size
            valign='middle',
            font_size='12sp',
            size_hint_y=None,  # 修复：明确设置size_hint_y
            height=20  # 修复：明确设置高度
        )
        self.calorie_label.bind(texture_size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))  # 修复：绑定texture_size更新text_size
        info_layout.add_widget(self.calorie_label)
        
        # 单位和重量信息
        unit_text = food_data.get('unit', '份')
        if 'weight' in food_data:
            unit_text += ' | ' + str(food_data.get('weight', '未知')) + 'g'
            
        unit_label = Label(
            text=unit_text,
            font_name='ChineseFont' if App.get_running_app().font_available else 'Microsoft YaHei',
            color=[0.56, 0.56, 0.59, 1],  # #8E8E93
            halign='left',
            text_size=(None, None),  # 修复：设置合适的text_size
            valign='middle',
            font_size='10sp',
            size_hint_y=None,  # 修复：明确设置size_hint_y
            height=20  # 修复：明确设置高度
        )
        unit_label.bind(texture_size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))  # 修复：绑定texture_size更新text_size
        info_layout.add_widget(unit_label)
        
        layout.add_widget(info_layout)
        self.add_widget(layout)
        
        # 根据热量值设置颜色
        self.update_calorie_color()
    
    def update_graphics_pos(self, instance, value):
        self.rect.pos = self.pos
        self.line.rounded_rectangle = (self.x, self.y, self.width, self.height, 8)
    
    def update_graphics_size(self, instance, value):
        self.rect.size = self.size
        self.line.rounded_rectangle = (self.x, self.y, self.width, self.height, 8)
    
    def on_item_touch_down(self, instance, touch):
        if self.collide_point(*touch.pos):
            # 添加按下效果
            self.canvas.before.clear()
            with self.canvas.before:
                Color(0.8, 0.8, 0.8, 1)  # 灰色按下效果
                self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
                Color(0.7, 0.7, 0.7, 1)
                self.line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 8), width=1)
            
            # 延迟恢复原状
            from kivy.clock import Clock
            Clock.schedule_once(self.restore_normal_state, 0.1)
            
            self.select_callback(self.food_data)
            return True
        return False
    
    def restore_normal_state(self, dt):
        """恢复正常的视觉状态"""
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
            Color(0.9, 0.9, 0.9, 1)
            self.line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 8), width=1)
    
    def update_calorie_color(self):
        """根据热量值更新颜色"""
        calories = self.food_data.get("calories", 0)
        if calories <= 100:
            self.calorie_label.color = IOS_SUCCESS  # 绿色 - 低热量
        elif calories <= 300:
            self.calorie_label.color = IOS_MINT     # 薄荷绿 - 中等热量
        else:
            self.calorie_label.color = IOS_CORAL    # 珊瑚橙 - 高热量

# KV语言定义移到外部，避免中文字符问题
kv_string = '''
<AdvancedFoodSelector>:
    orientation: 'vertical'
    padding: '10dp'
    spacing: '10dp'
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    # 顶部标题区域
    BoxLayout:
        size_hint_y: None
        height: '35dp'
        padding: '6dp', '2dp'
        canvas.before:
            Color:
                rgba: 0.95, 0.95, 0.95, 1
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [6]
        Label:
            id: title_label
            text: '食物选择器'
            font_name: 'ChineseFont' if app.font_available else 'Microsoft YaHei'
            font_size: '16sp'
            color: 0, 0, 0, 1
            bold: True
            halign: 'center'
            valign: 'middle'  # 修复：添加垂直对齐
            text_size: self.size  # 修复：绑定text_size
    
    # 搜索区域
    BoxLayout:
        size_hint_y: None
        height: '35dp'
        spacing: '6dp'
        
        TextInput:
            id: search_input
            hint_text: '搜索食物名称...'
            font_name: 'ChineseFont' if app.font_available else 'Microsoft YaHei'
            font_size: '13sp'
            multiline: False
            on_text: root.on_search_text_change(self.text)
            foreground_color: [0, 0, 0, 1]
            hint_text_color: [0.5, 0.5, 0.5, 1]
            padding_x: '10dp'
            padding_y: '10dp'
            # 添加input_type属性以支持中文输入
            input_type: 'text'
            # 添加write_tab属性以支持中文输入法
            write_tab: False
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [18]
                Color:
                    rgba: 0.8, 0.8, 0.8, 1
                Line:
                    rounded_rectangle: self.x, self.y, self.width, self.height, 18
                    width: 1.0
        
        Button:
            text: '清除'
            font_name: 'ChineseFont' if app.font_available else 'Microsoft YaHei'
            font_size: '13sp'
            size_hint_x: None
            width: '50dp'
            background_color: 0.9, 0.9, 0.9, 1
            color: 0, 0, 0, 1
            on_press: root.clear_search()
            on_touch_down: root.on_button_touch_down(self, args[1])
            on_touch_up: root.on_button_touch_up(self, args[1])
            canvas.before:
                Color:
                    rgba: 0.9, 0.9, 0.9, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [18]
    
    # 筛选区域
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: self.minimum_height
        spacing: '10dp'
        
        # 分类筛选区域
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            
            Label:
                text: '按分类筛选'
                font_name: 'ChineseFont' if app.font_available else 'Microsoft YaHei'
                font_size: '13sp'
                color: 0, 0, 0, 1
                size_hint_y: None
                height: '18dp'
                halign: 'left'
                valign: 'middle'  # 修复：添加垂直对齐
                text_size: self.size  # 修复：绑定text_size
            
            BoxLayout:
                size_hint_y: None
                height: '32dp'
                spacing: '5dp'
                
                ScrollView:
                    do_scroll_y: False
                    bar_width: 0
                    BoxLayout:
                        id: category_buttons_container
                        orientation: 'horizontal'
                        spacing: '5dp'
                        size_hint_x: None
                        width: self.minimum_width
                        
                        Button:
                            text: '全部'
                            font_name: 'ChineseFont' if app.font_available else 'Microsoft YaHei'
                            font_size: '12sp'
                            size_hint_x: None
                            width: '50dp'
                            background_color: 0.5, 0.85, 0.72, 1
                            color: 1, 1, 1, 1
                            on_press: root.filter_by_category(None)
                            on_touch_down: root.on_button_touch_down(self, args[1])
                            on_touch_up: root.on_button_touch_up(self, args[1])
                            canvas.before:
                                Color:
                                    rgba: 0.5, 0.85, 0.72, 1
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [14]
                        
                        Button:
                            text: '主食'
                            font_name: 'ChineseFont' if app.font_available else 'Microsoft YaHei'
                            font_size: '12sp'
                            size_hint_x: None
                            width: '50dp'
                            background_color: 1, 1, 1, 1
                            color: 0, 0, 0, 1
                            on_press: root.filter_by_category('staple_foods')
                            on_touch_down: root.on_button_touch_down(self, args[1])
                            on_touch_up: root.on_button_touch_up(self, args[1])
                            canvas.before:
                                Color:
                                    rgba: 1, 1, 1, 1
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [14]
                                Color:
                                    rgba: 0.8, 0.8, 0.8, 1
                                Line:
                                    rounded_rectangle: self.x, self.y, self.width, self.height, 14
                                    width: 1.0
                        
                        Button:
                            text: '水果'
                            font_name: 'ChineseFont' if app.font_available else 'Microsoft YaHei'
                            font_size: '12sp'
                            size_hint_x: None
                            width: '50dp'
                            background_color: 1, 1, 1, 1
                            color: 0, 0, 0, 1
                            on_press: root.filter_by_category('fruits')
                            on_touch_down: root.on_button_touch_down(self, args[1])
                            on_touch_up: root.on_button_touch_up(self, args[1])
                            canvas.before:
                                Color:
                                    rgba: 1, 1, 1, 1
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [14]
                                Color:
                                    rgba: 0.8, 0.8, 0.8, 1
                                Line:
                                    rounded_rectangle: self.x, self.y, self.width, self.height, 14
                                    width: 1.0
                        
                        Button:
                            text: '零食'
                            font_name: 'ChineseFont' if app.font_available else 'Microsoft YaHei'
                            font_size: '12sp'
                            size_hint_x: None
                            width: '50dp'
                            background_color: 1, 1, 1, 1
                            color: 0, 0, 0, 1
                            on_press: root.filter_by_category('snacks')
                            on_touch_down: root.on_button_touch_down(self, args[1])
                            on_touch_up: root.on_button_touch_up(self, args[1])
                            canvas.before:
                                Color:
                                    rgba: 1, 1, 1, 1
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [14]
                                Color:
                                    rgba: 0.8, 0.8, 0.8, 1
                                Line:
                                    rounded_rectangle: self.x, self.y, self.width, self.height, 14
                                    width: 1.0
                        
                        Button:
                            text: '成品菜'
                            font_name: 'ChineseFont' if app.font_available else 'Microsoft YaHei'
                            font_size: '12sp'
                            size_hint_x: None
                            width: '50dp'
                            background_color: 1, 1, 1, 1
                            color: 0, 0, 0, 1
                            on_press: root.filter_by_category('prepared_dishes')
                            on_touch_down: root.on_button_touch_down(self, args[1])
                            on_touch_up: root.on_button_touch_up(self, args[1])
                            canvas.before:
                                Color:
                                    rgba: 1, 1, 1, 1
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [14]
                                Color:
                                    rgba: 0.8, 0.8, 0.8, 1
                                Line:
                                    rounded_rectangle: self.x, self.y, self.width, self.height, 14
                                    width: 1.0
                        
                        Button:
                            text: '我的食谱'
                            font_name: 'ChineseFont' if app.font_available else 'Microsoft YaHei'
                            font_size: '12sp'
                            size_hint_x: None
                            width: '65dp'
                            background_color: 1, 1, 1, 1
                            color: 0, 0, 0, 1
                            on_press: root.filter_by_category('user_recipes')
                            on_touch_down: root.on_button_touch_down(self, args[1])
                            on_touch_up: root.on_button_touch_up(self, args[1])
                            canvas.before:
                                Color:
                                    rgba: 1, 1, 1, 1
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [14]
                                Color:
                                    rgba: 0.8, 0.8, 0.8, 1
                                Line:
                                    rounded_rectangle: self.x, self.y, self.width, self.height, 14
                                    width: 1.0
        
        # 热量筛选区域
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            
            Label:
                text: '按热量筛选 (千卡)'
                font_name: 'ChineseFont' if app.font_available else 'Microsoft YaHei'
                font_size: '13sp'
                color: 0, 0, 0, 1
                size_hint_y: None
                height: '18dp'
                halign: 'left'
                valign: 'middle'  # 修复：添加垂直对齐
                text_size: self.size  # 修复：绑定text_size
            
            BoxLayout:
                size_hint_y: None
                height: '35dp'
                spacing: '6dp'
                
                TextInput:
                    id: min_calorie_input
                    hint_text: '最小值'
                    font_name: 'ChineseFont' if app.font_available else 'Microsoft YaHei'
                    font_size: '13sp'
                    multiline: False
                    input_type: 'number'
                    size_hint_x: 0.4
                    foreground_color: [0, 0, 0, 1]
                    hint_text_color: [0.5, 0.5, 0.5, 1]
                    padding_x: '10dp'
                    padding_y: '10dp'
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [18]
                        Color:
                            rgba: 0.8, 0.8, 0.8, 1
                        Line:
                            rounded_rectangle: self.x, self.y, self.width, self.height, 18
                            width: 1.0
                
                Label:
                    text: '-'
                    font_name: 'ChineseFont' if app.font_available else 'Microsoft YaHei'
                    font_size: '13sp'
                    size_hint_x: None
                    width: '14dp'
                    color: [0, 0, 0, 1]
                    halign: 'center'
                    valign: 'middle'  # 修复：添加垂直对齐
                    text_size: self.size  # 修复：绑定text_size
                
                TextInput:
                    id: max_calorie_input
                    hint_text: '最大值'
                    font_name: 'ChineseFont' if app.font_available else 'Microsoft YaHei'
                    font_size: '13sp'
                    multiline: False
                    input_type: 'number'
                    size_hint_x: 0.4
                    foreground_color: [0, 0, 0, 1]
                    hint_text_color: [0.5, 0.5, 0.5, 1]
                    padding_x: '10dp'
                    padding_y: '10dp'
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [18]
                        Color:
                            rgba: 0.8, 0.8, 0.8, 1
                        Line:
                            rounded_rectangle: self.x, self.y, self.width, self.height, 18
                            width: 1.0
                
                Button:
                    text: '筛选'
                    font_name: 'ChineseFont' if app.font_available else 'Microsoft YaHei'
                    font_size: '13sp'
                    size_hint_x: None
                    width: '50dp'
                    background_color: 0.5, 0.85, 0.72, 1
                    color: 1, 1, 1, 1
                    on_press: root.filter_by_calories()
                    on_touch_down: root.on_button_touch_down(self, args[1])
                    on_touch_up: root.on_button_touch_up(self, args[1])
                    canvas.before:
                        Color:
                            rgba: 0.5, 0.85, 0.72, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [18]
                
                Button:
                    text: '清除'
                    font_name: 'ChineseFont' if app.font_available else 'Microsoft YaHei'
                    font_size: '13sp'
                    size_hint_x: None
                    width: '50dp'
                    background_color: 0.9, 0.9, 0.9, 1
                    color: 0, 0, 0, 1
                    on_press: root.clear_calorie_filter()
                    on_touch_down: root.on_button_touch_down(self, args[1])
                    on_touch_up: root.on_button_touch_up(self, args[1])
                    canvas.before:
                        Color:
                            rgba: 0.9, 0.9, 0.9, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [18]
    
    # 食物列表区域
    ScrollView:
        id: food_scroll
        bar_width: 6
        scroll_type: ['bars', 'content']
        bar_color: 0.5, 0.85, 0.72, 1
        bar_inactive_color: 0.8, 0.8, 0.8, 1
        
        BoxLayout:
            id: food_list_container
            orientation: 'vertical'
            spacing: '6dp'
            size_hint_y: None
            height: self.minimum_height
            padding: '3dp'

'''

Builder.load_string(kv_string)

class AdvancedFoodSelector(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.food_data = self._load_all_food_data()
        self.filtered_foods = []
        self.current_selection_callback = None
        self.current_meal_calories = 0
        self.popup = None
        self.active_category_button = None
        self.category_buttons = {}
        self.search_timer = None
        self.touch_start_pos = None
        
    def _load_all_food_data(self):
        """加载所有食物数据"""
        # 从recipe_core加载基础数据
        fruits, staple_foods, prepared_dishes, snacks = load_food_data()
        
        # 加载用户自定义食谱
        user_recipes = []
        if RECIPE_FILE.exists():
            try:
                with open(RECIPE_FILE, 'r', encoding='utf-8') as f:
                    user_recipes = json.load(f)
            except Exception as e:
                print(f"读取用户食谱时出错: {e}")
        
        # 组织数据结构
        food_data = {
            "user_recipes": user_recipes,
            "staple_foods": staple_foods,
            "fruits": fruits,
            "snacks": snacks,
            "prepared_dishes": prepared_dishes,
            "all_foods": user_recipes + staple_foods + fruits + snacks + prepared_dishes
        }
        
        return food_data
    
    def show_food_selector(self, selection_callback, current_meal_calories=0):
        """显示高级食物选择器"""
        self.current_selection_callback = selection_callback
        self.current_meal_calories = current_meal_calories
        
        # 更新标题显示当前餐食热量
        if hasattr(self, 'ids') and 'title_label' in self.ids:
            self.ids.title_label.text = f'食物选择器 (目标: {current_meal_calories} 千卡)'
        
        # 显示所有食物
        self.filtered_foods = self.food_data["all_foods"]
        self._display_foods()
        
        # 显示弹窗
        self.popup = Popup(
            title='',  # 标题在内部实现
            content=self,
            size_hint=(0.95, 0.95),
            auto_dismiss=True,  # 启用自动关闭
            separator_height=0  # 隐藏默认分隔线
        )
        self.popup.open()
    
    def on_search_text_change(self, search_text):
        """搜索文本改变时的处理"""
        # 使用防抖技术减少频繁更新
        from kivy.clock import Clock
        if self.search_timer:
            Clock.unschedule(self.search_timer)
        self.search_timer = Clock.schedule_once(lambda dt: self._perform_search(search_text), 0.3)
    
    def _perform_search(self, search_text):
        """执行搜索"""
        if not search_text:
            self.filtered_foods = self.food_data["all_foods"]
        else:
            # 支持中文搜索
            self.filtered_foods = [
                food for food in self.food_data["all_foods"] 
                if search_text.lower() in food["name"].lower() or 
                   search_text in food["name"]
            ]
        self._display_foods()
    
    def clear_search(self):
        """清除搜索"""
        self.ids.search_input.text = ""
        self.filtered_foods = self.food_data["all_foods"]
        self._display_foods()
    
    def filter_by_category(self, category):
        """按分类筛选"""
        # 更新按钮状态
        self._update_category_buttons(category)
        
        if category is None:
            # 显示所有食物
            self.filtered_foods = self.food_data["all_foods"]
        elif category == "user_recipes":
            # 显示用户自定义食谱
            self.filtered_foods = self.food_data["user_recipes"]
        else:
            # 显示指定分类的食物
            self.filtered_foods = self.food_data[category]
        
        self._display_foods()
    
    def _update_category_buttons(self, active_category):
        """更新分类按钮的视觉状态"""
        # 重置所有按钮为默认状态
        for cat, button in self.category_buttons.items():
            if cat == active_category:
                # 激活状态 - 薄荷绿背景
                button.background_color = IOS_MINT
                button.color = [1, 1, 1, 1]  # 白色文字
            else:
                # 默认状态 - 白色背景
                button.background_color = [1, 1, 1, 1]
                button.color = [0, 0, 0, 1]  # 黑色文字
    
    def filter_by_calories(self):
        """按热量范围筛选"""
        try:
            min_cal = float(self.ids.min_calorie_input.text) if self.ids.min_calorie_input.text else 0
            max_cal = float(self.ids.max_calorie_input.text) if self.ids.max_calorie_input.text else float('inf')
            
            filtered = []
            for food in self.food_data["all_foods"]:  # 始终基于所有食物筛选
                cal = food.get("calories", 0)
                if min_cal <= cal <= max_cal:
                    filtered.append(food)
            
            self.filtered_foods = filtered
            self._display_foods()
        except ValueError:
            # 输入无效时忽略
            pass
    
    def clear_calorie_filter(self):
        """清除热量筛选"""
        self.ids.min_calorie_input.text = ""
        self.ids.max_calorie_input.text = ""
        # 重新应用当前分类筛选
        self._display_foods()
    
    def _display_foods(self):
        """显示食物列表"""
        container = self.ids.food_list_container
        container.clear_widgets()
        
        if not self.filtered_foods:
            # 显示无结果提示
            no_result = Builder.load_string('''
BoxLayout:
    orientation: 'vertical'
    size_hint_y: None
    height: '50dp'
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [8]
    Label:
        text: '未找到符合条件的食物'
        font_name: 'ChineseFont' if app.font_available else 'Microsoft YaHei'
        font_size: '14sp'
        color: [0.5, 0.5, 0.5, 1]
        halign: 'center'  # 修复：添加水平对齐
        valign: 'middle'  # 修复：添加垂直对齐
        text_size: self.size  # 修复：绑定text_size
''')
            container.add_widget(no_result)
            return
        
        # 按首字母分组
        grouped_foods = get_grouped_foods(self.filtered_foods)
        
        # 限制显示的食物数量以提高性能
        max_foods_to_display = 200
        foods_count = 0
        
        # 显示分组的食物
        for letter in sorted(grouped_foods.keys()):
            group_foods = grouped_foods[letter]
            
            # 添加分组标题
            group_header = Builder.load_string(f'''
BoxLayout:
    orientation: 'vertical'
    size_hint_y: None
    height: '28dp'
    padding: '6dp', '2dp'
    canvas.before:
        Color:
            rgba: 0.95, 0.95, 0.95, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [6]
    Label:
        text: '{letter}'
        font_name: 'ChineseFont' if app.font_available else 'Microsoft YaHei'
        font_size: '14sp'
        color: [1, 0.42, 0.42, 1]
        halign: 'left'
        text_size: self.size
        valign: 'middle'
        bold: True
''')
            container.add_widget(group_header)
            
            # 添加该组的食物
            for food in group_foods:
                # 创建食物项
                food_item = FoodItem(food, self.select_food_callback)
                container.add_widget(food_item)
                
                # 限制显示的食物数量
                foods_count += 1
                if foods_count >= max_foods_to_display:
                    # 添加提示信息
                    more_foods_label = Builder.load_string('''
BoxLayout:
    orientation: 'vertical'
    size_hint_y: None
    height: '40dp'
    padding: '6dp', '2dp'
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [6]
    Label:
        text: '还有更多食物，请使用搜索功能查找'
        font_name: 'ChineseFont' if app.font_available else 'Microsoft YaHei'
        font_size: '12sp'
        color: [0.5, 0.5, 0.5, 1]
        halign: 'center'
        text_size: self.size
        valign: 'middle'
''')
                    container.add_widget(more_foods_label)
                    return
    
    def select_food_callback(self, food_data):
        """食物选择回调"""
        if self.current_selection_callback:
            self.current_selection_callback(food_data)
        self.dismiss_popup()
    
    def dismiss_popup(self):
        """关闭弹窗"""
        if self.popup:
            self.popup.dismiss()
            self.popup = None
    
    def on_button_touch_down(self, button, touch):
        """按钮按下时的处理"""
        if button.collide_point(*touch.pos):
            # 按下时改变按钮颜色
            button.background_color = get_color_from_hex("#CCCCCC")  # 灰色
            button.color = [0, 0, 0, 1]  # 黑色文字
            return True
        return False
    
    def on_button_touch_up(self, button, touch):
        """按钮释放时的处理"""
        # 恢复按钮颜色
        if button.text in ['全部']:
            button.background_color = IOS_MINT  # 薄荷绿
            button.color = [1, 1, 1, 1]  # 白色文字
        elif button.text in ['筛选', '清除']:
            # 检查按钮文本以确定颜色
            if button.text == '筛选':
                button.background_color = IOS_MINT  # 薄荷绿
            else:
                button.background_color = [0.9, 0.9, 0.9, 1]  # 灰色
            button.color = [0, 0, 0, 1]  # 黑色文字
        else:
            button.background_color = [1, 1, 1, 1]  # 白色背景
            button.color = [0, 0, 0, 1]  # 黑色文字
        return False
    
    def handle_key_down(self, text_input, key, keycode, text, modifiers, more_str=None):
        """处理键盘按键事件，确保中文输入正常工作"""
        # 当有文本输入时，触发搜索
        if text and text.strip():
            # 使用Clock调度来确保输入法组合字符已经完成
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.on_search_text_change(text_input.text), 0.1)
        return False