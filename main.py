# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.core.window import Window
from kivy.utils import platform, get_color_from_hex
from kivy.core.text import LabelBase
from kivy.uix.boxlayout import BoxLayout
import os
from pathlib import Path

# 注册中文字体 - 优先使用系统中文字体
font_path = None

# 仅在非Android平台上检查Windows系统中的常见中文字体路径
if platform != 'android':
    # 检查Windows系统中的常见中文字体路径
    possible_paths = [
        "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
        "C:/Windows/Fonts/simsun.ttc",  # 宋体
        "C:/Windows/Fonts/simhei.ttf",  # 黑体
        "C:/Windows/Fonts/msyh.ttf",  # 微软雅黑另一种格式
    ]

    # 首先检查系统中文字体
    for path in possible_paths:
        if os.path.exists(path):
            font_path = path
            break

# 如果没有找到系统中文字体，则检查项目目录中的字体文件
if not font_path:
    project_font_dir = Path(__file__).parent / "fonts"
    project_fonts = [
        project_font_dir / "Roboto-Regular.ttf",
        project_font_dir / "Inter-Regular.ttf",
        project_font_dir / "SanFrancisco-Regular.ttf"
    ]
    
    for font_file in project_fonts:
        if font_file.exists():
            font_path = str(font_file)
            break

# 如果找到字体文件，则注册
if font_path:
    print(f"使用字体文件: {font_path}")
    LabelBase.register(name='ChineseFont', fn_regular=font_path)
    # 添加备用字体注册
    LabelBase.register(name='FallbackFont', fn_regular='C:/Windows/Fonts/msyh.ttc')
    font_available = True
    font_name = 'ChineseFont'
else:
    # 如果没有找到字体文件，使用默认字体（可能无法正常显示中文）
    print("警告：未找到系统中文字体，中文可能无法正常显示")
    font_available = False
    font_name = 'Roboto'

# 仅在非Android平台上注册Microsoft YaHei字体文件
if platform != 'android':
    LabelBase.register(name='Microsoft YaHei', fn_regular='C:/Windows/Fonts/msyh.ttc')

# 为Windows平台添加额外的IME支持配置
if platform == 'win':
    from kivy.config import Config
    Config.set('kivy', 'keyboard_mode', 'system')
    Config.write()

# 1. 全局常量  iOS 清新配色 (Apple 2025官方配色)
# 主色（Brand Accent）
IOS_MINT = get_color_from_hex("#7EDAB8")      # 薄荷绿 - 主按钮 / 选中态 / 强调图标
IOS_CORAL = get_color_from_hex("#FF6B6B")     # 珊瑚橙 - 警示、删除、热量超标提示
IOS_ORANGE = get_color_from_hex("#FFA500")    # 橙色 - 保存反馈按钮

# 中性色（Neutrals）
IOS_BG = get_color_from_hex("#F2F7F7")        # 背景白 - 页面底色
IOS_CARD = get_color_from_hex("#FFFFFF")      # 二级背景 - 卡片、输入框
IOS_DIVIDER = get_color_from_hex("#E5E5EA")   # 分割线 - 边框、线
IOS_TEXT_MAIN = get_color_from_hex("#000000") # 主文案 - 大标题
IOS_TEXT_SEC = get_color_from_hex("#8E8E93")  # 副文案 - 描述文字

# 语义色（System Status）
IOS_SUCCESS = get_color_from_hex("#34C759")   # 成功绿 - 完成、达标
IOS_WARNING = get_color_from_hex("#FFCC00")   # 警告黄 - 提醒
IOS_ERROR = get_color_from_hex("#FF3B30")     # 错误红 - 输入错误

# 2. 让 Windows/Mac 调试时也圆角 + 毛玻璃
Window.clearcolor = (*IOS_BG,)  # IOS_BG 已经是正确的 RGBA 格式
if platform != "android":
    Window.size = (390, 844)  # iPhone 14 Pro 逻辑像素


