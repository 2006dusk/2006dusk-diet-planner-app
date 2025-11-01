# -*- coding: utf-8 -*-
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.utils import get_color_from_hex
from kivy.lang import Builder
from kivy.app import App
from kivy.graphics import Color, RoundedRectangle, Line
import json
from pathlib import Path
from datetime import datetime

# 导入rgba函数供KV文件使用
from kivy.utils import get_color_from_hex as rgba

# 从主应用导入颜色常量
from main import IOS_MINT, IOS_CORAL, IOS_BG, IOS_CARD, IOS_DIVIDER, IOS_TEXT_MAIN, IOS_TEXT_SEC

# 导入数据管理器
from utils.data_manager import DataManager

# 在这里定义TodayPlanScreen的KV语言
today_plan_screen_kv = '''
#:import FlatButton components.custom_widgets.FlatButton
#:import Card components.custom_widgets.Card

<TodayPlanScreen>:
    name: 'water'
    BoxLayout:
        orientation: 'vertical'

        # Header
        BoxLayout:
            size_hint_y: None
            height: '108dp'
            padding: '24dp', '48dp', '24dp', '12dp'
            Label:
                text: "今日饮食计划"
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

                # 信息概览卡片
                BoxLayout:
                    id: overview_card
                    orientation: 'vertical'
                    spacing: '15dp'
                    size_hint_y: None
                    height: self.minimum_height
                    padding: ['24dp', '20dp']

                    Label:
                        id: date_label
                        text: "今日计划"
                        font_name: 'ChineseFont' if app.font_available else 'Roboto'
                        font_size: '18sp'
                        color: rgba('#000000')
                        size_hint_y: None
                        height: '30dp'
                        bold: True

                    BoxLayout:
                        orientation: 'horizontal'
                        spacing: '20dp'
                        size_hint_y: None
                        height: '60dp'

                        BoxLayout:
                            orientation: 'vertical'
                            spacing: '5dp'

                            Label:
                                text: "总热量"
                                font_name: 'ChineseFont' if app.font_available else 'Roboto'
                                font_size: '14sp'
                                color: rgba('#8E8E93')

                            Label:
                                id: total_calories
                                text: "0 千卡"
                                font_name: 'ChineseFont' if app.font_available else 'Roboto'
                                font_size: '16sp'
                                color: rgba('#FF6B6B')
                                bold: True

                        BoxLayout:
                            orientation: 'vertical'
                            spacing: '5dp'

                            Label:
                                text: "餐次"
                                font_name: 'ChineseFont' if app.font_available else 'Roboto'
                                font_size: '14sp'
                                color: rgba('#8E8E93')

                            Label:
                                id: meal_count
                                text: "0 餐"
                                font_name: 'ChineseFont' if app.font_available else 'Roboto'
                                font_size: '16sp'
                                color: rgba('#7EDAB8')
                                bold: True

                # 规划显示区域 - 统一样式的餐次模块集合
                GridLayout:
                    id: meals_grid
                    cols: 1
                    spacing: '20dp'
                    size_hint_y: None
                    height: self.minimum_height
'''

Builder.load_string(today_plan_screen_kv)


