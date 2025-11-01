# -*- coding: utf-8 -*-
"""
自定义过渡效果，支持根据导航方向设置不同的滑动效果
"""
from kivy.uix.screenmanager import SlideTransition
from kivy.animation import AnimationTransition


class DirectionalSlideTransition(SlideTransition):
    """支持方向控制的滑动过渡效果"""
    
    def __init__(self, direction='left', duration=0.4, **kwargs):
        super().__init__(duration=duration, **kwargs)
        self.direction = direction
        self.anim_kwargs = {'transition': AnimationTransition.out_cubic}
    
    def start(self, manager):
        # 保存当前屏幕和目标屏幕的原始位置
        if self.screen_out and hasattr(self.screen_out, '_original_pos'):
            self.screen_out.pos = self.screen_out._original_pos
        if self.screen_in and hasattr(self.screen_in, '_original_pos'):
            self.screen_in.pos = self.screen_in._original_pos
            
        super().start(manager)