class IosStyleApp(App):
    # 添加属性用于在KV中判断字体是否可用
    font_available = font_available
    font_name = font_name

    def build(self):
        # 强制初始化窗口尺寸，避免弹窗位置计算错误
        Window.size = (390, 844)
        
        # 导入在这里以避免循环导入
        from kivy.lang import Builder
        from kivy.uix.screenmanager import ScreenManager
        
        # 导入屏幕类
        from modules.plan_diet.plan_screen import DietPlanScreen
        from modules.weight_plan.weight_screen import WeightScreen
        from modules.today_plan.today_plan_screen import TodayPlanScreen
        from modules.body_data.body_data_screen import BodyDataScreen  # 新增身体数据屏幕
        from modules.report.report_screen import ReportScreen  # 添加报告屏幕
        from modules.recipes.recipes_screen import RecipeScreen
        
        # 加载KV样式文件
        Builder.load_file('kv_styles.kv')
        
        # 创建 ScreenManager 并添加屏幕
        sm = ScreenManager()
        # 导入首页屏幕
        from modules.home.home_screen import HomeScreen
        # 也可以选择使用优化版首页
        # from screens.optimized_home import OptimizedHomeScreen
        sm.add_widget(HomeScreen(name='home'))
        # sm.add_widget(OptimizedHomeScreen(name='optimized_home'))
        sm.add_widget(DietPlanScreen(name='plan'))
        sm.add_widget(RecipeScreen(name='recipes'))
        sm.add_widget(BodyDataScreen(name='profile'))  # 使用body_data_screen作为profile屏幕
        sm.add_widget(TodayPlanScreen(name='water'))
        sm.add_widget(WeightScreen(name='weight'))
        # 移除重复添加的BodyDataScreen
        # sm.add_widget(BodyDataScreen(name='body_data'))  # 新增身体数据屏幕
        sm.add_widget(ReportScreen(name='report'))  # 添加报告屏幕
        
        # 设置默认过渡效果
        from kivy.uix.screenmanager import SlideTransition
        from kivy.animation import AnimationTransition
        sm.transition = SlideTransition(duration=0.4, direction='left')
        sm.transition.anim_kwargs = {'transition': AnimationTransition.out_cubic}
        sm.bind(current=self.on_screen_change)
        return sm

    def on_screen_change(self, instance, value):
        """当屏幕切换时更新tab按钮状态"""
        # 遍历所有屏幕更新tab按钮状态
        for screen in instance.screens:
            for child in screen.children:
                if isinstance(child, BoxLayout):  # 找到底部tab容器
                    for i, tab_button in enumerate(reversed(child.children)):
                        if hasattr(tab_button, 'active'):
                            # 根据当前屏幕设置active状态
                            if screen.name == 'home' and i == 3:  # 首页tab
                                tab_button.active = (value == 'home')
                            elif screen.name == 'plan' and i == 2:  # 计划tab
                                tab_button.active = (value == 'plan')
                            elif screen.name == 'recipes' and i == 1:  # 食谱tab
                                tab_button.active = (value == 'recipes')
                            elif screen.name == 'profile' and i == 0:  # 我的tab
                                tab_button.active = (value == 'profile')
                            else:
                                tab_button.active = False
    
    def update_tab_buttons(self, pressed_button):
        """更新tab按钮状态"""
        # 遍历所有屏幕更新tab按钮状态
        for screen in self.root.screens:
            for child in screen.children:
                if isinstance(child, BoxLayout):  # 找到底部tab容器
                    for tab_button in reversed(child.children):
                        if hasattr(tab_button, 'active'):
                            tab_button.active = (tab_button == pressed_button)

    def on_button_press(self):
        pass

    def on_button_release(self):
        pass

    def navigate_to_screen(self, screen_name, direction='left'):
        """带方向控制的屏幕切换"""
        from kivy.uix.screenmanager import SlideTransition
        from kivy.animation import AnimationTransition
        
        # 设置过渡效果和方向
        transition = SlideTransition(duration=0.4, direction=direction)
        transition.anim_kwargs = {'transition': AnimationTransition.out_cubic}
        
        # 应用过渡效果并切换屏幕
        self.root.transition = transition
        self.root.current = screen_name

if __name__ == '__main__':
    IosStyleApp().run()