class MealModule(BoxLayout):
    """
    统一的餐次模块组件
    根据每个文字的高度，动态计算背景的高度，避免文字重叠
    """

    def __init__(self, meal_data=None, meal_time="", **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.padding = [15, 15, 15, 15]
        self.spacing = 15  # 增加组件间距，避免重叠

        # 初始化UI
        self._init_ui(meal_data, meal_time)

        # 绑定图形更新
        self.bind(pos=self._update_graphics, size=self._update_graphics)

    def _init_ui(self, meal_data, meal_time):
        """初始化UI组件"""
        app = App.get_running_app()

        # 标题行
        title_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=35  # 增加高度避免重叠
        )

        title_label = Label(
            text=meal_time.split()[0] if meal_time else "未知餐次",
            font_name='ChineseFont' if app.font_available else 'Roboto',
            font_size='16sp',
            color=IOS_TEXT_MAIN,
            halign='left',
            valign='middle'
        )

        time_label = Label(
            text=meal_time.split()[1] if " " in meal_time else "",
            font_name='ChineseFont' if app.font_available else 'Roboto',
            font_size='14sp',
            color=IOS_TEXT_SEC,
            halign='right',
            valign='middle'
        )

        title_box.add_widget(title_label)
        title_box.add_widget(time_label)
        self.add_widget(title_box)

        # 食物列表区域
        foods_box = GridLayout(
            cols=1,
            spacing=8  # 增加食物项之间的间距
        )

        if not meal_data or not meal_data.get("components"):
            # 显示空状态
            empty_label = Label(
                text="暂无食物",
                font_name='ChineseFont' if app.font_available else 'Roboto',
                font_size='14sp',
                color=IOS_TEXT_SEC,
                size_hint_y=None,
                height=25  # 增加高度
            )
            foods_box.add_widget(empty_label)
        else:
            # 显示食物列表（显示所有食物）
            components = meal_data.get("components", [])
            for i, component in enumerate(components):
                food_box = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=22  # 增加高度避免重叠
                )

                food_name = Label(
                    text=component['food']['name'],
                    font_name='ChineseFont' if app.font_available else 'Roboto',
                    font_size='14sp',
                    color=IOS_TEXT_MAIN,
                    halign='left',
                    valign='middle'
                )

                food_calories = Label(
                    text=f"{component['food']['calories']}千卡",
                    font_name='ChineseFont' if app.font_available else 'Roboto',
                    font_size='12sp',
                    color=IOS_CORAL,
                    halign='right',
                    valign='middle'
                )

                food_box.add_widget(food_name)
                food_box.add_widget(food_calories)
                foods_box.add_widget(food_box)

                # 如果不是最后一个食物且总数大于1，添加分隔线

        self.add_widget(foods_box)

        # 分隔线

        # 营养信息行
        nutrition_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=35  # 增加高度避免重叠
        )

        calories_text = f"{meal_data.get('calories', 0) if meal_data else 0}千卡"
        calories_label = Label(
            text=calories_text,
            font_name='ChineseFont' if app.font_available else 'Roboto',
            font_size='14sp',
            color=IOS_CORAL,
            bold=True,
            halign='left',
            valign='middle',
            size_hint_x=0.4
        )

        nutrients_box = BoxLayout(
            orientation='horizontal',
            spacing=10,  # 增加营养信息项之间的间距
            size_hint_x=0.6
        )

        protein_text = f"蛋白质: {meal_data.get('protein', 0) if meal_data else 0}g"
        fat_text = f"脂肪: {meal_data.get('fat', 0) if meal_data else 0}g"
        carbs_text = f"碳水: {meal_data.get('carbs', 0) if meal_data else 0}g"

        protein_label = Label(
            text=protein_text,
            font_name='ChineseFont' if app.font_available else 'Roboto',
            font_size='11sp',
            color=IOS_TEXT_SEC,
            halign='left',
            valign='middle',
            size_hint_x=0.33
        )

        fat_label = Label(
            text=fat_text,
            font_name='ChineseFont' if app.font_available else 'Roboto',
            font_size='11sp',
            color=IOS_TEXT_SEC,
            halign='center',
            valign='middle',
            size_hint_x=0.33
        )

        carbs_label = Label(
            text=carbs_text,
            font_name='ChineseFont' if app.font_available else 'Roboto',
            font_size='11sp',
            color=IOS_TEXT_SEC,
            halign='right',
            valign='middle',
            size_hint_x=0.33
        )

        nutrients_box.add_widget(protein_label)
        nutrients_box.add_widget(fat_label)
        nutrients_box.add_widget(carbs_label)

        nutrition_box.add_widget(calories_label)
        nutrition_box.add_widget(nutrients_box)
        self.add_widget(nutrition_box)

        # 设置组件高度 - 根据每个文字的高度动态计算，并留有余量避免重叠
        title_height = 35  # 标题行高度
        foods_height = len(meal_data.get("components", [])) * 22 if meal_data and meal_data.get(
            "components") else 25  # 食物列表高度
        food_spacings = max(0, len(meal_data.get("components", [])) - 1) * 8 if meal_data and meal_data.get(
            "components") else 0  # 食物间距
        separators_height = 0  # 已移除分割线
        middle_separator_height = 0  # 已移除分割线
        nutrition_height = 35  # 营养信息行高度
        padding_height = 30  # 上下内边距高度
        spacing_height = 30  # 内部组件间距高度

        self.height = title_height + foods_height + food_spacings + separators_height + middle_separator_height + nutrition_height + padding_height + spacing_height

        # 更新图形
        self._update_graphics()

    def _update_graphics(self, *args):
        """更新卡片背景图形"""
        self.canvas.before.clear()
        with self.canvas.before:
            # 绘制背景
            Color(rgba=IOS_CARD + [0.95])
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[20]
            )

            # 添加边框
            Color(rgba=IOS_DIVIDER + [0.7])
            Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, 20),
                width=1
            )


class TodayPlanScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.plan_data = None
        self.data_manager = DataManager()

    def navigate_back(self):
        """返回主页，使用左滑动效"""
        app = App.get_running_app()
        if hasattr(app, 'navigate_to_screen'):
            app.navigate_to_screen('home', direction='right')
        else:
            print("导航功能不可用")

    def on_pre_enter(self):
        """在进入屏幕前加载数据"""
        self.load_plan_data()

    def load_plan_data(self):
        """加载计划数据"""
        try:
            # 使用数据管理器获取当前计划
            self.plan_data = self.data_manager.get_current_plan()

            if self.plan_data:
                # 显示计划
                self.display_plan()
            else:
                self.show_message("未找到今日规划数据")
        except Exception as e:
            self.show_message(f"加载数据时出错: {str(e)}")

    def display_plan(self):
        """显示今日规划"""
        # 获取结果显示容器
        meals_grid = self.ids.meals_grid
        # 清除之前的结果
        meals_grid.clear_widgets()

        # 获取概览卡片并应用背景
        overview_card = self.ids.overview_card
        self._apply_overview_card_graphics(overview_card)
        overview_card.bind(pos=self._update_overview_card_graphics, size=self._update_overview_card_graphics)

        # 更新日期标签
        date_label = self.ids.date_label
        if self.plan_data and "date" in self.plan_data:
            date_label.text = f"今日计划 ({self.plan_data['date']})"
        else:
            date_label.text = f"今日计划 ({datetime.now().strftime('%Y-%m-%d')})"

        if not self.plan_data:
            self.show_message("无规划数据")
            return

        try:
            # 更新总览信息
            total_calories = self.ids.total_calories
            # 计算实际摄入热量（基于当前页面显示的食物数据实时计算）
            actual_intake = self._calculate_actual_intake()
            total_calories.text = f"{actual_intake['calories']:.0f} 千卡"

            meal_count = self.ids.meal_count
            meal_count.text = f"{len(self.plan_data.get('plan', []))} 餐"

            # 显示饮食计划 - 使用统一样式的餐次模块
            meal_times = ["早餐 07:30", "午餐 12:00", "下午茶 15:30", "晚餐 18:30"]
            for i, meal in enumerate(self.plan_data.get('plan', [])):
                # 获取餐次时间
                meal_time = meal_times[i] if i < len(meal_times) else f"餐次 {i + 1}"

                # 创建统一样式的餐次模块
                meal_module = MealModule(
                    meal_data=meal,
                    meal_time=meal_time
                )

                meals_grid.add_widget(meal_module)

        except Exception as e:
            self.show_message(f"显示规划时出错: {str(e)}")

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
        if self.plan_data and 'plan' in self.plan_data:
            plan_list = self.plan_data['plan']
            for meal in plan_list:
                total_nutrition["calories"] += meal.get("calories", 0)
                total_nutrition["protein"] += meal.get("protein", 0)
                total_nutrition["fat"] += meal.get("fat", 0)
                total_nutrition["carbs"] += meal.get("carbs", 0)

        return total_nutrition

    def _apply_overview_card_graphics(self, container):
        """为概览卡片应用背景图形"""
        # 直接绘制背景
        self._draw_overview_card_background(container)

    def _draw_overview_card_background(self, container):
        """实际绘制概览卡片背景"""
        # 清除之前的背景
        container.canvas.before.clear()

        # 绘制新背景
        with container.canvas.before:
            Color(rgba=IOS_CARD + [0.95])  # 使用IOS_CARD颜色
            RoundedRectangle(
                pos=container.pos,
                size=container.size,
                radius=[24]
            )

            # 添加边框
            Color(rgba=IOS_DIVIDER + [0.7])
            Line(
                rounded_rectangle=(container.x, container.y, container.width, container.height, 24),
                width=1.2
            )

    def _update_overview_card_graphics(self, instance, value):
        """更新概览卡片的图形"""
        # 使用Clock.schedule_once确保在布局完成后更新背景
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self._redraw_overview_card_background(instance), 0)

    def _redraw_overview_card_background(self, instance):
        """重新绘制概览卡片背景"""
        # 确保在UI线程中执行
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self._do_redraw_overview_card_background(instance), 0)

    def _do_redraw_overview_card_background(self, instance):
        """实际执行重新绘制概览卡片背景"""
        if hasattr(instance, 'canvas') and hasattr(instance.canvas, 'before'):
            # 清除之前的背景
            instance.canvas.before.clear()

            # 绘制新背景
            with instance.canvas.before:
                Color(rgba=IOS_CARD + [0.95])  # 使用IOS_CARD颜色
                RoundedRectangle(
                    pos=instance.pos,
                    size=instance.size,
                    radius=[24]
                )

                # 添加边框
                Color(rgba=IOS_DIVIDER + [0.7])
                Line(
                    rounded_rectangle=(instance.x, instance.y, instance.width, instance.height, 24),
                    width=1.2
                )

    def show_message(self, message):
        """显示消息"""
        print(f"[INFO] {message}")