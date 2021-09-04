#encoding=utf-8
"""初始化窗口"""
import pygame
from pygame.locals import *

#import pygame._view
import game
import sys
from tools import *

SCREEN_PER_SEC = 40
SCREEN_WIDTH = 384
SCREEN_HEIGHT = 608
SCORE_HEIGHT = 100
BOUNDARY_LINE_HEIGHT = 10
SCREENRECT = Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)


def start(stage_num=1):
    #界面大小   分数面板
    # Initialise screen
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH,
                    SCREEN_HEIGHT + SCORE_HEIGHT + BOUNDARY_LINE_HEIGHT))
    pygame.display.set_caption('MY TANK  guochen')
    # Fill background

    pygame.display.flip()
    game.Game(screen, stage_num=stage_num).run()

if __name__ == "__main__":
    stage_num = 1
    if len(sys.argv) > 1:
        stage_num = int(sys.argv[1])
    start(stage_num=stage_num)
