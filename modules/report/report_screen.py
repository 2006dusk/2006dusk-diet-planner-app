# -*- coding: utf-8 -*-
"""
健康报告模块
负责显示用户的健康数据报告和图表
"""

import json
import os
from datetime import datetime, timedelta
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App

# 导入统一数据管理器
from utils.data_manager import DataManager

# 在这里定义ReportScreen的KV语言
report_screen_kv = '''
#:import FlatButton components.custom_widgets.FlatButton
#:import Card components.custom_widgets.Card
#:import LineChart components.charts.LineChart

<ReportScreen>:
    name: 'report'
    BoxLayout:
        orientation: 'vertical'

        # Header
        BoxLayout:
            size_hint_y: None
            height: '108dp'
            padding: '24dp', '48dp', '24dp', '12dp'
            Label:
                text: "健康报告"
                font_name: 'ChineseFont' if app.font_available else 'Roboto'
                font_size: '32sp'
                color: rgba('#000000')
                bold: False

        # 返回按钮和时间范围切换按钮区域
        BoxLayout:
            size_hint_y: None
            height: '60dp'
            padding: '12dp'
            spacing: '10dp'
            
            FlatButton:
                text: "← 返回"
                size_hint_x: None
                width: '100dp'
                on_press: root.navigate_back()
            
            Widget:
                size_hint_x: 1
            
            FlatButton:
                id: range_button
                text: "周"
                size_hint_x: None
                width: '100dp'
                on_press: root.toggle_time_range()

        # 图表区域 - 添加了更大的顶部边距
        ScrollView:
            bar_width: 0
            scroll_type: ['bars', 'content']
            effect_cls: 'ScrollEffect'
            
            BoxLayout:
                orientation: 'vertical'
                padding: '24dp', '50dp'  # 大幅增加顶部内边距
                spacing: '30dp'  # 增加容器间间距
                size_hint_y: None
                height: self.minimum_height
                
                # 体重变化图表
                Card:
                    size_hint_y: None
                    height: '250dp'
                    padding: ['24dp', '35dp', '24dp', '20dp']  # 增加标题上边距
                    spacing: '20dp'  # 增加容器内元素间距
                    Label:
                        text: "体重变化"
                        font_name: 'ChineseFont' if app.font_available else 'Roboto'
                        font_size: '16sp'
                        color: rgba('#000000')
                        size_hint_y: None
                        height: '40dp'
                        padding: ['0dp', '20dp', '0dp', '0dp']  # 标题上边距
                    LineChart:
                        id: weight_chart
                        size_hint_y: None
                        height: '190dp'
                
                # 体脂率变化图表
                Card:
                    size_hint_y: None
                    height: '250dp'
                    padding: ['24dp', '35dp', '24dp', '20dp']  # 增加标题上边距
                    spacing: '20dp'  # 增加容器内元素间距
                    Label:
                        text: "体脂率变化"
                        font_name: 'ChineseFont' if app.font_available else 'Roboto'
                        font_size: '16sp'
                        color: rgba('#000000')
                        size_hint_y: None
                        height: '40dp'
                        padding: ['0dp', '20dp', '0dp', '0dp']  # 标题上边距
                    LineChart:
                        id: body_fat_chart
                        size_hint_y: None
                        height: '190dp'
                
                # 三餐营养摄入
                Card:
                    size_hint_y: None
                    height: '250dp'
                    padding: ['24dp', '35dp', '24dp', '20dp']  # 增加标题上边距
                    spacing: '20dp'  # 增加容器内元素间距
                    Label:
                        text: "三餐营养摄入"
                        font_name: 'ChineseFont' if app.font_available else 'Roboto'
                        font_size: '16sp'
                        color: rgba('#000000')
                        size_hint_y: None
                        height: '40dp'
                        padding: ['0dp', '20dp', '0dp', '0dp']  # 标题上边距
                    LineChart:
                        id: nutrition_chart
                        size_hint_y: None
                        height: '190dp'
'''

Builder.load_string(report_screen_kv)

class ReportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.daily_intake_data = []
        self.weekly_data = []
        self.time_range = "week"  # 默认显示周数据
        self.data_manager = DataManager()  # 初始化数据管理器
        self.user_profile = {}
        
    def on_pre_enter(self, *args):
        """在进入屏幕前加载数据"""
        self.load_data()
        self.update_charts()
    
    def load_data(self):
        """加载数据"""
        # 使用数据管理器加载数据
        self.daily_intake_data = self.data_manager.get_daily_intake()
        self.weekly_data = self.data_manager.get_weekly_data()
        self.user_profile = self.data_manager.get_profile()
        
        # 如果没有数据，尝试从独立文件加载（向后兼容）
        if not self.daily_intake_data:
            self.load_daily_intake_data()
        
        if not self.weekly_data:
            self.load_weekly_data()
            
        # 不再生成示例数据
        pass
    
    def load_daily_intake_data(self):
        """加载每日摄入数据"""
        try:
            data_file_path = os.path.join(os.getcwd(), "data", "user_data", "daily_intake.json")
            if os.path.exists(data_file_path):
                with open(data_file_path, 'r', encoding='utf-8') as f:
                    self.daily_intake_data = json.load(f)
            else:
                self.daily_intake_data = []
        except Exception as e:
            print(f"加载每日摄入数据时出错: {e}")
            self.daily_intake_data = []

    def load_weekly_data(self):
        """加载每周数据"""
        try:
            data_file_path = os.path.join(os.getcwd(), "data", "user_data", "weekly_data.json")
            if os.path.exists(data_file_path):
                with open(data_file_path, 'r', encoding='utf-8') as f:
                    self.weekly_data = json.load(f)
            else:
                self.weekly_data = []
        except Exception as e:
            print(f"加载每周数据时出错: {e}")
            self.weekly_data = []

    def generate_sample_data(self):
        """生成示例数据用于演示（已禁用）"""
        # 已禁用示例数据生成
        pass

    def navigate_back(self):
        """返回主页，使用右滑动效"""
        app = App.get_running_app()
        if hasattr(app, 'navigate_to_screen'):
            app.navigate_to_screen('home', direction='right')

    def toggle_time_range(self):
        """切换时间范围"""
        # 循环切换时间范围: 周 -> 月 -> 年 -> 周
        if self.time_range == 'week':
            self.time_range = 'month'
            self.ids.range_button.text = "月"
        elif self.time_range == 'month':
            self.time_range = 'year'
            self.ids.range_button.text = "年"
        else:  # year
            self.time_range = 'week'
            self.ids.range_button.text = "周"
            
        # 更新图表数据
        self.update_charts()

    def update_charts(self):
        """更新所有图表"""
        # 准备图表数据
        chart_data = self.prepare_chart_data()
        
        # 更新体重变化图表
        self.ids.weight_chart.data_points = chart_data['weight_data_points']
        self.ids.weight_chart.draw_chart()
        
        # 更新体脂率变化图表
        self.ids.body_fat_chart.data_points = chart_data['body_fat_data_points']
        self.ids.body_fat_chart.draw_chart()
        
        # 更新营养摄入图表
        self.ids.nutrition_chart.data_points = chart_data['nutrition_data']
        self.ids.nutrition_chart.draw_chart()

    def prepare_chart_data(self):
        """准备图表数据"""
        # 体重变化数据
        weight_data_points = []
        # 体脂率变化数据
        body_fat_data_points = []
        # 营养摄入数据
        nutrition_data = []
        
        if self.time_range == "week":
            # 周视图：显示实际存在的数据天数，而不是虚假渲染
            if self.daily_intake_data:
                # 获取最近的数据，最多显示7天
                recent_data = self.daily_intake_data[-7:] if len(self.daily_intake_data) >= 7 else self.daily_intake_data
                
                # 处理实际存在的数据天数
                for record in recent_data:
                    date = record["date"]
                    weight_data_points.append({
                        "date": date,
                        "weight": record["weight"]
                    })
                    body_fat_data_points.append({
                        "date": date,
                        "body_fat": record["body_fat_percentage"]
                    })
                    
                    breakfast_calories = record["meals"]["breakfast"]["calories"]
                    lunch_calories = record["meals"]["lunch"]["calories"]
                    dinner_calories = record["meals"]["dinner"]["calories"]
                    
                    nutrition_data.append({
                        "date": date,
                        "breakfast": breakfast_calories,
                        "lunch": lunch_calories,
                        "dinner": dinner_calories
                    })
            else:
                # 如果没有daily_intake_data，则从当前计划中获取数据
                current_plan = self.data_manager.get_current_plan()
                if current_plan:
                    # 使用今天的日期
                    today = datetime.now().strftime("%Y-%m-%d")
                    # 从当前计划中提取各餐热量
                    breakfast_calories = 0
                    lunch_calories = 0
                    dinner_calories = 0
                    
                    for meal in current_plan.get("plan", []):
                        meal_type = meal.get("meal_type")
                        calories = meal.get("calories", 0)
                        
                        if meal_type == "breakfast":
                            breakfast_calories = calories
                        elif meal_type == "lunch":
                            lunch_calories = calories
                        elif meal_type == "dinner":
                            dinner_calories = calories
                    
                    # 添加单天数据点
                    nutrition_data.append({
                        "date": today,
                        "breakfast": breakfast_calories,
                        "lunch": lunch_calories,
                        "dinner": dinner_calories
                    })
                
                # 为体重和体脂添加默认数据点（使用用户档案中的数据）
                profile = self.data_manager.get_profile()
                if profile:
                    today = datetime.now().strftime("%Y-%m-%d")
                    current_weight = profile.get("current_weight", 70)
                    weight_data_points.append({
                        "date": today,
                        "weight": current_weight
                    })
                    
                    # 体脂率需要估算（这里使用一个简单的估算）
                    # 通常体脂率与BMI有一定关系，这里使用一个简化公式
                    height = profile.get("height", 170) / 100  # 转换为米
                    if height > 0:
                        bmi = current_weight / (height * height)
                        # 简化的体脂率估算（仅用于演示）
                        # 男性体脂率估算公式：体脂率 = (1.2 * BMI) + (0.23 * 年龄) - 16.2
                        # 女性体脂率估算公式：体脂率 = (1.2 * BMI) + (0.23 * 年龄) - 5.4
                        gender = profile.get("gender", "男")
                        age = profile.get("age", 25)
                        if gender == "男":
                            estimated_body_fat = max(3, min(30, (1.2 * bmi) + (0.23 * age) - 16.2))
                        else:
                            estimated_body_fat = max(3, min(30, (1.2 * bmi) + (0.23 * age) - 5.4))
                    else:
                        # 如果身高数据无效，使用默认估算
                        estimated_body_fat = 15.0
                    
                    body_fat_data_points.append({
                        "date": today,
                        "body_fat": round(estimated_body_fat, 1)
                    })
                
                # 移除了只有一天数据时不生成图表数据的限制
                        
        elif self.time_range == "month":
            # 月视图：显示实际存在的数据天数，而不是虚假渲染
            if self.daily_intake_data:
                # 取最近30天的数据
                recent_daily_data = self.daily_intake_data[-30:] if len(self.daily_intake_data) >= 30 else self.daily_intake_data
                
                # 如果数据少于5天，则直接显示每一天的数据
                if len(recent_daily_data) < 5:
                    for record in recent_daily_data:
                        date = record["date"]
                        weight_data_points.append({
                            "date": date,
                            "weight": record["weight"]
                        })
                        body_fat_data_points.append({
                            "date": date,
                            "body_fat": record["body_fat_percentage"]
                        })
                        
                        breakfast_calories = record["meals"]["breakfast"]["calories"]
                        lunch_calories = record["meals"]["lunch"]["calories"]
                        dinner_calories = record["meals"]["dinner"]["calories"]
                        
                        nutrition_data.append({
                            "date": date,
                            "breakfast": breakfast_calories,
                            "lunch": lunch_calories,
                            "dinner": dinner_calories
                        })
                else:
                    # 每5天分为一组，显示实际组数
                    num_groups = min(6, len(recent_daily_data) // 5 + (1 if len(recent_daily_data) % 5 > 0 else 0))
                    for i in range(num_groups):
                        # 计算每组的起始和结束索引
                        start_idx = i * 5
                        end_idx = min((i + 1) * 5, len(recent_daily_data))
                        
                        # 获取这5天的数据
                        group_data = recent_daily_data[start_idx:end_idx]
                        
                        # 计算平均值
                        total_weight = sum(record["weight"] for record in group_data)
                        total_body_fat = sum(record["body_fat_percentage"] for record in group_data)
                        total_breakfast = sum(record["meals"]["breakfast"]["calories"] for record in group_data)
                        total_lunch = sum(record["meals"]["lunch"]["calories"] for record in group_data)
                        total_dinner = sum(record["meals"]["dinner"]["calories"] for record in group_data)
                        
                        avg_weight = total_weight / len(group_data)
                        avg_body_fat = total_body_fat / len(group_data)
                        avg_breakfast = total_breakfast / len(group_data)
                        avg_lunch = total_lunch / len(group_data)
                        avg_dinner = total_dinner / len(group_data)
                        
                        # 使用组的最后一天作为日期标签
                        date = group_data[-1]["date"]
                        
                        weight_data_points.append({
                            "date": date,
                            "weight": round(avg_weight, 2)
                        })
                        body_fat_data_points.append({
                            "date": date,
                            "body_fat": round(avg_body_fat, 2)
                        })
                        nutrition_data.append({
                            "date": date,
                            "breakfast": round(avg_breakfast, 2),
                            "lunch": round(avg_lunch, 2),
                            "dinner": round(avg_dinner, 2)
                        })
            else:
                # 如果没有daily_intake_data，则从当前计划中获取数据
                current_plan = self.data_manager.get_current_plan()
                if current_plan:
                    # 使用今天的日期
                    today = datetime.now().strftime("%Y-%m-%d")
                    # 从当前计划中提取各餐热量
                    breakfast_calories = 0
                    lunch_calories = 0
                    dinner_calories = 0
                    
                    for meal in current_plan.get("plan", []):
                        meal_type = meal.get("meal_type")
                        calories = meal.get("calories", 0)
                        
                        if meal_type == "breakfast":
                            breakfast_calories = calories
                        elif meal_type == "lunch":
                            lunch_calories = calories
                        elif meal_type == "dinner":
                            dinner_calories = calories
                    
                    # 添加单天数据点
                    nutrition_data.append({
                        "date": today,
                        "breakfast": breakfast_calories,
                        "lunch": lunch_calories,
                        "dinner": dinner_calories
                    })
                
                # 为体重和体脂添加默认数据点（使用用户档案中的数据）
                profile = self.data_manager.get_profile()
                if profile:
                    today = datetime.now().strftime("%Y-%m-%d")
                    current_weight = profile.get("current_weight", 70)
                    weight_data_points.append({
                        "date": today,
                        "weight": current_weight
                    })
                    
                    # 体脂率需要估算（这里使用一个简单的估算）
                    # 通常体脂率与BMI有一定关系，这里使用一个简化公式
                    height = profile.get("height", 170) / 100  # 转换为米
                    if height > 0:
                        bmi = current_weight / (height * height)
                        # 简化的体脂率估算（仅用于演示）
                        # 男性体脂率估算公式：体脂率 = (1.2 * BMI) + (0.23 * 年龄) - 16.2
                        # 女性体脂率估算公式：体脂率 = (1.2 * BMI) + (0.23 * 年龄) - 5.4
                        gender = profile.get("gender", "男")
                        age = profile.get("age", 25)
                        if gender == "男":
                            estimated_body_fat = max(3, min(30, (1.2 * bmi) + (0.23 * age) - 16.2))
                        else:
                            estimated_body_fat = max(3, min(30, (1.2 * bmi) + (0.23 * age) - 5.4))
                    else:
                        # 如果身高数据无效，使用默认估算
                        estimated_body_fat = 15.0
                    
                    body_fat_data_points.append({
                        "date": today,
                        "body_fat": round(estimated_body_fat, 1)
                    })
        elif self.time_range == "year":
            # 年视图：显示实际存在的月份数据，而不是虚假渲染
            if self.daily_intake_data:
                # 按月份分组数据
                monthly_data = {}
                for record in self.daily_intake_data:
                    # 解析日期并提取年月
                    date_obj = datetime.strptime(record["date"], "%Y-%m-%d")
                    year_month = date_obj.strftime("%Y-%m")
                    
                    if year_month not in monthly_data:
                        monthly_data[year_month] = []
                    monthly_data[year_month].append(record)
                
                # 取实际存在的月份，最多显示12个月
                sorted_months = sorted(monthly_data.keys())[-12:]
                for year_month in sorted_months:
                    records = monthly_data[year_month]
                    if records:
                        # 取该月最后一条记录
                        last_record = records[-1]
                        date_obj = datetime.strptime(last_record["date"], "%Y-%m-%d")
                        # 显示为"1月"、"2月"等格式
                        date = f"{date_obj.month}月"
                        weight_data_points.append({
                            "date": date,
                            "weight": last_record["weight"]
                        })
                        body_fat_data_points.append({
                            "date": date,
                            "body_fat": last_record["body_fat_percentage"]
                        })
                        
                        # 对于年视图，营养摄入数据使用默认值（因为年度视图不显示详细营养摄入）
                        nutrition_data.append({
                            "date": date,
                            "breakfast": 500,  # 默认值
                            "lunch": 700,      # 默认值
                            "dinner": 600      # 默认值
                        })
            else:
                # 如果没有daily_intake_data，则从当前计划中获取数据
                current_plan = self.data_manager.get_current_plan()
                if current_plan:
                    # 使用今天的日期
                    today = datetime.now().strftime("%Y-%m-%d")
                    # 从当前计划中提取各餐热量
                    breakfast_calories = 0
                    lunch_calories = 0
                    dinner_calories = 0
                    
                    for meal in current_plan.get("plan", []):
                        meal_type = meal.get("meal_type")
                        calories = meal.get("calories", 0)
                        
                        if meal_type == "breakfast":
                            breakfast_calories = calories
                        elif meal_type == "lunch":
                            lunch_calories = calories
                        elif meal_type == "dinner":
                            dinner_calories = calories
                    
                    # 添加单天数据点
                    nutrition_data.append({
                        "date": today,
                        "breakfast": breakfast_calories,
                        "lunch": lunch_calories,
                        "dinner": dinner_calories
                    })
                
                # 为体重和体脂添加默认数据点（使用用户档案中的数据）
                profile = self.data_manager.get_profile()
                if profile:
                    today = datetime.now().strftime("%Y-%m-%d")
                    current_weight = profile.get("current_weight", 70)
                    weight_data_points.append({
                        "date": today,
                        "weight": current_weight
                    })
                    
                    # 体脂率需要估算（这里使用一个简单的估算）
                    # 通常体脂率与BMI有一定关系，这里使用一个简化公式
                    height = profile.get("height", 170) / 100  # 转换为米
                    if height > 0:
                        bmi = current_weight / (height * height)
                        # 简化的体脂率估算（仅用于演示）
                        # 男性体脂率估算公式：体脂率 = (1.2 * BMI) + (0.23 * 年龄) - 16.2
                        # 女性体脂率估算公式：体脂率 = (1.2 * BMI) + (0.23 * 年龄) - 5.4
                        gender = profile.get("gender", "男")
                        age = profile.get("age", 25)
                        if gender == "男":
                            estimated_body_fat = max(3, min(30, (1.2 * bmi) + (0.23 * age) - 16.2))
                        else:
                            estimated_body_fat = max(3, min(30, (1.2 * bmi) + (0.23 * age) - 5.4))
                    else:
                        # 如果身高数据无效，使用默认估算
                        estimated_body_fat = 15.0
                    
                    body_fat_data_points.append({
                        "date": today,
                        "body_fat": round(estimated_body_fat, 1)
                    })
                    
                    # 对于年视图，营养摄入数据使用默认值（因为年度视图不显示详细营养摄入）
                    nutrition_data.append({
                        "date": f"{datetime.now().month}月",
                        "breakfast": 500,  # 默认值
                        "lunch": 700,      # 默认值
                        "dinner": 600      # 默认值
                    })

        return {
            "weight_data_points": weight_data_points,
            "body_fat_data_points": body_fat_data_points,
            "nutrition_data": nutrition_data
        }