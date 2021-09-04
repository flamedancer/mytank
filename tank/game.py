#encoding=utf-8
"""游戏主循环"""
import sys
import pygame
from pygame.locals import *

from stage import *


class Game:
    def __init__(self, screen, stage_num=1):
        self.clock = pygame.time.Clock()
        self.screen = screen
        self.screen = screen
        self.gamestart()

        self.control_delay_time = SCREEN_PER_SEC        # 控制键盘灵敏度 否则压下一次程序将判断为多次
        self.controltime = self.control_delay_time

        self.stage_num = stage_num

    def gamestart(self):
        start_picture = load_image('start_pic.gif')
        boundary_line_picture = load_image('back_line.gif')

        score_background = pygame.Surface((SCREEN_WIDTH, SCORE_HEIGHT))
        score_background = score_background.convert()

        score_background.fill((255, 255, 255))

        self.screen.blit(start_picture, (0, 0))
        self.screen.blit(boundary_line_picture, (0, SCREEN_HEIGHT))
        self.screen.blit(score_background, (0, SCREEN_HEIGHT + BOUNDARY_LINE_HEIGHT))

        self.gamebegin = False
        self.gamepause = False
        self.gameover = False

    def begingame(self):
        self.stage = eval("Stage{0}(self.screen)".format(self.stage_num))
        self.gamebegin = True

    def pausegame(self):
        self.gamepause = not self.gamepause

    def nextstage(self):
        self.stage_num = self.stage_num + 1
        self.stage = eval("Stage{0}(self.screen)".format(self.stage_num))
        #self.stage = Stage2(self.screen)

    def restartstage(self):
        self.stage = eval("Stage{0}(self.screen)".format(self.stage_num))

    def controlgame(self, keystate):
        if self.controltime == self.control_delay_time:
            if keystate[K_RETURN]:
                if not self.gamebegin:
                    self.begingame()
                else:
                    self.pausegame()
                self.controltime = self.controltime - 1
        elif self.controltime > 0:
            self.controltime = self.controltime - 1
        elif self.controltime == 0:
            self.controltime = self.control_delay_time

    def fail(self):
        self.gameover = True
        self.restartstage()

    def run(self):

        while True:
            self.clock.tick(SCREEN_PER_SEC)
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
            keystate = pygame.key.get_pressed()
            self.controlgame(keystate)
            if self.gamebegin and not self.gamepause:
                result = self.stage.process(keystate=keystate)
                if result == "win":
                    self.nextstage()
                elif result == "fail":
                    self.fail()

            pygame.display.update()

