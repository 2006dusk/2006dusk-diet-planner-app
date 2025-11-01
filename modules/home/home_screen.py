# -*- coding: utf-8 -*-
from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.graphics import Color, RoundedRectangle
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.lang import Builder
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy.app import App
import json
from pathlib import Path

# ---------- 1. 全局常量  苹果 2025 清新色 ----------
# 从主应用导入颜色常量
from main import IOS_BG, IOS_CARD, IOS_MINT, IOS_TEXT_MAIN, IOS_TEXT_SEC

# 导入rgba函数供KV文件使用
from kivy.utils import get_color_from_hex as rgba
from kivy.app import App

# 导入统一数据管理器
from utils.data_manager import DataManager

# 数据文件路径
DATA_DIR = Path(__file__).parent.parent / "data"
USER_DATA_DIR = DATA_DIR / "user_data"

USER_PLAN_FILE = USER_DATA_DIR / "user_plan.json"
WEEKLY_DATA_FILE = USER_DATA_DIR / "weekly_data.json"
DAILY_INTAKE_FILE = USER_DATA_DIR / "daily_intake.json"

def get_dynamic_module_data():
    """根据实际数据动态生成模块数据"""
    modules = [
        {"icon": "🍽️", "title": "计划饮食", "sub": "今日目标已设", "val": "1 400 kcal"},
        {"icon": "📋", "title": "今日规划", "sub": "查看三餐计划", "val": "已设定"},
        {"icon": "⚖️", "title": "体重规划", "sub": "本周目标", "val": "-0.3 kg"},
        {"icon": "📚", "title": "食谱查看", "sub": "查看所有食物", "val": "3 道"},
        {"icon": "📊", "title": "健康报告", "sub": "记录天数", "val": "0 天"},
        {"icon": "👤", "title": "个人中心", "sub": "个人信息设置", "val": "待完善"},
    ]
    
    # 初始化数据管理器
    data_manager = DataManager()
    
    # 动态更新计划饮食的val值
    current_plan = data_manager.get_current_plan()
    if current_plan and "recommended_calories" in current_plan:
        calories = current_plan["recommended_calories"]
        modules[0]["val"] = f"{int(calories)} kcal"
    
    # 动态更新今日规划的val值
    if current_plan and "plan" in current_plan and current_plan["plan"]:
        modules[1]["val"] = "已设定"
    else:
        modules[1]["val"] = "未设定"
    
    # 动态更新体重规划的val值
    profile_data = data_manager.get_profile()
    weight_history = profile_data.get("weight_history", [])
    if len(weight_history) >= 2:
        current_weight = weight_history[-1]["weight"]
        previous_weight = weight_history[-2]["weight"]
        weight_diff = current_weight - previous_weight
        modules[2]["val"] = f"{weight_diff:+.1f} kg"
    
    # 动态更新食谱查看的val值
    user_recipes = data_manager.get_user_recipes()
    modules[3]["val"] = f"{len(user_recipes)} 道"
    
    # 动态更新健康报告的val值 - 显示实际数据天数
    daily_intake = data_manager.get_daily_intake()
    modules[4]["val"] = f"{len(daily_intake)} 天"
    
    # 动态更新个人中心的val值
    user_info = data_manager.get_profile()
    required_fields = ["age", "height", "current_weight", "target_weight", "gender"]
    if all(user_info.get(k) is not None for k in required_fields):
        modules[5]["val"] = "已完成"
    else:
        modules[5]["val"] = "待完善"
    
    return modules

# ---------- 2. 6 个模块数据 ----------
# MODULES = get_dynamic_module_data()

