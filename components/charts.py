# -*- coding: utf-8 -*-
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Line, Ellipse
from kivy.utils import get_color_from_hex
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.app import App
import os
import json
from datetime import datetime

# 导入统一数据管理器
from utils.data_manager import DataManager


class LineChart(BoxLayout):
    def __init__(self, data_points=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.data_points = data_points or []
        self.bind(size=self.draw_chart, pos=self.draw_chart)
        self.nutrition_view = "breakfast"  # breakfast, lunch, dinner (默认改为早餐)
        print(f"初始化图表，数据点数量: {len(self.data_points)}")
        
    def _draw_single_point_chart(self, chart_container):
        """绘制单点图表"""
        # 获取画布尺寸
        width, height = chart_container.size
        x, y = chart_container.pos
        
        # 如果尺寸还没准备好，稍后再试
        if width <= 0 or height <= 0:
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self._draw_single_point_chart(chart_container), 0.01)
            return

        # 设置边距
        margin_left = 10
        margin_right = 10
        margin_top = 30
        margin_bottom = 50
        chart_width = width - margin_left - margin_right
        chart_height = height - margin_top - margin_bottom

        if chart_width <= 0 or chart_height <= 0:
            print("图表尺寸无效，不绘制图表")
            return

        # 获取数据点
        point = self.data_points[0]
        date = point.get('date', '')
        
        # 获取应用程序实例以访问字体设置
        app = App.get_running_app()
        font_name = app.font_name if app and hasattr(app, 'font_name') else 'Roboto'

        # 检查数据类型并绘制相应图表
        if 'weight' in point:
            self._draw_single_weight_point(chart_container, margin_left, margin_right, margin_top, margin_bottom, 
                                         chart_width, chart_height, x, y, point, date, font_name)
        elif 'body_fat' in point:
            self._draw_single_body_fat_point(chart_container, margin_left, margin_right, margin_top, margin_bottom, 
                                           chart_width, chart_height, x, y, point, date, font_name)
        elif 'breakfast' in point:
            self._draw_single_nutrition_point(chart_container, margin_left, margin_right, margin_top, margin_bottom, 
                                            chart_width, chart_height, x, y, point, date, font_name)

    def draw_chart(self, *args):
        """绘制折线图"""
        # 清除之前添加的容器
        for child in self.children[:]:
            self.remove_widget(child)
        
        print(f"绘制图表，数据点数量: {len(self.data_points) if self.data_points else 0}")

        if not self.data_points or len(self.data_points) == 0:
            print("没有数据点，不绘制图表")
            # 显示无数据提示
            no_data_label = Label(
                text="暂无数据",
                halign='center',
                valign='middle'
            )
            self.add_widget(no_data_label)
            return
        
        # 当只有一天数据时，显示单点数据
        if len(self.data_points) < 2:
            print("数据点少于2个，显示单点数据")
            # 创建图表区域
            chart_container = FloatLayout()
            self.add_widget(chart_container)
            
            # 确保容器已经被添加并获取正确的尺寸
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self._draw_single_point_chart(chart_container), 0)
            return

        # 创建图表区域和时间标签区域
        chart_container = FloatLayout()
        self.add_widget(chart_container)
        
        time_container = BoxLayout(size_hint_y=0.1, spacing=10)
        self.add_widget(time_container)

        # 确保容器已经被添加并获取正确的尺寸
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self._draw_chart_content(chart_container, time_container), 0)

    def _draw_single_weight_point(self, chart_container, margin_left, margin_right, margin_top, margin_bottom, 
                                chart_width, chart_height, x, y, point, date, font_name):
        """绘制单个体重点数据"""
        weight = point['weight']
        
        # 计算坐标范围，增加一些边距使数据不贴边
        min_weight = weight - 1
        max_weight = weight + 1
        weight_range = max_weight - min_weight
        
        # 数据点位置（居中显示）
        px = x + margin_left + chart_width / 2
        py = y + margin_bottom + chart_height / 2
        
        # 绘制坐标轴
        with chart_container.canvas:
            Color(0.2, 0.2, 0.2, 1)  # 深灰色
            # X轴
            Line(points=[x + margin_left, y + margin_bottom, x + margin_left + chart_width, y + margin_bottom], width=1)
            # Y轴
            Line(points=[x + margin_left, y + margin_bottom, x + margin_left, y + margin_bottom + chart_height], width=1)
            
            # 绘制数据点
            Color(0.5, 0.9, 0.7, 1)  # 薄荷绿
            Ellipse(pos=(px-4, py-4), size=(8, 8))
        
        # 添加数值标签
        value_label = Label(
            text=str(weight),
            center_x=px,
            center_y=py + 20,
            font_size='12sp',
            font_name=font_name,
            color=(0, 0, 0, 1),
            size_hint=(None, None),
            size=(50, 20),
            halign='center',
            valign='middle'
        )
        chart_container.add_widget(value_label)
        
        # 添加Y轴标签
        y_label = Label(
            text="体重(kg)",
            pos=(x + margin_left + 15, y + margin_bottom + chart_height // 2 - 10),
            size=(30, 20),
            font_size='12sp',
            font_name=font_name,
            color=(0.3, 0.3, 0.3, 1)
        )
        chart_container.add_widget(y_label)
        
        # 添加日期标签
        date_label = Label(
            text=date,
            center_x=px,
            y=y + margin_bottom - 30,
            font_size='10sp',
            font_name=font_name,
            color=(0.3, 0.3, 0.3, 1),
            size_hint=(None, None),
            size=(50, 20),
            halign='center',
            valign='middle'
        )
        chart_container.add_widget(date_label)
        
    def _draw_single_body_fat_point(self, chart_container, margin_left, margin_right, margin_top, margin_bottom, 
                                  chart_width, chart_height, x, y, point, date, font_name):
        """绘制单个体脂率数据点"""
        body_fat = point['body_fat']
        
        # 计算坐标范围
        min_body_fat = body_fat - 1
        max_body_fat = body_fat + 1
        body_fat_range = max_body_fat - min_body_fat
        
        # 数据点位置（居中显示）
        px = x + margin_left + chart_width / 2
        py = y + margin_bottom + chart_height / 2
        
        # 绘制坐标轴
        with chart_container.canvas:
            Color(0.2, 0.2, 0.2, 1)  # 深灰色
            # X轴
            Line(points=[x + margin_left, y + margin_bottom, x + margin_left + chart_width, y + margin_bottom], width=1)
            # Y轴
            Line(points=[x + margin_left, y + margin_bottom, x + margin_left, y + margin_bottom + chart_height], width=1)
            
            # 绘制数据点
            Color(0.9, 0.5, 0.7, 1)  # 粉红色
            Ellipse(pos=(px-4, py-4), size=(8, 8))
        
        # 添加数值标签
        value_label = Label(
            text=str(body_fat),
            center_x=px,
            center_y=py + 20,
            font_size='12sp',
            font_name=font_name,
            color=(0, 0, 0, 1),
            size_hint=(None, None),
            size=(50, 20),
            halign='center',
            valign='middle'
        )
        chart_container.add_widget(value_label)
        
        # 添加Y轴标签
        y_label = Label(
            text="体脂率(%)",
            pos=(x + margin_left + 15, y + margin_bottom + chart_height // 2 - 10),
            size=(40, 20),
            font_size='12sp',
            font_name=font_name,
            color=(0.3, 0.3, 0.3, 1),
            halign='left'
        )
        chart_container.add_widget(y_label)
        
        # 添加日期标签
        date_label = Label(
            text=date,
            center_x=px,
            y=y + margin_bottom - 30,
            font_size='10sp',
            font_name=font_name,
            color=(0.3, 0.3, 0.3, 1),
            size_hint=(None, None),
            size=(50, 20),
            halign='center',
            valign='middle'
        )
        chart_container.add_widget(date_label)
        
    def _draw_single_nutrition_point(self, chart_container, margin_left, margin_right, margin_top, margin_bottom, 
                                   chart_width, chart_height, x, y, point, date, font_name):
        """绘制单个营养摄入数据点"""
        # 根据当前视图选择要绘制的数据
        calories = 0
        color = (0.2, 0.6, 1, 1)
        label_text = ""
        
        if self.nutrition_view == "breakfast":
            calories = point['breakfast']
            label_text = "早餐"
            color = (1, 0.4, 0.4, 1)  # 红色
        elif self.nutrition_view == "lunch":
            calories = point['lunch']
            label_text = "午餐"
            color = (0.3, 0.8, 0.7, 1)  # 青色
        elif self.nutrition_view == "dinner":
            calories = point['dinner']
            label_text = "晚餐"
            color = (0.5, 0.9, 0.7, 1)  # 绿色
        
        # 计算坐标范围
        min_calories = calories * 0.5
        max_calories = calories * 1.5 if calories > 0 else 100
        calories_range = max_calories - min_calories
        
        # 数据点位置（居中显示）
        px = x + margin_left + chart_width / 2
        py = y + margin_bottom + chart_height / 2
        
        # 绘制坐标轴
        with chart_container.canvas:
            Color(0.2, 0.2, 0.2, 1)  # 深灰色
            # X轴
            Line(points=[x + margin_left, y + margin_bottom, x + margin_left + chart_width, y + margin_bottom], width=1)
            # Y轴
            Line(points=[x + margin_left, y + margin_bottom, x + margin_left, y + margin_bottom + chart_height], width=1)
            
            # 绘制数据点
            Color(*color)
            Ellipse(pos=(px-4, py-4), size=(8, 8))
        
        # 添加数值标签
        value_label = Label(
            text=str(calories),
            center_x=px,
            center_y=py + 20,
            font_size='12sp',
            font_name=font_name,
            color=(0, 0, 0, 1),
            size_hint=(None, None),
            size=(50, 20),
            halign='center',
            valign='middle'
        )
        chart_container.add_widget(value_label)
        
        # 添加Y轴标签
        y_label = Label(
            text="卡路里(kcal)",
            pos=(x + margin_left + 15, y + margin_bottom + chart_height // 2 - 10),
            size=(50, 20),
            font_size='12sp',
            font_name=font_name,
            color=(0.3, 0.3, 0.3, 1),
            halign='left'
        )
        chart_container.add_widget(y_label)
        
        # 添加日期标签
        date_label = Label(
            text=date,
            center_x=px,
            y=y + margin_bottom - 30,
            font_size='10sp',
            font_name=font_name,
            color=(0.3, 0.3, 0.3, 1),
            size_hint=(None, None),
            size=(50, 20),
            halign='center',
            valign='middle'
        )
        chart_container.add_widget(date_label)
        
        # 添加餐类标签
        meal_label = Label(
            text=label_text,
            center_x=px,
            y=y + margin_bottom - 50,
            font_size='10sp',
            font_name=font_name,
            color=(0.3, 0.3, 0.3, 1),
            size_hint=(None, None),
            size=(50, 20),
            halign='center',
            valign='middle'
        )
        chart_container.add_widget(meal_label)
        
        # 添加切换按钮
        toggle_button = Button(
            text="早餐" if self.nutrition_view == "breakfast" else "午餐" if self.nutrition_view == "lunch" else "晚餐",
            size_hint=(None, None),
            size=(60, 30),
            pos_hint={'right': 0.98, 'top': 0.98},
            font_name=font_name,
            background_color=(0.2, 0.6, 1, 1)
        )
        
        def on_toggle_button_press(instance):
            view_order = ["breakfast", "lunch", "dinner"]
            current_index = view_order.index(self.nutrition_view)
            next_index = (current_index + 1) % len(view_order)
            self.nutrition_view = view_order[next_index]
            self.draw_chart()
        
        toggle_button.bind(on_press=on_toggle_button_press)
        chart_container.add_widget(toggle_button)
        
    def _load_user_profile(self):
        """加载用户配置文件"""
        try:
            # 使用统一数据管理器加载用户档案
            data_manager = DataManager()
            return data_manager.get_profile()
        except Exception as e:
            print(f"加载用户配置文件时出错: {e}")
        return None

    def _format_date_label(self, date_str, chart_type):
        """根据图表类型格式化日期标签"""
        try:
            # 解析日期
            if '月' in date_str:  # 年视图的月份数据，如"10月"
                return date_str
            
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            
            if chart_type == "week":
                # 周视图：显示日期，如"10/28"
                return f"{date_obj.month}/{date_obj.day}"
            elif chart_type == "month":
                # 月视图：显示日期，如"10/28"
                return f"{date_obj.month}/{date_obj.day}"
            elif chart_type == "year":
                # 年视图：显示月份，如"10月"
                return f"{date_obj.month}月"
            else:
                return date_str
        except Exception as e:
            print(f"日期格式化错误: {e}")
            return date_str

    def _draw_chart_content(self, chart_container, time_container):
        # 获取画布尺寸
        width, height = chart_container.size
        x, y = chart_container.pos
        
        # 如果尺寸还没准备好，稍后再试
        if width <= 0 or height <= 0:
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self._draw_chart_content(chart_container, time_container), 0.01)
            return

        # 设置更大的边距以适应标签，略微放大图表区域
        margin_left = 10  # 增加左侧边距以容纳数值标签和Y轴
        margin_right = 10
        margin_top = 30
        margin_bottom = 50  # 增加底部边距以容纳日期标签
        chart_width = width - margin_left - margin_right
        chart_height = height - margin_top - margin_bottom

        if chart_width <= 0 or chart_height <= 0:
            print("图表尺寸无效，不绘制图表")
            return

        print(f"图表尺寸: {width}x{height}, 画布位置: ({x}, {y})")
        print(f"图表绘制区域: {chart_width}x{chart_height}")

        # 加载用户配置
        user_profile = self._load_user_profile()

        # 检查数据类型（体重数据、体脂率数据还是营养摄入数据）
        if 'weight' in self.data_points[0]:
            print("检测到体重数据")
            self._draw_weight_chart(chart_container, time_container, margin_left, margin_right, margin_top, margin_bottom, 
                                  chart_width, chart_height, x, y, user_profile)
        elif 'body_fat' in self.data_points[0]:
            print("检测到体脂率数据")
            self._draw_body_fat_chart(chart_container, time_container, margin_left, margin_right, margin_top, margin_bottom, 
                                    chart_width, chart_height, x, y, user_profile)
        elif 'breakfast' in self.data_points[0]:
            print("检测到营养摄入数据")
            self._draw_nutrition_chart(chart_container, time_container, margin_left, margin_right, margin_top, margin_bottom, 
                                     chart_width, chart_height, x, y, user_profile)

    def _draw_weight_chart(self, chart_container, time_container, margin_left, margin_right, margin_top, margin_bottom, 
                          chart_width, chart_height, x, y, user_profile):
        """绘制体重变化图表"""
        print("绘制体重图表")
        # 提取数据
        weights = [point['weight'] for point in self.data_points]
        dates = [point['date'] for point in self.data_points]

        if not weights:
            return

        # 确定图表类型（根据数据点数量）
        chart_type = "week"  # 默认周视图
        if len(weights) <= 2:
            chart_type = "year"  # 年视图
        elif len(weights) <= 6:
            chart_type = "month"  # 月视图

        # 计算坐标范围，增加一些边距使数据不贴边
        min_weight = min(weights)
        max_weight = max(weights)
        weight_padding = (max_weight - min_weight) * 0.1 if max_weight != min_weight else 1
        min_weight -= weight_padding
        max_weight += weight_padding
        weight_range = max_weight - min_weight

        print(f"体重范围: {min_weight} - {max_weight}")

        # 绘制坐标轴
        with chart_container.canvas:
            Color(0.2, 0.2, 0.2, 1)  # 深灰色
            # X轴
            Line(points=[x + margin_left, y + margin_bottom, x + margin_left + chart_width, y + margin_bottom], width=1)
            # Y轴
            Line(points=[x + margin_left, y + margin_bottom, x + margin_left, y + margin_bottom + chart_height], width=1)

        # 获取应用程序实例以访问字体设置
        app = App.get_running_app()
        font_name = app.font_name if app and hasattr(app, 'font_name') else 'Roboto'

        # 不添加X轴标题（根据用户要求移除）
        
        y_label = Label(
            text="体重(kg)",
            pos=(x + margin_left + 15, y + margin_bottom + chart_height // 2 - 10),
            size=(30, 20),
            font_size='12sp',
            font_name=font_name,
            color=(0.3, 0.3, 0.3, 1)
        )
        chart_container.add_widget(y_label)

        # 绘制用户体重折线
        points = []
        num_points = len(weights)
        for i, weight in enumerate(weights):
            # 计算坐标
            px = x + margin_left + (i / (num_points - 1 if num_points > 1 else 1)) * chart_width
            py = y + margin_bottom + ((weight - min_weight) / weight_range) * chart_height
            points.extend([px, py])
            print(f"数据点 {i}: ({px}, {py}) - 日期: {dates[i]}, 体重: {weight}")

        with chart_container.canvas:
            Color(0.5, 0.9, 0.7, 1)  # 薄荷绿
            if len(points) >= 4:
                Line(points=points, width=2)
                
            # 绘制数据点
            for k in range(0, len(points), 2):
                px, py = points[k], points[k+1]
                Ellipse(pos=(px-3, py-3), size=(6, 6))

        # 添加数值标签，显示所有数据点，并靠近各自的数据点
        for i in range(num_points):
            # 获取坐标
            px = x + margin_left + (i / (num_points - 1 if num_points > 1 else 1)) * chart_width
            py = y + margin_bottom + ((weights[i] - min_weight) / weight_range) * chart_height
            
            # 添加数值标签（直接在数据点上方）
            value_label = Label(
                text=str(weights[i]),
                center_x=px + 25,  # 标签与节点强制竖向对齐，并整体右移5px
                center_y=py + 15,  # 将标签放在节点上方
                font_size='10sp',
                font_name=font_name,
                color=(0, 0, 0, 1),  # 黑色标签
                size_hint=(None, None),  # 禁用size_hint以使用固定大小
                size=(40, 20),
                halign='center',
                valign='middle'
            )
            chart_container.add_widget(value_label)
            
            # 添加X轴标签（底部对齐）并格式化
            formatted_date = self._format_date_label(dates[i], chart_type)
            date_label = Label(
                text=formatted_date,
                center_x=px + 25,  # 标签与节点强制竖向对齐，并整体右移25px
                y=y + margin_bottom - 50,  # 进一步增加上边距，调整标签位置
                font_size='10sp',
                font_name=font_name,
                color=(0.3, 0.3, 0.3, 1),
                size_hint=(None, None),  # 禁用size_hint以使用固定大小
                size=(40, 20),
                halign='center',
                valign='middle'
            )
            chart_container.add_widget(date_label)

    def _draw_body_fat_chart(self, chart_container, time_container, margin_left, margin_right, margin_top, margin_bottom, 
                            chart_width, chart_height, x, y, user_profile):
        """绘制体脂率变化图表"""
        print("绘制体脂率图表")
        # 提取数据
        body_fats = [point['body_fat'] for point in self.data_points]
        dates = [point['date'] for point in self.data_points]

        if not body_fats:
            return

        # 确定图表类型（根据数据点数量）
        chart_type = "week"  # 默认周视图
        if len(body_fats) <= 2:
            chart_type = "year"  # 年视图
        elif len(body_fats) <= 6:
            chart_type = "month"  # 月视图

        # 计算坐标范围，增加一些边距使数据不贴边
        min_body_fat = min(body_fats)
        max_body_fat = max(body_fats)
        body_fat_padding = (max_body_fat - min_body_fat) * 0.1 if max_body_fat != min_body_fat else 1
        min_body_fat -= body_fat_padding
        max_body_fat += body_fat_padding
        body_fat_range = max_body_fat - min_body_fat

        print(f"体脂率范围: {min_body_fat} - {max_body_fat}")

        # 绘制坐标轴
        with chart_container.canvas:
            Color(0.2, 0.2, 0.2, 1)  # 深灰色
            # X轴
            Line(points=[x + margin_left, y + margin_bottom, x + margin_left + chart_width, y + margin_bottom], width=1)
            # Y轴
            Line(points=[x + margin_left, y + margin_bottom, x + margin_left, y + margin_bottom + chart_height], width=1)

        # 获取应用程序实例以访问字体设置
        app = App.get_running_app()
        font_name = app.font_name if app and hasattr(app, 'font_name') else 'Roboto'

        # 不添加X轴标题（根据用户要求移除）
        
        y_label = Label(
            text="体脂率(%)",
            pos=(x + margin_left + 15, y + margin_bottom + chart_height // 2 - 10),
            size=(40, 20),
            font_size='12sp',
            font_name=font_name,
            color=(0.3, 0.3, 0.3, 1),
            halign='left'
        )
        chart_container.add_widget(y_label)

        # 绘制用户体脂率折线
        points = []
        num_points = len(body_fats)
        for i, body_fat in enumerate(body_fats):
            # 计算坐标
            px = x + margin_left + (i / (num_points - 1 if num_points > 1 else 1)) * chart_width
            py = y + margin_bottom + ((body_fat - min_body_fat) / body_fat_range) * chart_height
            points.extend([px, py])
            print(f"数据点 {i}: ({px}, {py}) - 日期: {dates[i]}, 体脂率: {body_fat}")

        with chart_container.canvas:
            Color(0.9, 0.5, 0.7, 1)  # 粉红色
            if len(points) >= 4:
                Line(points=points, width=2)
                
            # 绘制数据点
            for k in range(0, len(points), 2):
                px, py = points[k], points[k+1]
                Ellipse(pos=(px-3, py-3), size=(6, 6))

        # 添加数值标签，显示所有数据点，并靠近各自的数据点
        for i in range(num_points):
            # 获取坐标
            px = x + margin_left + (i / (num_points - 1 if num_points > 1 else 1)) * chart_width
            py = y + margin_bottom + ((body_fats[i] - min_body_fat) / body_fat_range) * chart_height
            
            # 添加数值标签（直接在数据点上方）
            value_label = Label(
                text=str(body_fats[i]),
                center_x=px + 25,  # 标签与节点强制竖向对齐，并整体右移25px
                center_y=py + 15,  # 将标签放在节点上方
                font_size='10sp',
                font_name=font_name,
                color=(0, 0, 0, 1),  # 黑色标签
                size_hint=(None, None),  # 禁用size_hint以使用固定大小
                size=(40, 20),
                halign='center',
                valign='middle'
            )
            chart_container.add_widget(value_label)
            
            # 添加X轴标签（底部对齐）并格式化
            formatted_date = self._format_date_label(dates[i], chart_type)
            date_label = Label(
                text=formatted_date,
                center_x=px + 25,  # 标签与节点强制竖向对齐，并整体右移25px
                y=y + margin_bottom - 50,  # 进一步增加上边距，调整标签位置
                font_size='10sp',
                font_name=font_name,
                color=(0.3, 0.3, 0.3, 1),
                size_hint=(None, None),  # 禁用size_hint以使用固定大小
                size=(40, 20),
                halign='center',
                valign='middle'
            )
            chart_container.add_widget(date_label)

    def _toggle_nutrition_view(self, view):
        """切换营养视图"""
        self.nutrition_view = view
        self.draw_chart()

    def _draw_nutrition_chart(self, chart_container, time_container, margin_left, margin_right, margin_top, margin_bottom, 
                             chart_width, chart_height, x, y, user_profile):
        """绘制营养摄入图表"""
        print("绘制营养摄入图表")
        # 提取数据
        breakfast_calories = [point['breakfast'] for point in self.data_points]
        lunch_calories = [point['lunch'] for point in self.data_points]
        dinner_calories = [point['dinner'] for point in self.data_points]
        dates = [point['date'] for point in self.data_points]

        if not breakfast_calories:
            return

        # 确定图表类型（根据数据点数量）
        chart_type = "week"  # 默认周视图
        if len(breakfast_calories) <= 2:
            chart_type = "year"  # 年视图
        elif len(breakfast_calories) <= 6:
            chart_type = "month"  # 月视图

        # 获取应用程序实例以访问字体设置
        app = App.get_running_app()
        font_name = app.font_name if app and hasattr(app, 'font_name') else 'Roboto'

        # 添加切换按钮（修改为单个按钮切换，只在早餐、午餐、晚餐之间切换）
        # 创建一个Button并直接添加到图表容器中，使用pos_hint进行定位
        toggle_button = Button(
            text="早餐" if self.nutrition_view == "breakfast" else "午餐" if self.nutrition_view == "lunch" else "晚餐",
            size_hint=(None, None),
            size=(60, 30),
            pos_hint={'right': 0.98, 'top': 0.98},  # 定位在右上角
            font_name=font_name,
            background_color=(0.2, 0.6, 1, 1)
        )
        
        # 绑定按钮点击事件，循环切换视图（只在早餐、午餐、晚餐之间切换）
        def on_toggle_button_press(instance):
            print(f"按钮被点击，当前视图: {self.nutrition_view}")  # 添加调试信息
            view_order = ["breakfast", "lunch", "dinner"]
            current_index = view_order.index(self.nutrition_view)
            next_index = (current_index + 1) % len(view_order)
            self._toggle_nutrition_view(view_order[next_index])
        
        toggle_button.bind(on_press=on_toggle_button_press)
        chart_container.add_widget(toggle_button)  # 将按钮直接添加到图表容器中
        
        # 绑定按钮点击事件，循环切换视图（只在早餐、午餐、晚餐之间切换）
        def on_toggle_button_press(instance):
            print(f"按钮被点击，当前视图: {self.nutrition_view}")  # 添加调试信息
            view_order = ["breakfast", "lunch", "dinner"]
            current_index = view_order.index(self.nutrition_view)
            next_index = (current_index + 1) % len(view_order)
            self._toggle_nutrition_view(view_order[next_index])
        


        # 计算坐标范围，增加一些边距使数据不贴边
        all_calories = breakfast_calories + lunch_calories + dinner_calories
        min_calories = min(all_calories)
        max_calories = max(all_calories)
        calories_padding = (max_calories - min_calories) * 0.1 if max_calories != min_calories else 1
        min_calories -= calories_padding
        max_calories += calories_padding
        calories_range = max_calories - min_calories

        print(f"卡路里范围: {min_calories} - {max_calories}")

        # 绘制坐标轴
        with chart_container.canvas:
            Color(0.2, 0.2, 0.2, 1)  # 深灰色
            # X轴
            Line(points=[x + margin_left, y + margin_bottom, x + margin_left + chart_width, y + margin_bottom], width=1)
            # Y轴
            Line(points=[x + margin_left, y + margin_bottom, x + margin_left, y + margin_bottom + chart_height], width=1)

        # 不添加X轴标题（根据用户要求移除）
        
        y_label = Label(
            text="卡路里(kcal)",
            pos=(x + margin_left + 15, y + margin_bottom + chart_height // 2 - 10),
            size=(50, 20),
            font_size='12sp',
            font_name=font_name,
            color=(0.3, 0.3, 0.3, 1),
            halign='left'
        )
        chart_container.add_widget(y_label)

        # 根据当前视图选择要绘制的数据（只显示单餐数据）
        lines_data = []
        if self.nutrition_view == "breakfast":
            lines_data = [(breakfast_calories, get_color_from_hex("#FF6B6B"), "早餐")]
        elif self.nutrition_view == "lunch":
            lines_data = [(lunch_calories, get_color_from_hex("#4ECDC4"), "午餐")]
        elif self.nutrition_view == "dinner":
            lines_data = [(dinner_calories, get_color_from_hex("#7EDAB8"), "晚餐")]

        # 存储所有线条的点用于后续标签绘制
        all_lines_points = []
        num_points = len(breakfast_calories)

        for i, (calories_data, color, label_prefix) in enumerate(lines_data):
            points = []
            for j, calories in enumerate(calories_data):
                # 计算坐标
                px = x + margin_left + (j / (num_points - 1 if num_points > 1 else 1)) * chart_width
                py = y + margin_bottom + ((calories - min_calories) / calories_range) * chart_height
                points.extend([px, py])
                print(f"数据点 {j}: ({px}, {py}) - 日期: {dates[j]}, 卡路里: {calories}")

            with chart_container.canvas:
                Color(*color)
                if len(points) >= 4:
                    Line(points=points, width=2)
                    
                # 绘制数据点
                for k in range(0, len(points), 2):
                    px, py = points[k], points[k+1]
                    Ellipse(pos=(px-3, py-3), size=(6, 6))
            
            all_lines_points.append((points, color, calories_data, label_prefix))

        # 添加数值标签，显示所有数据点，并靠近各自的数据点
        for i in range(num_points):
            # 为每条线添加数值标签
            for points, color, calories_data, label_prefix in all_lines_points:
                if i < len(calories_data):
                    px = points[i*2]
                    py = points[i*2+1]
                    
                    # 添加数值标签（直接在数据点上方）
                    value_label = Label(
                        text=str(calories_data[i]),
                        center_x=px + 25,  # 标签与节点强制竖向对齐，并整体右移25px
                        center_y=py + 15,  # 将标签放在节点上方
                        font_size='9sp',
                        font_name=font_name,
                        color=(0, 0, 0, 1),  # 黑色标签
                        size_hint=(None, None),  # 禁用size_hint以使用固定大小
                        size=(40, 20),
                        halign='center',
                        valign='middle'
                    )
                    chart_container.add_widget(value_label)
            
            # 添加X轴标签，底部对齐并格式化
            formatted_date = self._format_date_label(dates[i], chart_type)
            px = x + margin_left + (i / (num_points - 1 if num_points > 1 else 1)) * chart_width
            
            date_label = Label(
                text=formatted_date,
                center_x=px + 25,  # 标签与节点强制竖向对齐，并整体右移25px
                y=y + margin_bottom - 50,  # 进一步增加上边距，调整标签位置
                font_size='10sp',
                font_name=font_name,
                color=(0.3, 0.3, 0.3, 1),
                size_hint=(None, None),  # 禁用size_hint以使用固定大小
                size=(40, 20),
                halign='center',
                valign='middle'
            )
            chart_container.add_widget(date_label)

def load_user_profile():
    """加载用户档案数据"""
    try:
        # 使用统一数据管理器加载用户档案
        data_manager = DataManager()
        return data_manager.get_profile()
    except FileNotFoundError:
        print("未找到用户档案文件")
        return None
    except json.JSONDecodeError:
        print("用户档案文件格式错误")
        return None
    except Exception as e:
        print(f"加载用户档案时出错: {e}")
        return None