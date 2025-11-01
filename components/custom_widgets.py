# -*- coding: utf-8 -*-
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Line
from kivy.properties import BooleanProperty, ListProperty, StringProperty, ObjectProperty
from kivy.uix.button import ButtonBehavior
from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock


class BaseButton(ButtonBehavior, BoxLayout):
    """
    基础按钮类，所有按钮组件的基类
    统一实现按钮的样式、颜色和交互逻辑
    """

    def __init__(self, text='', **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_press')
        self.register_event_type('on_release')

        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = '48dp'
        self.padding = ['12dp', '8dp']

        # 创建标签
        self.label = Label(
            text=text,
            font_size='15sp',
            color=get_color_from_hex('#000000'),
            size_hint=(1, 1),
        )
        self.label.bind(pos=self._update_font, size=self._update_font)
        self.add_widget(self.label)

        # 绑定事件
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        self.bind(state=self._on_state_change)

        # 初始化图形
        self.update_graphics()

    def on_press(self):
        """处理按钮按下事件"""
        pass

    def on_release(self):
        """处理按钮释放事件"""
        pass

    def _update_font(self, *args):
        # 尝试获取app并设置字体
        try:
            app = App.get_running_app()
            if app and hasattr(app, 'font_available'):
                self.label.font_name = 'ChineseFont' if app.font_available else 'Microsoft YaHei'
            else:
                self.label.font_name = 'Microsoft YaHei'
        except:
            # 当Microsoft YaHei也不可用时，使用系统默认字体
            self.label.font_name = 'Microsoft YaHei'

    def update_graphics(self, *args):
        """统一的颜色管理方法"""
        self.canvas.before.clear()
        with self.canvas.before:
            # 根据按钮状态设置颜色，使用统一的清新绿色样式
            if self.state == 'down':
                Color(rgba=(1, 0.42, 0.4, 0.5))  # 按下时的珊瑚橙色
            else:
                # 检查按钮类型并根据需要设置颜色
                if isinstance(self, GenderButton):
                    if self.gender == 'male' and self.selected:
                        Color(rgba=(0.2, 0.6, 1, 1))  # 选中的男性按钮 - 蓝色
                    elif self.gender == 'female' and self.selected:
                        Color(rgba=(1, 0.6, 0.8, 1))  # 选中的女性按钮 - 粉色
                    elif self.gender == 'male':
                        Color(rgba=(0.2, 0.6, 1, 0.3))  # 未选中的男性按钮 - 浅蓝色
                    elif self.gender == 'female':
                        Color(rgba=(1, 0.6, 0.8, 0.3))  # 未选中的女性按钮 - 浅粉色
                    else:
                        Color(rgba=(0.498, 0.855, 0.722, 0.3))  # 默认颜色
                elif isinstance(self, GoalButton):
                    if self.selected:
                        Color(rgba=(0.2, 0.6, 1, 1))  # 选中时使用蓝色
                    else:
                        Color(rgba=(0.498, 0.855, 0.722, 0.3))  # 未选中时使用统一的清新绿色
                elif isinstance(self, FlatButton):
                    # 检查是否是保存成功状态
                    if getattr(self, 'save_success', False):
                        Color(rgba=(1, 0.42, 0.4, 1))  # 保存成功时显示橙色
                    else:
                        Color(rgba=(0.498, 0.855, 0.722, 0.3))  # 扁平按钮使用统一的清新绿色
                elif isinstance(self, TabButton):
                    Color(rgba=(0.498, 0.855, 0.722, 0.3))  # 标签按钮使用统一的清新绿色
                elif isinstance(self, SelectableLabel):
                    Color(rgba=(0.498, 0.855, 0.722, 0.3 if not self.selected else 0.8))  # 可选择标签根据选中状态调整透明度
                else:
                    Color(rgba=(0.498, 0.855, 0.722, 0.3))  # 默认使用统一的清新绿色 #7EDAB8
            from kivy.graphics.vertex_instructions import RoundedRectangle
            RoundedRectangle(pos=self.pos, size=self.size, radius=[12])

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # 触发按下事件
            self.dispatch('on_press')
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            # 触发释放事件
            self.dispatch('on_release')
            return True
        return super().on_touch_up(touch)

    def _on_state_change(self, widget, value):
        """当按钮状态改变时更新图形"""
        self.update_graphics()

    @property
    def text(self):
        return self.label.text if self.label else ""

    @text.setter
    def text(self, value):
        if self.label:
            self.label.text = value


class FlatButton(BaseButton):
    """标准扁平按钮"""
    # 按钮类型属性，用于区分不同类型的按钮
    button_type = StringProperty('')
    
    # 添加保存成功状态属性
    save_success = BooleanProperty(False)

    def __init__(self, text='', **kwargs):
        super().__init__(text=text, **kwargs)
        # 确保FlatButton没有selected属性相关的绑定


class SelectableLabel(BaseButton):
    """可选择标签按钮"""
    selected = BooleanProperty(False)

    def __init__(self, text='', **kwargs):
        super().__init__(text=text, **kwargs)

    def on_press(self):
        """处理按钮按下事件"""
        self.selected = not self.selected


class TabButton(BaseButton):
    """标签按钮"""
    active = BooleanProperty(False)

    def __init__(self, text='', **kwargs):
        super().__init__(text=text, **kwargs)

    def on_press(self):
        """处理按钮按下事件"""
        self.active = not self.active


class GenderButton(BaseButton):
    """性别按钮"""
    selected = BooleanProperty(False)
    gender = StringProperty('')  # 'male' 或 'female'

    def __init__(self, text='', **kwargs):
        super().__init__(text=text, **kwargs)
        self.bind(selected=self._on_selected_change)

    def _on_selected_change(self, instance, value):
        """当selected属性改变时更新图形"""
        self.update_graphics()

    def on_press(self):
        """处理按钮按下事件"""
        # 通知父组件处理选择逻辑
        parent = self.parent
        while parent:
            if hasattr(parent, 'select_gender'):
                parent.select_gender(self.gender)
                break
            parent = parent.parent


class GoalButton(BaseButton):
    """目标按钮"""
    selected = BooleanProperty(False)

    def __init__(self, text='', **kwargs):
        super().__init__(text=text, **kwargs)
        self.bind(selected=self._on_selected_change)

    def _on_selected_change(self, instance, value):
        """当selected属性改变时更新图形"""
        self.update_graphics()

    def on_press(self):
        """处理按钮按下事件"""
        # 通知父组件处理选择逻辑
        parent = self.parent
        while parent:
            if hasattr(parent, 'select_goal'):
                parent.select_goal(self.text)
                break
            parent = parent.parent


class Card(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = ('24dp', '20dp')
        self.spacing = '12dp'
        self.size_hint_y = None
        self.height = self.minimum_height
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        self.update_graphics()

    def update_graphics(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # 白色卡片背景
            Color(rgba=(1, 1, 1, 0.85))
            from kivy.graphics.vertex_instructions import RoundedRectangle
            RoundedRectangle(pos=self.pos, size=self.size, radius=[24])
            # 简单毛玻璃：白底 + 半透明遮罩
            Color(rgba=(1, 1, 1, 0.5))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[24])


class InputCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = ('24dp', '20dp')
        self.spacing = '16dp'
        self.size_hint_y = None
        self.height = self.minimum_height
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        self.update_graphics()

    def update_graphics(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(rgba=(1, 1, 1, 0.85))
            from kivy.graphics.vertex_instructions import RoundedRectangle
            RoundedRectangle(pos=self.pos, size=self.size, radius=[24])


class StyledTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 设置输入框的基本属性
        self.background_color = [0, 0, 0, 0]  # 完全透明背景
        self.foreground_color = get_color_from_hex('#000000')  # 黑色文字
        self.cursor_color = get_color_from_hex('#7EDAB8')  # 薄荷绿光标
        self.padding = [12, 12, 12, 12]  # 内边距
        self.size_hint_y = None
        self.height = 48  # 固定高度
        self.multiline = False

        # 设置字体以支持中文显示
        app = App.get_running_app()
        if app and hasattr(app, 'font_available') and app.font_available:
            self.font_name = 'ChineseFont'
        else:
            self.font_name = 'Microsoft YaHei'

        # 添加 IME 支持
        self.keyboard_suggestions = True
        self.input_type = 'text'

        # 不再绑定事件，避免干扰TextInput的正常功能

    def update_graphics(self, *args):
        """更新输入框的自定义图形"""
        # 使用canvas.after确保不影响TextInput的核心功能
        self.canvas.after.clear()
        with self.canvas.after:
            # 背景
            Color(rgba=(0.97, 0.97, 0.97, 1))  # 浅灰色背景
            from kivy.graphics.vertex_instructions import RoundedRectangle
            RoundedRectangle(pos=self.pos, size=self.size, radius=[12])

            # 边框
            Color(rgba=(0.498, 0.855, 0.722, 0.5))
            Line(rounded_rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1], 12), width=1.2)

    def insert_text(self, substring, from_undo=False):
        """重写插入文本方法确保正常输入"""
        # 对于中文输入，我们不需要特殊过滤，让系统处理IME
        return super().insert_text(substring, from_undo)