# ---------- 3. 小方块组件 ----------
class Tile(BoxLayout):
    def __init__(self, data, **kw):
        super().__init__(**kw)
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        # 使用放大后的尺寸: 180dp宽度、180dp高度
        self.width = dp(180)
        self.height = dp(180)
        self.data = data
        # 设置左右边距都是8px，保持水平方向对称间距
        self.padding = [dp(8), dp(8), dp(8), dp(8)]
        self.spacing = dp(3)
        self.radius = dp(12)
        self.draw_bg()
        # 延迟添加内容以确保正确渲染
        Clock.schedule_once(lambda dt: self.add_content(), 0)

    def draw_bg(self):
        # 清除之前的背景
        self.canvas.before.clear()
        with self.canvas.before:
            Color(rgba=(1, 1, 1, 0.95))  # 使用正确的RGBA格式，白色卡片背景
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *a):
        # 更新背景的位置和大小
        if hasattr(self, 'bg'):
            self.bg.pos = self.pos
            self.bg.size = self.size

    def add_content(self):
        # 创建主内容容器，用于统一管理间距
        content_container = BoxLayout(orientation='vertical')
        
        # 顶部布局：标题左上角对齐（带顶部边距）
        top_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35))
        
        # 标题左上角对齐，增大字号
        title = Label(text=self.data["title"], color=IOS_TEXT_MAIN, font_size=sp(16), bold=True,
                      halign='left', valign='top',
                      font_name='ChineseFont' if getattr(App.get_running_app(), 'font_available', False) else 'Roboto')
        title.bind(size=self._update_text_size)
        top_layout.add_widget(title)
        
        # 添加弹性空间将标题推向左侧
        top_layout.add_widget(Widget())
        
        content_container.add_widget(top_layout)
        
        # 中间内容区域（图标）
        middle_layout = BoxLayout(orientation='vertical', spacing=dp(2), size_hint_y=None, height=dp(24))
        
        # 图标居中，使用图标文字sp(20)
        icon = Label(text=self.data["icon"], font_size=sp(20), size_hint_y=None, height=dp(24),
                     halign='center', valign='middle')
        middle_layout.add_widget(icon)
        
        content_container.add_widget(middle_layout)

        # 底部布局：将副标题和数值放在一行，居中显示在控件中心偏下位置
        bottom_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30),
                                  spacing=dp(2))
        
        # 创建一个水平布局容器来容纳sub和val，并整体居中
        text_container = BoxLayout(orientation='horizontal', size_hint_x=None)
        text_container.bind(minimum_width=text_container.setter('width'))
        
        # 副标题右对齐，使用副标题文字sp(9)
        sub = Label(text=self.data["sub"], color=IOS_TEXT_SEC, font_size=sp(9),
                    halign='right', valign='middle',
                    font_name='ChineseFont' if getattr(App.get_running_app(), 'font_available', False) else 'Roboto',
                    size_hint_x=None)
        sub.bind(size=self._update_text_size)
        text_container.add_widget(sub)
        
        # 数值左对齐，使用数值文字sp(11)
        val = Label(text=self.data["val"], color=IOS_MINT, font_size=sp(11), bold=True,
                    halign='left', valign='middle',
                    font_name='ChineseFont' if getattr(App.get_running_app(), 'font_available', False) else 'Roboto',
                    size_hint_x=None)
        val.bind(size=self._update_text_size)
        text_container.add_widget(val)
        
        # 将文本容器添加到底部布局并居中
        bottom_layout.add_widget(Widget())  # 左侧弹簧
        bottom_layout.add_widget(text_container)  # 文本容器
        bottom_layout.add_widget(Widget())  # 右侧弹簧
        
        content_container.add_widget(bottom_layout)
        
        # 将内容容器添加到主控件
        self.add_widget(content_container)

    def _update_text_size(self, instance, size):
        """更新文本大小以确保对齐正确，防止异常换行"""
        instance.text_size = (instance.width, None) if instance.width > 0 else instance.size

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # 应用缩放动画
            Animation.cancel_all(self)
            # 停止所有子元素的动画
            for child in self.walk():
                if hasattr(child, 'animation'):
                    Animation.stop_all(child)
                elif isinstance(child, Label):
                    Animation.stop_all(child)
            
            # 创建控件和文字同步的缩放动画，确保视觉效果统一流畅
            Animation(size=(self.width*0.95, self.height*0.95),
                      pos=(self.x + self.width*0.025, self.y + self.height*0.025),
                      duration=0.08).start(self)
            from kivy.clock import Clock
            Clock.schedule_once(self.restore, 0.08)
            # 切换到对应的功能界面
            self.switch_to_screen()
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            # 恢复原始尺寸和位置
            Animation.cancel_all(self)
            Animation(size=(self.width, self.height),
                      pos=(self.x, self.y),
                      duration=0.08).start(self)
            return True
        return super().on_touch_up(touch)

    def switch_to_screen(self):
        """根据模块标题切换到对应的屏幕，使用右滑进入效果"""
        screen_map = {
            "计划饮食": "plan",
            "今日规划": "water",
            "体重规划": "weight",
            "食谱查看": "recipes",
            "健康报告": "report",
            "个人中心": "profile"  # 更改为使用profile而不是body_data
        }
        
        screen_name = screen_map.get(self.data["title"])
        if screen_name:
            app = App.get_running_app()
            # 使用左滑进入新页面
            if hasattr(app, 'navigate_to_screen'):
                app.navigate_to_screen(screen_name, direction='left')

    def restore(self, _):
        # 恢复到原始尺寸和位置
        Animation.cancel_all(self)
        Animation(size=(dp(180), dp(180)),
                  pos=(self.x, self.y),
                  duration=0.08).start(self)

