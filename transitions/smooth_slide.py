# -*- coding: utf-8 -*-
from kivy.uix.screenmanager import TransitionBase
from kivy.animation import Animation
from kivy.graphics import PushMatrix, PopMatrix, Translate, Color, Rectangle


class SmoothSlideTransition(TransitionBase):
    """平滑滑动过渡效果"""

    def start(self, manager):
        super().start(manager)
        new_screen = self.screen_in if self.is_push else self.screen_out
        manager.canvas.add(PushMatrix())
        manager.canvas.add(Translate())
        manager.canvas.add(PopMatrix())
        self.animation = Animation(
            d=self.duration,
            t=self.transition,
            x=0 if self.is_push else -manager.width
        )
        self.animation.start(manager.canvas.children[-2])
        self.animation.bind(on_complete=self.complete)

    def on_complete(self, *args):
        self.screen_in.pos = (0, 0)
        self.screen_out.pos = (0, 0)
        self.manager.canvas.remove_group(self)
        super().on_complete()