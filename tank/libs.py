#encoding=utf-8
"""一些处理工具"""
#import pygame
from start import *
from pygame.locals import *


class State(object):

    def __init__(self, name):
        self.name = name

    def do_actions(self):
        pass

    def check_conditions(self):
        pass

    def entry_actions(self):
        pass

    def exit_actions(self):
        pass


class StateMachine(object):
    def __init__(self):
        self.states = {}
        self.active_state = None

    def add_state(self, state):
        self.states[state.name] = state

    def think(self):
        if self.active_state is None:
            return
        self.active_state.do_actions()
        new_state_name = self.active_state.check_conditions()
        if new_state_name is not None:
            self.set_state(new_state_name)

    def set_state(self, new_state_name):
        if self.active_state is not None:
            self.active_state.exit_actions()
        self.active_state = self.states[new_state_name]
        self.active_state.entry_actions()


def time_to_frams(second):
    # 将秒数 换算成帧数
    if type(second) in [type(1), type(0.1)]:
        return second * SCREEN_PER_SEC
    else:
        return [item * SCREEN_PER_SEC for item in second]


def change_rect(rect, rate):
    # rect 中点不变 按比例放缩 返回放缩后的rect
    width, height = rect.width * rate, rect.height * rate
    left = rect.left + (rect.width - width) / 2
    top = rect.top + (rect.height - height) / 2
    return Rect(left, top, width, height)

