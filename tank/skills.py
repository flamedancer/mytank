#encoding=utf-8
"""技能"""
from math import sin, cos, pi
import random

import pygame
from pygame.locals import *

from start import *
from libs import *
from tools import *
import tanks
from collision import *


class Skill(pygame.sprite.Sprite):
    def __init__(self, owner):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.owner = owner

    def wounded(self, wound):
        self.heath = self.heath - wound
        if self.heath <= 0:
            self.killself()


class Snipe(Skill):
    image = None
    gap = 200
    move_speed = 3
    image = None

    def __init__(self, owner):
        Skill.__init__(self, owner)
        self.name = self.owner.name + "Snipe"
        self.image = load_image("Snipe.gif")
        # center = (self.owner.rect.center[0] + self.gap * self.owner.direct[0],
        #            self.owner.rect.center[1] + self.gap * self.owner.direct[1])
        center = (SCREENRECT.width // 2, int(SCREENRECT.height // 2))
        self.rect = self.image.get_rect(center=center)
        self.owner.movable = False
        self.owner.skilling = True
        self.owner.shootable = False

        self.delay_time = SCREEN_PER_SEC * 5
        self.thiscontroltime = self.delay_time

    def shot(self):
        for item in self.owner.game_items:
            if not isinstance(item, tanks.Mytank) and item.rect.collidepoint(self.rect.center):
                # item.died()
                if item is not self:
                    item.wounded(200)

    def killself(self):
        self.owner.movable = True
        self.owner.skilling = False
        self.owner.shootable = True
        self.kill()

    def update(self, keystate):
        direction = None
        if not self.thiscontroltime:
            if keystate[K_j]:
                self.shot()
                self.thiscontroltime = self.delay_time
                self.killself()

        elif self.thiscontroltime > 0:
            self.thiscontroltime = self.thiscontroltime - 1
        if keystate[K_w]:
            direction = (0, -1)
        elif keystate[K_d]:
            direction = (1, 0)
        elif keystate[K_s]:
            direction = (0, 1)
        elif keystate[K_a]:
            direction = (-1, 0)
        if direction:
            self.rect.move_ip(direction[0] * self.move_speed,
                                     direction[1] * self.move_speed)


class Fireshield(Skill):
    gap = 25
    move_speed = 12   # 旋转角度速度
    rotation = -240        # 初始角度
    image = None
    heath = 20

    def __init__(self, owner):
        Skill.__init__(self, owner)
        self.name = self.owner.name + ":skill_fireshield"
        self.image = load_image("fire.gif")
        center = (self.owner.rect.center[0] + self.gap * self.owner.direct[0],
                    self.owner.rect.center[1] + self.gap * self.owner.direct[1])
        self.rect = self.image.get_rect(center=center)

    def update(self, keystate):
        collision(self, self.owner.game_items, self.rect)
        if self.rotation >= 360:
            self.rotation = 0
        self.rotation = self.rotation + self.move_speed
        x = self.gap * sin(self.rotation * pi / 180)
        y = self.gap * cos(self.rotation * pi / 180)
        self.rect.center = (self.owner.rect.center[0] + x, self.owner.rect.center[1] + y)

    def killself(self):
        self.kill()

    def wounded(self, wound):
        self.heath = self.heath - wound
        if self.heath <= 0:
            self.killself()


class IcePicr(Skill):
    # boos女神技能 冰锥
    images = None
    speed = 80

    def __init__(self, owner, topleft):
        Skill.__init__(self, owner)
        self.name = self.owner.name + ":icePicr"
        self.images = loadimage_to_slices("icePicr.gif", 9)
        self.image = self.images[0]
        self.imageindex = 0
        self.rect = self.image.get_rect(topleft=topleft)
        self.rect = change_rect(self.rect, 0.4)

        self.keeptime = 15  # 控制每幅图的静止帧数
        self.nowkeeptime = self.keeptime

    def update(self, keystate):
        if self.nowkeeptime == 0:
            self.nowkeeptime = self.keeptime
            if self.imageindex < len(self.images) - 1:
                if self.imageindex >= 2 and self.imageindex <= 6:
                    self.rect.move_ip((0, self.speed))
                    collision(self, self.owner.game_items, rect=self.rect)
                self.imageindex = self.imageindex + 1
                self.image = self.images[self.imageindex]

            else:
                self.killself()
        else:
            self.nowkeeptime = self.nowkeeptime - 1

    def killself(self):
        self.kill()

    def wounded(self, wound):
        pass


class Meteor(Skill):
    # boos女神技能 暗黑流星
    images = None
    speed = 5

    def __init__(self, owner, topleft, targetpoint):
        Skill.__init__(self, owner)
        self.name = self.owner.name + ":meteor"
        self.images = loadimage_to_slices("meteor.gif", 11)
        self.image = self.images[0]
        self.imageindex = 0
        self.rect = self.image.get_rect(topleft=topleft)
        self.rect = change_rect(self.rect, 0.6)
        targetvector = pygame.math.Vector2(targetpoint)
        selfvector = pygame.math.Vector2(self.rect.center)

        self.movevector = (targetvector - selfvector).normalize() * self.speed    # 运行方向单位向量 * 行动速度

        self.keeptime = 15  # 控制每幅图的静止帧数
        self.nowkeeptime = self.keeptime

    def update(self, keystate):
        if self.imageindex >= 3:
            self.rect.move_ip(self.movevector.x, self.movevector.y)
            collision(self, self.owner.game_items, rect=self.rect)
        if self.nowkeeptime == 0:
            self.nowkeeptime = self.keeptime
            if self.imageindex < len(self.images) - 1:
                self.imageindex = self.imageindex + 1
                self.image = self.images[self.imageindex]

            else:
                self.killself()
        else:
            self.nowkeeptime = self.nowkeeptime - 1

    def killself(self):
        self.kill()

    def wounded(self, wound):
        pass


class Rattan(Skill):
    # 女神技能春藤
    images = None

    def __init__(self, owner, topleft):
        Skill.__init__(self, owner)
        self.name = self.owner.name + ":rattan"
        self.images = loadimage_to_slices("rattan.gif", 4)
        self.image = self.images[0]
        self.imageindex = 0
        self.rect = self.image.get_rect(topleft=topleft)

        self.keeptime = [10, 30, 10, 30]
        self.nowkeeptime = self.keeptime[self.imageindex]
        self.grow = True

    def update(self, keystate):
        if self.nowkeeptime == 0:
            if self.imageindex <= len(self.images) - 1:
                if self.grow:
                    self.imageindex = self.imageindex + 1
                    if self.imageindex == len(self.images) - 1:
                        self.grow = False
                        collision(self, self.owner.game_items, rect=self.rect)
                else:
                    if self.imageindex == 0:
                        self.killself()
                        return
                    self.imageindex = self.imageindex - 1
                self.image = self.images[self.imageindex]

                self.nowkeeptime = self.keeptime[self.imageindex]
        else:
            self.nowkeeptime = self.nowkeeptime - 1

    def killself(self):
        self.kill()

    def wounded(self, wound):
        pass


class Flower(Skill):
    # 花仙技能
    images = None
    heath = 10

    def __init__(self, owner, topleft, direct):
        Skill.__init__(self, owner)
        self.name = self.owner.name + ":flower"
        self.images = load_images("redflower.gif", "yellowflower.gif")

        # 出现黄花的概率
        yellowrate = 0.3
        roll = random.random()
        if roll > yellowrate:    # color == "red"
            self.image = self.images[0]
            self.speed = 4
        else:
            self.image = self.images[1]
            self.speed = 3
        self.direct = direct   # direct 为向量

        self.rect = self.image.get_rect(topleft=topleft)

    def killself(self):
        self.kill()

    def update(self, keystate):
        collision(self, self.owner.game_items, rect=self.rect)
        self.rect.move_ip((self.speed * self.direct.x, self.speed * self.direct.y))
        if not SCREENRECT.colliderect(self.rect):
            self.killself()