# ---------- 4. 首页网格 ----------
class HomeGrid(GridLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.cols = 2
        self.spacing = [dp(8), dp(8)]
        # 设置左右边距都是8px
        self.padding = [dp(8), dp(16), dp(8), dp(16)]
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        # 重新获取动态数据
        dynamic_modules = get_dynamic_module_data()
        for m in dynamic_modules:
            self.add_widget(Tile(m))

# ---------- 5. 响应式组件 ----------
from kivy.metrics import dp, sp
from kivy.app import App

# 1. 根据屏宽决定列数与 Tile 尺寸
def responsive_cols():
    # 修改为始终返回2列，符合用户要求在普通情况下也是两行
    return 2

def tile_size():
    # 使用放大后的尺寸: 180dp宽度、180dp高度
    return dp(180), dp(180)

# 2. 响应式 Tile
class ResponsiveTile(Tile):
    def __init__(self, data, **kw):
        # 每次创建时都重新获取动态数据
        dynamic_data = get_dynamic_module_data()
        # 查找匹配的数据
        matched_data = None
        for d in dynamic_data:
            if d["title"] == data["title"]:
                matched_data = d
                break
        if matched_data:
            data = matched_data
            
        super().__init__(data, **kw)
        # 重新绑定尺寸
        self.size_hint = (None, None)
        self.width, self.height = tile_size()
        # 字号随屏宽线性缩放（基准 360 dp 下为原字号）
        scale = Window.width / dp(360)
        for label in self.walk(restrict=True):
            if isinstance(label, Label):
                # 增大字号缩放比例
                label.font_size = sp(label.font_size * scale * 1.2)

# 3. 响应式 HomeGrid
class ResponsiveHomeGrid(GridLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.cols = 2
        self.spacing = [dp(8), dp(8)]
        # 设置左右边距都是8px
        self.padding = [dp(8), dp(16), dp(8), dp(16)]
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        self.bind(size=self._update_padding)  # 绑定size变化事件
        self.rebuild()

        # 横竖屏切换时重新布局
        Window.bind(size=self.on_win_size)

    def _update_padding(self, *args):
        # 计算使网格居中的左右padding，保持左右边距都是8px
        if self.width <= 0:  # 确保宽度已经正确初始化
            return
        total_tile_width = dp(180) * 2 + dp(8)  # 两个tile宽度 + 间距
        padding = (self.width - total_tile_width) / 2
        # 确保最小边距为8px
        self.padding = [max(dp(8), padding), dp(16), max(dp(8), padding), dp(16)]

    def on_win_size(self, *a):
        self.clear_widgets()
        self.rebuild()

    def rebuild(self):
        self.cols = responsive_cols()
        # 更新padding以保持居中
        Clock.schedule_once(self._update_padding, 0)  # 延迟执行确保布局正确
        # 每次重建时都重新获取动态数据
        dynamic_modules = get_dynamic_module_data()
        for m in dynamic_modules:
            self.add_widget(ResponsiveTile(m))

# ---------- 6. 首页屏幕 KV 语言 ----------
home_screen_kv = '''
<HomeScreen>:
    name: 'home'
    BoxLayout:
        orientation: 'vertical'

        # Header
        BoxLayout:
            size_hint_y: None
            height: '108dp'
            padding: '24dp', '48dp', '24dp', '12dp'
            Label:
                text: "健康助手"
                font_name: 'ChineseFont' if app.font_available else 'Roboto'
                font_size: '32sp'
                color: rgba('#000000')
                bold: False

        # Scroll 内容
        ScrollView:
            do_scroll_x: False
            GridLayout:
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                ResponsiveHomeGrid:
                    id: home_grid
'''

Builder.load_string(home_screen_kv)

# ---------- 7. 首页屏幕 ----------
class HomeScreen(Screen):
    pass